[![Documentation Status](https://readthedocs.org/projects/craftium/badge/?version=latest)](https://craftium.readthedocs.io/en/latest/?badge=latest)

# Craftium

<img src="../craftium-docs/imgs/craftium_logo.png" alt="Craftium logo" width="350" align="right">

✨ *Imagine the features of Minecraft: open world, procedural generation, fully destructible voxel environments... but open source, without Java, easily extensible in [Lua](https://www.lua.org), and with the modern [Gymnasium API](https://gymnasium.farama.org/index.html) designed for RL... This is* **Craftium!** ✨

**[[Docs](https://craftium.readthedocs.io/en/latest/)] [[GitHub](https://github.com/mikelma/craftium/)] [[Paper (ArXiv)](https://arxiv.org/abs/2407.03969)]**

<p align="left">
  <img src="../craftium-docs/imgs/env_chop_tree.gif" width="100" align="center">
  <img src="../craftium-docs/imgs/env_room.gif" width="100" align="center">
  <img src="../craftium-docs/imgs/env_speleo.gif" width="100" align="center">
  <img src="../craftium-docs/imgs/env_spiders_attack.gif" width="100", align="center">
</p>

[Craftium](https://craftium.readthedocs.io/en/latest/) is a fully open-source platform for creating Reinforcement Learning (RL) environments and tasks that provides a [Gymnasium](https://gymnasium.farama.org/index.html) wrapper for the [Minetest](https://www.minetest.net/) voxel game engine. Craftium forks Minetest to support:

- Connecting to Craftium's Python process via TCP (sending observations, and other data; receiving action commands)
- Executing Craftium actions as keyboard and mouse controls.
- Extesions to the Lua API for creating RL environments and tasks.
- Minetest's client/server synchronization.

📚 Craftium's documentation can be found [here](https://craftium.readthedocs.io/en/latest/).

📑 If you use craftium in your projects or research please consider [citing](#citing-craftium) the project, and don't hesitate to let us know what you have created using the library! 🤗

## Features ✨

- **Super extensible 🧩:** Minetest is built with modding in mind! The game engine is completely extensible using the [Lua](https://www.lua.org) programming language. Easily create mods to implement the environment that suits the needs of your research!

- **Modern RL API 🤖:** Craftium slightly modifies Mintest to communicate with Python, and implements the well-known [Gymnasium](https://gymnasium.farama.org/index.html)'s [Env](https://gymnasium.farama.org/api/env/) API. This opens the door to a huge number of existing tools and libraries compatible with this API, such as [stable-baselines3](https://stable-baselines3.readthedocs.io) or [CleanRL](https://github.com/vwxyzjn/cleanrl).

- **Fully open source 🤠:** Craftium is based on the Minetest and Gymnasium, both open-source projects.

- **No more Java ⚡:** The Minecraft game is written in Java, not a very friendly language for clusters and high-performance applications. Contrarily, Minetest is written in C++, much more friendly for clusters, and highly performant!

## Installation ⚙️

First, clone craftium using the `--recurse-submodules` flag (**important**: the flag fetches submodules needed by the library) and `cd` into the project's main directory:

```bash
git clone --recurse-submodules https://github.com/mikelma/craftium.git # if you prefer ssh: git@github.com:mikelma/craftium.git
cd craftium
```

`craftium` depends on [Minetest](https://github.com/minetest/minetest), which in turn, depends on a series of libraries that we need to install. Minetest's repo contains [instructions](https://github.com/minetest/minetest/blob/master/doc/compiling/linux.md) on how to setup the build environment for many Linux distros (and  [MacOS](https://github.com/minetest/minetest/blob/master/doc/compiling/macos.md)). In Ubuntu/Debian the following command installs all the required libraries:

```bash
sudo apt install g++ make libc6-dev cmake libpng-dev libjpeg-dev libgl1-mesa-dev libsqlite3-dev libogg-dev libvorbis-dev libopenal-dev libcurl4-gnutls-dev libfreetype6-dev zlib1g-dev libgmp-dev libjsoncpp-dev libzstd-dev libluajit-5.1-dev gettext libsdl2-dev
```

Then, check that `setuptools` is updated and run the installation command in the craftium repo's directory:

```bash
pip install -U setuptools
```

and,

```bash
pip install .
```

This last command should compile minetest, install python dependencies, and, finally, craftium. If the installation process fails, please consider submitting an issue [here](https://github.com/mikelma/craftium/issues).

## Getting started 💡

Craftium implements [Gymnasium's](https://gymnasium.farama.org/) [`Env`](https://gymnasium.farama.org/api/env/) API, making it compatible with many popular reinforcement learning libraries and tools like [stable-baselines3](https://stable-baselines3.readthedocs.io/en/master/index.html) and [CleanRL](https://github.com/vwxyzjn/cleanrl).

Thanks to the mentioned API, using craftium environments is as simple as using any gymnasium environment. The example below shows the implementation of a random agent in one of the craftium's environments:

```python
import gymnasium as gym
import craftium

env = gym.make("Craftium/ChopTree-v0")

observation, info = env.reset()

for t in range(100):
    action = env.action_space.sample()  # get a random action
    observation, reward, terminated, truncated, _info = env.step(action)

    if terminated or truncated:
        observation, info = env.reset()

env.close()
```

Training a CNN-based agent using PPO is as simple as:

```python
from stable_baselines3 import PPO
from stable_baselines3.common import logger
import gymnasium as gym
import craftium

env = gym.make("Craftium/ChopTree-v0")

model = PPO("CnnPolicy", env, verbose=1)

new_logger = logger.configure("logs-ppo-agent", ["stdout", "csv"])
model.set_logger(new_logger)
model.learn(total_timesteps=100_000)

env.close()
```

This example trains a CNN-based agent for 10K timesteps in the `Craftium/ChopTree-v0` environment using PPO. Additionally, we set up a custom logger that records training statistics to a CSV file inside the `logs-ppo-agent/` directory.

## Citing Craftium 📑

```bibtex
@article{malagon2024craftium,
  title={Craftium: An Extensible Framework for Creating Reinforcement Learning Environments},
  author={Mikel Malag{\'o}n and Josu Ceberio and Jose A. Lozano},
  journal={arXiv preprint arXiv:2407.03969},
  year={2024}
}
```

## Contributing 🏋️

We appreciate contributions to craftium! craftium is in early development, so many possible improvements and bugs are expected. If you have found a bug or have a suggestion, please consider opening an [issue](https://github.com/mikelma/craftium/issues) if it isn't already covered. In case you want to submit a fix or an improvement to the library, [pull requests](https://github.com/mikelma/craftium/pulls) are also very welcome!

## License 📖

Craftium is based on [minetest](https://github.com/minetest/minetest) and its source code is distributed with this library. Craftium maintains the same licenses as minetest:  MIT for code and CC-BY-SA 3.0 for content.

## Acknowledgements 🤗

We thank the minetest and gymnasium developers and community for maintaining such an excellent open-source project. We also thank [minerl](minerl.readthedocs.io/) and other projects integrating minetest and gymnasium ([here](https://github.com/EleutherAI/minetest) and [here](https://github.com/Astera-org/minetest)) for serving as inspiration for this project.
