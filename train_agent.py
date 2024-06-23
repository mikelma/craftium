import numpy as np
import matplotlib.pyplot as plt
from stable_baselines3 import A2C #, PPO
from stable_baselines3.common import logger
from craftium import CraftiumEnv, DiscreteActionWrapper
from uuid import uuid4
import os


def make_env():
    env = CraftiumEnv(
        env_dir="craftium-envs/room",
        max_timesteps=500,
        init_frames=200,
        obs_width=64,
        obs_height=64,
        # render_mode="human",
        minetest_dir=os.getcwd(),
    )

    env = DiscreteActionWrapper(
        env,
        actions=["forward", "mouse x+", "mouse x-"],
        mouse_mov=0.5,
    )

    return env

if __name__ == "__main__":
    env = make_env()

    log_path = f"./run-logs/{str(uuid4())}/"
    new_logger = logger.configure(log_path, ["stdout", "csv"])

    model = A2C("CnnPolicy", env, verbose=1)
    model.set_logger(new_logger)
    model.learn(total_timesteps=100_000)

    # # Enjoy trained agent
    # vec_env = model.get_env()
    # obs = vec_env.reset()
    # for i in range(1000):
    #     print(i)
    #     action, _states = model.predict(obs, deterministic=True)
    #     obs, rewards, dones, info = vec_env.step(action)
    #     print(rewards)
    #     plt.clf()
    #     plt.imshow(np.transpose(obs[0], (2, 1, 0)))
    #     plt.pause(1e-7)

    env.close()
