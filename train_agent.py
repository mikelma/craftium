from argparse import ArgumentParser
from uuid import uuid4
import os
from stable_baselines3 import A2C, PPO
from stable_baselines3.common import logger
from stable_baselines3.common.vec_env import DummyVecEnv, VecMonitor, VecFrameStack
import gymnasium as gym
import craftium

def parse_args():
    parser = ArgumentParser()

    # fmt: off
    parser.add_argument("--run-name", type=str, default=None,
        help="Unique name for the run. Defaults to a random uuid.")
    parser.add_argument("--runs-dir", type=str, default="./run-logs/",
        help="Name of the directory where run's data is stored. Defaults to './run-logs/'")

    parser.add_argument("--env-id", type=str, default="Craftium/ChopTree-v0",
        help="Name (registered) of the environment.")
    parser.add_argument("--total-timesteps", type=int, default=10_000_000,
        help="Number of timesteps to train for.")
    parser.add_argument("--num-envs", type=int, default=4,
        help="Number of environments to use.")
    parser.add_argument("--method", type=str, default="a2c", choices=["ppo", "a2c"],
        help="RL method to use to optimize the agent.")
    # fmt: on

    return parser.parse_args()

def make_env(env_id):
    def _init():
        # set up the environment
        craftium_kwargs = dict(
            frameskip=3,
            rgb_observations=False,
            gray_scale_keepdim=True,
        )

        env = gym.make(env_id, **craftium_kwargs)
        env.reset()

        return env
    return _init

if __name__ == "__main__":
    args = parse_args()

    if args.run_name is None:
        run_name = f"{args.env_id.replace('/', '-')}-{args.method}--{str(uuid4())}"
    else:
        run_name = args.run_name

    # configure SB3 logger
    log_path = os.path.join(args.runs_dir, run_name)
    print(f"** Storing run's data in {log_path}")
    new_logger = logger.configure(log_path, ["stdout", "csv"])

    envs = DummyVecEnv([make_env(args.env_id) for _ in range(args.num_envs)])
    envs = VecFrameStack(envs, 3)
    envs = VecMonitor(envs)

    method_class = PPO if args.method == "ppo" else A2C
    model = method_class("CnnPolicy", envs, verbose=1)
    model.set_logger(new_logger)

    model.learn(total_timesteps=args.total_timesteps)

    envs.close()
