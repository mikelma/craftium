import os
from typing import Optional
import time

from .mt_client import MtClient
from .minetest import Minetest

import numpy as np

# import gymnasium as gym
from gymnasium import Env
from gymnasium.spaces import Dict, Discrete, Box


class CraftiumEnv(Env):
    """The main class implementing Gymnasium's [Env](https://gymnasium.farama.org/api/env/) API.

    :param obs_width: The width of the observation image in pixels.
    :param obs_height: The height of the observation image in pixels.
    :param init_frames: The number of frames to wait for Minetest to load.
    :param render_mode: Render mode ("human" or "rgb_array"), see [Env.render](https://gymnasium.farama.org/api/env/#gymnasium.Env.render).
    :param max_timesteps: Maximum number of timesteps until episode termination. Disabled if set to `None`.
    :param run_dir: Path to save the artifacts created by the run. Will be automatically generated if not provided.
    """
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 30}

    def __init__(
            self,
            obs_width: int = 640,
            obs_height: int = 360,
            init_frames: int = 15,
            render_mode: Optional[str] = None,
            max_timesteps: Optional[int] = None,
            run_dir: Optional[os.PathLike] = None,
    ):
        super(CraftiumEnv, self).__init__()

        self.obs_width = obs_width
        self.obs_height = obs_height
        self.init_frames = init_frames
        self.max_timesteps = max_timesteps

        self.action_space = Dict({
            "forward": Discrete(2),
            "backward": Discrete(2),
            "left": Discrete(2),
            "right": Discrete(2),
            "jump": Discrete(2),
            "aux1": Discrete(2),
            "sneak": Discrete(2),
            "zoom": Discrete(2),
            "dig": Discrete(2),
            "place": Discrete(2),
            "drop": Discrete(2),
            "inventory": Discrete(2),
            "slot_1": Discrete(2),
            "slot_2": Discrete(2),
            "slot_3": Discrete(2),
            "slot_4": Discrete(2),
            "slot_5": Discrete(2),
            "slot_6": Discrete(2),
            "slot_7": Discrete(2),
            "slot_8": Discrete(2),
            "slot_9": Discrete(2),
            "mouse": Box(low=-1, high=1, shape=(2,), dtype=np.float32),
        })

        # names of the actions in the order they must be sent to MT
        self.action_order = [
            "forward", "backward", "left", "right", "jump", "aux1", "sneak",
            "zoom", "dig", "place", "drop", "inventory", "slot_1", "slot_2",
            "slot_3", "slot_4", "slot_5", "slot_6", "slot_7", "slot_8", "slot_9",
        ]

        self.observation_space = Box(low=0, high=255, shape=(obs_width, obs_height, 3))

        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode

        # handles the MT configuration and process
        self.mt = Minetest(
            run_dir=run_dir,
            headless=render_mode != "human",
        )

        # variable initialized in the `reset` method
        self.client = None  # client that connects to minetest

        self.last_observation = None  # used in render if "rgb_array"
        self.timesteps = 0  # the timesteps counter

    def _get_info(self):
        return dict()

    def reset(
        self,
        *,
        seed: Optional[int] = None,
        options: Optional[dict] = None,
    ):
        """Resets the environment to an initial internal state, returning an initial observation and info.

        See [Env.reset](https://gymnasium.farama.org/api/env/#gymnasium.Env.reset) in the Gymnasium docs.

        :param seed: The random seed.
        :param options: Options dictionary.
        """
        super().reset(seed=seed)
        self.timesteps = 0

        # kill the active mt process and the python client if any
        if self.client is not None:
            self.client.close()
            self.mt.kill_process()

        # start the new MT process
        self.mt.start_process()  # launch the new MT process
        time.sleep(2)  # wait for MT to initialize (TODO Improve this)

        # connect the client to the MT process
        self.client = MtClient(
            img_width=self.obs_width,
            img_height=self.obs_height,
        )

        # HACK skip some frames to let the game initialize
        for _ in range(self.init_frames):
            _observation, _reward, _term = self.client.receive()
            self.client.send([0]*21, 0, 0)  # nop action

        observation, _reward, _term = self.client.receive()
        self.last_observation = observation

        info = self._get_info()

        return observation, info

    def step(self, action):
        """Run one timestep of the environment’s dynamics using the agent actions.

        See [Env.step](https://gymnasium.farama.org/api/env/#gymnasium.Env.step) in the Gymnasium docs.

        :param action: An action provided by the agent.
        """
        self.timesteps += 1

        # convert the action dict to a format to be sent to MT through mt_client
        keys = [0]*21  # all commands (keys) except the mouse
        mouse_x, mouse_y = 0, 0
        for k, v in action.items():
            if k == "mouse":
                x, y = v[0], v[1]
                mouse_x = int(x*(self.obs_width // 2))
                mouse_y = int(y*(self.obs_height // 2))
            else:
                keys[self.action_order.index(k)] = v
        # send the action to MT
        self.client.send(keys, mouse_x, mouse_y)

        # receive the new info from minetest
        observation, reward, termination = self.client.receive()
        self.last_observation = observation

        info = self._get_info()

        truncated = self.max_timesteps is not None and self.timesteps >= self.max_timesteps

        return observation, reward, termination, truncated, info

    def render(self):
        if self.render_mode == "rgb_array":
            return self.last_observation

    def close(self):
        self.mt.kill_process()
        self.mt.clear()
        self.client.close()
