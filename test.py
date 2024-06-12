import time

from craftium import CraftiumEnv

import numpy as np
import matplotlib.pyplot as plt

if __name__ == "__main__":
    env = CraftiumEnv(
        env_dir="craftium-envs/chop-tree",
        # render_mode="human",
        # max_timesteps=15,
    )
    iters = 10

    observation, info = env.reset()

    start = time.time()
    for i in range(iters):
        plt.clf()
        plt.imshow(np.transpose(observation, (1, 0, 2)))
        plt.pause(1e-7)

        # action = env.action_space.sample()
        action = dict()
        observation, reward, terminated, truncated, _info = env.step(action)

        print(i, reward, terminated, truncated)

        if terminated or truncated:
            observation, info = env.reset()

    end = time.time()
    print(f"** {iters} frames in {end-start}s => {(end-start)/iters} per frame")

    env.close()
