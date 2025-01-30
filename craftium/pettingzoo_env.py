from pettingzoo import AECEnv
from pettingzoo.utils import agent_selector, wrappers
from typing import Optional
import os
import functools
from . import root_path
from .multiagent_env import MarlCraftiumEnv

AVAIL_ENVS = {
    "Craftium/MultiAgentCombat-v0": dict(
        env_dir="craftium-envs/multi-agent-combat",
        conf=dict(
            num_agents=2,
            obs_width=64,
            obs_height=64,
            max_timesteps=1000,
            rgb_observations=True,
            init_frames=200,
            sync_mode=False,
        ),
    ),
}


def env(env_name: str, render_mode: Optional[str] = None, **kwargs):
    """
    Returns the PettingZoo version (`AECEnv`) of multi-agent Craftium environments.

    :param env_name: Name of the environment to load.
    :param render_mode: Rendering mode (`"rgb_array"` or `"human"`).
    :param **kwargs: Additional keyword arguments to pass to the created Craftium environment (see `MarlCraftiumEnv`).
    """
    env_dir = os.path.join(root_path, AVAIL_ENVS[env_name]["env_dir"])
    final_args = kwargs | AVAIL_ENVS[env_name]["conf"]

    return raw_env(
        env_dir,
        render_mode,
        **final_args
    )


class raw_env(AECEnv):
    metadata = {"render_modes": ["human", "rgb_array"], "name": "craftium_env"}

    def __init__(self, env_dir: str, render_mode: Optional[str] = None, **kwargs):
        self.na = kwargs["num_agents"]
        self.possible_agents = ["player_" + str(r) for r in range(self.na)]

        # mapping between agent ID and name
        self.agent_id_map = dict(
            zip(self.possible_agents, list(range(len(self.possible_agents))))
        )

        self.env = MarlCraftiumEnv(
            env_dir=env_dir,
            **kwargs
        )

    @functools.lru_cache(maxsize=None)
    def observation_space(self, agent):
        return self.env.observation_space[0]

    @functools.lru_cache(maxsize=None)
    def action_space(self, agent):
        return self.env.action_space

    def render(self):
        pass

    def observe(self, agent):
        return self.observations[agent]

    def close(self):
        self.env.close()

    def reset(self, seed=None, options=None):
        observations, infos = self.env.reset()

        self.agents = self.possible_agents[:]
        self.rewards = {agent: 0 for agent in self.agents}
        self._cumulative_rewards = {agent: 0 for agent in self.agents}
        self.terminations = {agent: False for agent in self.agents}
        self.truncations = {agent: False for agent in self.agents}
        self.infos = {agent: infos for i, agent in enumerate(self.agents)}
        # self.state = {agent: observations[i] for i, agent in enumerate(self.agents)}
        self.observations = {agent: observations[i]
                             for i, agent in enumerate(self.agents)}

        # the agent_selector utility allows easy cyclic stepping through the agents list
        self._agent_selector = agent_selector(self.agents)
        self.agent_selection = self._agent_selector.next()

    def step(self, action):
        if (
            self.terminations[self.agent_selection]
            or self.truncations[self.agent_selection]
        ):
            # handles stepping an agent which is already dead
            # accepts a None action for the one agent, and moves the agent_selection to
            # the next dead agent,  or if there are no more dead agents, to the next live agent
            self._was_dead_step(action)
            return

        agent = self.agent_selection

        agent_id = self.agent_id_map[agent]

        self.env.current_agent_id = agent_id
        observation, reward, termination, truncated, info = self.env.step_agent(
            action)

        self.observations[agent] = observation
        self.rewards[agent] = reward
        self.truncations[agent] = truncated
        self.terminations[agent] = termination

        # collect reward if it is the last agent to act
        if self._agent_selector.is_last():
            # Adds .rewards to ._cumulative_rewards
            self._accumulate_rewards()
        # selects the next agent.
        self.agent_selection = self._agent_selector.next()
