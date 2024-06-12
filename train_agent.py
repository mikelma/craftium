import numpy as np
import matplotlib.pyplot as plt
from stable_baselines3 import PPO
from gymnasium import ActionWrapper, Env
from gymnasium.spaces import MultiDiscrete

from craftium import CraftiumEnv


class DiscreteActionWrapper(ActionWrapper):
    def __init__(self, env: Env):
        ActionWrapper.__init__(self, env)

        # actions:
        #  forward, backward, left, right, jump, dig,
        #  mouse -x, mouse +x, mouse -y, mouse +y
        self.action_space = MultiDiscrete(np.full(10, 2))
        self.mouse_mov = 0.8

    def action(self, action):
        r = self.mouse_mov

        mouse = [0, 0]

        if action[6] == 1:
            mouse[0] += r
        if action[7] == 1:
            mouse[0] += -r
        if action[8] == 1:
            mouse[1] += r
        if action[9] == 1:
            mouse[1] += -r

        return {
            "forward": action[0],
            "backward": action[1],
            "left": action[2],
            "right": action[3],
            "jump": action[4],
            "dig": action[5],
            "mouse": mouse,
        }


if __name__ == "__main__":
    env = CraftiumEnv(
        env_dir="craftium-envs/chop-tree",
        max_timesteps=200,
        obs_width=64,
        obs_height=64,
        render_mode="human",
    )

    env = DiscreteActionWrapper(env)

    model = PPO("CnnPolicy", env, verbose=1)
    model.learn(total_timesteps=10_000)

    model.save("ppo_chop-tree")
    env.close()
