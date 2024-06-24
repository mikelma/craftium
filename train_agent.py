import numpy as np
import matplotlib.pyplot as plt
from stable_baselines3 import A2C #, PPO
from stable_baselines3.common import logger
from craftium import CraftiumEnv, DiscreteActionWrapper
from uuid import uuid4
import os
from argparse import ArgumentParser


def parse_args():
    parser = ArgumentParser()

    # fmt: off
    parser.add_argument("--tcp-port", type=int, default=None,
        help="TCP port to use for communicating with minetest.")
    parser.add_argument("--run-name", type=str, default=None,
        help="Unique name for the run. Defaults to a random uuid.")
    parser.add_argument("--runs-dir", type=str, default="./run-logs/",
        help="Name of the directory where run's data is stored. Defaults to './run-logs/'")

    parser.add_argument("--total-timesteps", type=int, default=100_000,
        help="Number of timesteps to train for.")
    parser.add_argument("--episode-timesteps", type=int, default=500,
        help="Length of episodes in number of timesteps.")
    parser.add_argument("--init-frames", type=int, default=200,
        help="Number of frames to wait until the minetest's world is loaded.")
    # fmt: on

    return parser.parse_args()


def make_env(**env_kwargs):
    env = CraftiumEnv(
        env_dir="craftium-envs/room",
        obs_width=64,
        obs_height=64,
        minetest_dir=os.getcwd(),
        **env_kwargs,
    )

    env = DiscreteActionWrapper(
        env,
        actions=["forward", "mouse x+", "mouse x-"],
        mouse_mov=0.5,
    )

    return env

if __name__ == "__main__":
    args = parse_args()

    env = make_env(
        max_timesteps=args.episode_timesteps,
        init_frames=args.init_frames,
        tcp_port=args.tcp_port,
    )

    run_name = str(uuid4()) if args.run_name is None else args.run_name
    log_path = os.path.join(args.runs_dir, run_name)

    print(f"** Storing run's data in {log_path}")
    new_logger = logger.configure(log_path, ["stdout", "csv"])

    model = A2C("CnnPolicy", env, verbose=1)
    model.set_logger(new_logger)

    model.learn(total_timesteps=args.total_timesteps)

    env.close()
