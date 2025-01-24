import os
import time
import signal
from typing import Optional, Any

from .craftium_env import ACTION_ORDER
from .mt_channel import MtChannel
from .minetest import MTServerOnly, MTClientOnly

from gymnasium.spaces import Dict, Discrete, Box
import numpy as np


class MarlCraftiumEnv():
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 30}

    def __init__(
            self,
            num_agents: int,
            env_dir: os.PathLike,
            obs_width: int = 640,
            obs_height: int = 360,
            init_frames: int = 200,
            render_mode: Optional[str] = None,
            max_timesteps: Optional[int] = None,
            run_dir_prefix: Optional[os.PathLike] = None,
            game_id: str = "minetest",
            world_name: str = "world",
            minetest_dir: Optional[str] = None,
            # tcp_port: Optional[int] = None,
            mt_server_conf: dict[str, Any] = dict(),
            mt_clients_conf: dict[str, Any] = dict(),
            pipe_proc: bool = True,
            mt_listen_timeout: int = 60_000,
            mt_server_port: Optional[int] = None,
            frameskip: int = 1,
            rgb_observations: bool = True,
            gray_scale_keepdim: bool = False,
            seed: Optional[int] = None,
            sync_mode: bool = False,
            fps_max: int = 200,
            pmul: Optional[int] = None,
    ):
        assert num_agents > 1, "Number of agents lower than 2. Use CraftiumEnv for single agent environments."
        self.num_agents = num_agents
        self.obs_width = obs_width
        self.obs_height = obs_height
        self.init_frames = init_frames // frameskip
        self.max_timesteps = max_timesteps
        self.gray_scale_keepdim = gray_scale_keepdim
        self.rgb_observations = rgb_observations

        # define the action space
        action_dict = {}
        for act in ACTION_ORDER[:-1]:  # all actions except the last ("mouse")
            action_dict[act] = Discrete(2)  # 1/0: key pressed/not pressed
        # define the mouse action
        action_dict[ACTION_ORDER[-1]
                    ] = Box(low=-1, high=1, shape=(2,), dtype=np.float32)
        self.action_space = Dict(action_dict)

        # define the observation space
        shape = [num_agents, obs_width, obs_height]
        if rgb_observations:
            shape.append(3)
        elif gray_scale_keepdim:
            shape.append(1)

        self.observation_space = Box(
            low=0, high=255, shape=shape, dtype=np.uint8)

        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode

        # crate a communication channel between python and MT (server) for each of the agents
        self.mt_channs = []
        for _ in range(num_agents):
            chann = MtChannel(
                img_width=self.obs_width,
                img_height=self.obs_height,
                listen_timeout=mt_listen_timeout,
                rgb_imgs=rgb_observations,
            )
            self.mt_channs.append(chann)

        # create a MT instance that will be configured as the server
        self.mt_server = MTServerOnly(
            run_dir_prefix=run_dir_prefix,
            seed=seed,
            game_id=game_id,
            world_name=world_name,
            sync_dir=env_dir,
            minetest_dir=minetest_dir,
            minetest_conf=mt_server_conf,
            pipe_proc=pipe_proc,
            mt_server_port=mt_server_port,
            sync_mode=sync_mode,
            fps_max=fps_max,
            pmul=pmul,
        )

        # create a MT (client) instance for each agent
        self.mt_clients = []
        for i in range(num_agents):
            client = MTClientOnly(
                tcp_port=self.mt_channs[i].port,
                client_name=f"agent{i}",
                mt_server_port=self.mt_server.server_port,
                run_dir_prefix=run_dir_prefix,
                headless=i == 0 and render_mode != "human",
                seed=seed,
                sync_dir=env_dir,
                screen_w=obs_width,
                screen_h=obs_height,
                minetest_dir=minetest_dir,
                minetest_conf=mt_clients_conf,
                pipe_proc=pipe_proc,
                frameskip=frameskip,
                rgb_frames=rgb_observations,
                sync_mode=sync_mode,
                fps_max=fps_max,
                pmul=pmul,
            )
            self.mt_clients.append(client)

        # used in render if "rgb_array"
        self.last_observations = [None]*num_agents
        self.timesteps = 0  # the timesteps counter
        self.current_agent_id = 0

    def _get_info(self):
        return dict()

    def reset(self, **kwargs):
        self.timesteps = 0

        observations = []

        # intialize the MT processes (server and clients)
        # NOTE: only done the first time reset is called
        if self.mt_server.proc is None:
            self.mt_server.start_process()
            # HACK wait for the server to initialize before launching the clients
            print(
                "* Waiting for MT server to initialize. This is only required in the first call to reset")
            # TODO Use a an argument of the class instead of a constant
            time.sleep(5)

            for i in range(self.num_agents):
                # start the new MT (client) process
                self.mt_clients[i].start_process()
                # re-open the connection between python and the MT client
                self.mt_channs[i].open_conn()

                # HACK skip some frames to let the game initialize
                # TODO This "waiting" should be implemented in Minetest not in python
                for _ in range(self.init_frames):
                    _observation, _reward, _term = self.mt_channs[i].receive()
                    self.mt_channs[i].send([0]*21, 0, 0)  # nop action

                # receive the new info from minetest
                observation, reward, _termination = self.mt_channs[i].receive()
                if not self.gray_scale_keepdim and not self.rgb_observations:
                    observation = observation[:, :, 0]
                observations.append(observation)
                self.last_observations[i] = observation

        else:  # soft reset
            for i in range(self.num_agents):
                # send a soft reset to the MT client
                self.mt_channs[i].send_soft_reset()
                # receive a new observation from minetest
                observation, reward, _termination = self.mt_channs[i].receive()
                if not self.gray_scale_keepdim and not self.rgb_observations:
                    observation = observation[:, :, 0]
                observations.append(observation)
                self.last_observations[i] = observation

        infos = self._get_info()

        # stack the observations of each agent
        observations = np.vstack([np.expand_dims(obs, 0)
                                 for obs in observations])

        return observations, infos

    def step_agent(self, action):
        self.timesteps += 1

        if self.current_agent_id == self.num_agents:
            self.current_agent_id = 0
        agent_id = self.current_agent_id
        self.current_agent_id += 1

        # convert the action dict to a format to be sent to MT through mt_chann
        keys = [0]*21  # all commands (keys) except the mouse
        mouse_x, mouse_y = 0, 0
        for k, v in action.items():
            if k == "mouse":
                x, y = v[0], -v[1]
                mouse_x = int(x*(self.obs_width // 2))
                mouse_y = int(y*(self.obs_height // 2))
            else:
                keys[ACTION_ORDER.index(k)] = v

        # send the action to MT
        self.mt_channs[agent_id].send(keys, mouse_x, mouse_y)

        # receive the new info from minetest
        observation, reward, termination = self.mt_channs[agent_id].receive()
        if not self.gray_scale_keepdim and not self.rgb_observations:
            observation = observation[:, :, 0]

        self.last_observations[agent_id] = observation
        info = self._get_info()

        truncated = self.max_timesteps is not None and self.timesteps >= self.max_timesteps

        return observation, reward, termination, truncated, info

    def step(self, actions):
        assert len(
            actions) == self.num_agents, f"The number of actions ({len(actions)}) must match with the number of agents ({self.num_agents})"

        observations, rewards, terminations, truncations = [], [], [], []
        infos = dict()
        for agent_id in range(self.num_agents):
            self.current_agent_id = agent_id
            obs, rwd, trm, trc, inf = self.step_agent(actions[agent_id])
            observations.append(obs)
            rewards.append(rwd)
            terminations.append(trm)
            truncations.append(trc)
            infos |= inf  # the | operator merges two dicts

        # stack the observations of each agent
        observations = np.vstack([np.expand_dims(obs, 0)
                                 for obs in observations])
        rewards = np.array(rewards)
        terminations = np.array(terminations)
        truncations = np.array(truncations)
        return observations, rewards, terminations, truncations, infos

    def render(self):
        if self.render_mode == "rgb_array":
            return self.last_observations

    def close(self, clear: bool = True):
        """
        Closes the environment and removes temporary files.

        :param clear: Whether to remove the MT working 
        directory or not.
        """
        # close all MT clients
        for i in range(self.num_agents):
            if self.mt_channs[i].is_open():
                self.mt_channs[i].send_kill()
                self.mt_channs[i].close_conn()
                self.mt_clients[i].close_pipes()
                self.mt_clients[i].wait_close()
            if clear:
                self.mt_clients[i].clear()

        # close the MT server
        self.mt_server.close_pipes()
        # send a kill signal to the server, as we've no way to send a self-termination
        # command to it like in the case of the clients
        os.killpg(os.getpgid(self.mt_server.proc.pid), signal.SIGTERM)
        if clear:
            self.mt_server.clear()
