[![Documentation Status](https://readthedocs.org/projects/craftium/badge/?version=latest)](https://craftium.readthedocs.io/en/latest/?badge=latest) ![Luanti version](https://img.shields.io/badge/Luanti-v5.12.0-blue)

# Craftium

<img src="../craftium-docs/imgs/craftium_logo.png" alt="Craftium logo" width="350" align="right">

✨ *Imagine the richness of Minecraft: open worlds, procedural generation, fully destructible voxel environments... but open source, without Java, easily extensible in [Lua](https://www.lua.org), and with the modern [Gymnasium](https://gymnasium.farama.org/index.html) and [PettingZoo](https://pettingzoo.farama.org/) APIs for AI single-and multi-agent research... This is* **Craftium!** ✨

**[[Docs](https://craftium.readthedocs.io/en/latest/)] [[GitHub](https://github.com/mikelma/craftium/)] [[Paper (ICML 2025)](https://arxiv.org/abs/2407.03969)]**

<p align="left">
  <img src="../craftium-docs/imgs/env_chop_tree.gif" width="100" align="center">
  <img src="../craftium-docs/imgs/env_room.gif" width="100" align="center">
  <img src="../craftium-docs/imgs/env_speleo.gif" width="100" align="center">
  <img src="../craftium-docs/imgs/env_spiders_attack.gif" width="100", align="center">
</p>

[Craftium](https://craftium.readthedocs.io/en/latest/) is a fully open-source platform for creating fast, rich, and diverse **single and multi-agent** environments. Craftium is based on the amazing [Luanti](https://www.luanti.org/) voxel game engine and the popular [Gymnasium](https://gymnasium.farama.org/index.html) and [PettingZoo](https://pettingzoo.farama.org/) APIs. Craftium forks Luanti to support:

- Connecting to Craftium's Python process (sending environment's data and receiving agent's action commands)
- Executing Craftium actions as keyboard and mouse controls.
- Extensions to the Lua API for creating RL environments.
- Enabling soft resets of the environments without restarting the engine.
- Luanti client(s)/server synchronization for slow agents (e.g., LLMs or VLMs).

📚 Craftium's documentation can be found [here](https://craftium.readthedocs.io/en/latest/).

📑 If you use craftium in your projects or research please consider [citing](#citing-craftium) the project, and don't hesitate to let us know what you have created using the library! 🤗

## Features ✨

- **Super extensible 🧩:** Luanti is built with modding in mind! The game engine is completely extensible using the [Lua](https://www.lua.org) programming language. Easily create mods to implement the environment that suits the needs of your research! See [environments](https://craftium.readthedocs.io/en/latest/environments/) for a showcase of what is possible with craftium.

- **Blazingly fast ⚡:** Craftium achieves +2K steps per second more than Minecraft-based alternatives! Environment richness, 3D, computational efficiency all meet in craftium!

- **Extensive documentation 📚:** Craftium extensively [documents](https://craftium.readthedocs.io) how to [use](https://craftium.readthedocs.io/en/latest/getting-started/) existing [environments](https://craftium.readthedocs.io/en/latest/environments) and [create](https://craftium.readthedocs.io/en/latest/creating-envs/) new ones. The documentation also includes a low-level [reference](https://craftium.readthedocs.io/en/latest/reference/) of the exported Python classes and gymnasium [Wrappers](https://craftium.readthedocs.io/en/latest/wrappers/), [extensions to the Lua API](https://craftium.readthedocs.io/en/latest/lua_functions/), and [code examples](https://craftium.readthedocs.io/en/latest/lua_env_cookbook/). Moreover, Craftium greatly benefits from existing Luanti documentation like the [wiki](https://wiki.luanti.org/), [reference](https://api.luanti.org/), and [modding book](https://rubenwardy.com/minetest_modding_book/en/basics/getting_started.html).

- **Modern API 🤖:** Craftium implements the well-known [Gymnasium](https://gymnasium.farama.org/index.html) and [PettingZoo](https://pettingzoo.farama.org/) APIs, opening the door to a vast number of existing tools and libraries compatible with these APIs. For example, [stable-baselines3](https://stable-baselines3.readthedocs.io) or [CleanRL](https://github.com/vwxyzjn/cleanrl) (check [examples](#examples-) section!).

- **Fully open source 🤠:** Both, craftium and Luanti are fully open-source projects. This allowed us to modify Luanti's source code to tightly integrate it with our library, reducing the number of ugly hacks.

- **No more Java 👹:** The Minecraft game is written in Java, not an especially friendly language for clusters and high-performance applications. Contrarily, Luanti is written in C++, more adequate for clusters, and highly performant!

## Installation ⚙️

First, clone craftium using the `--recurse-submodules` flag (**important**: the flag fetches submodules needed by the library) and `cd` into the project's main directory:

```bash
git clone --recurse-submodules https://github.com/mikelma/craftium.git # if you prefer ssh: git@github.com:mikelma/craftium.git
cd craftium
```

`craftium` depends on [Luanti](https://github.com/luanti-org/luanti), which in turn, depends on a series of libraries that we need to install. Luanti's repo contains [instructions](https://github.com/luanti-org/luanti/blob/master/doc/compiling/linux.md) on how to setup the build environment for many Linux distros (and [MacOS](https://github.com/luanti-org/luanti/blob/master/doc/compiling/macos.md). In Ubuntu/Debian the following command installs all the required libraries:

```bash
sudo apt install g++ make libc6-dev cmake libpng-dev libjpeg-dev libgl1-mesa-dev libsqlite3-dev libogg-dev libvorbis-dev libopenal-dev libcurl4-gnutls-dev libfreetype6-dev zlib1g-dev libgmp-dev libjsoncpp-dev libzstd-dev libluajit-5.1-dev gettext libsdl2-dev
```

Additionally, `craftium` requires Python's header files to build a dedicated Python module implemented in C (`mt_server`):

```bash
sudo apt install libpython3-dev
```

Then, check that `setuptools` is updated and run the installation command in the craftium repo's directory:

```bash
pip install -U setuptools
```

and,

```bash
pip install .
```

This last command should compile Luanti, install Python dependencies, and, finally, craftium. If the installation process fails, please consider submitting an issue [here](https://github.com/mikelma/craftium/issues). Note that this command only installs the minimum dependencies to run craftium, execute `pip install ".[examples]"` for installing optional dependencies (e.g., for running examples).

## Getting started 💡

As craftium implements the Gymnasium and PettingZoo APIs, using craftium environments is as simple as using any Gymnasium environment. The example below shows the implementation of a random agent in one of the craftium's default environments:

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
model.learn(total_timesteps=1_000_000)

env.close()
```

This example trains a CNN-based agent for 1M timesteps in the `Craftium/ChopTree-v0` environment using PPO. Additionally, we set up a custom logger that records training statistics to a CSV file inside the `logs-ppo-agent/` directory.

Craftium is not only limited to "typical" RL scenarios, its versatility makes it the ideal platform for meta-RL, open-ended learning, continual and lifelong RL, or unsupervised environment design (and more!). As a showcase, Craftium provides open-world and procedurally generated tasks (see [environments](https://craftium.readthedocs.io/en/latest/environments/) for more info). This code snippet initializes a procedurally generated dungeon environment with 5 rooms and a maximum number of 4 monsters per room:
```python
env, map_str = craftium.make_dungeon_env(
    mapgen_kwargs=dict(
        n_rooms=5,
        max_monsters_per_room=5,
    ),
    return_map_str=True,
)
print(map_str.split("-")[1])
```

## Examples 🤓

By implementing Gymnasium's API, craftium supports many existing tools and libraries. Check these scripts for some examples:

- **Stable baselines3**: [sb3_train.py](https://github.com/mikelma/craftium/blob/main/sb3_train.py)
- **Ray rllib**: [sb3_train.py](https://github.com/mikelma/craftium/blob/main/ray_train.py)
- **CleanRL**: [cleanrl_ppo_train.py](https://github.com/mikelma/craftium/blob/main/cleanrl_ppo_train.py)

## Citing Craftium 📑

```bibtex
@inproceedings{malagon2025craftium,
  title={Craftium: Bridging Flexibility and Efficiency for Rich 3D Single- and Multi-Agent Environments},
  author={Mikel Malag{\'o}n and Josu Ceberio and Jose A. Lozano},
  booktitle={International Conference on Machine Learning (ICML)},
  year={2025}
}
```

## Contributing 🏋️

We appreciate contributions to craftium! craftium is in early development, so many possible improvements and bugs are expected. If you have found a bug or have a suggestion, please consider opening an [issue](https://github.com/mikelma/craftium/issues) if it isn't already covered. In case you want to submit a fix or an improvement to the library, [pull requests](https://github.com/mikelma/craftium/pulls) are also very welcome!

## License 📖

Craftium forks [Luanti](https://github.com/luanti-org/luant) and its source code is distributed with this library. Craftium maintains the same licenses as Luanti:  MIT for code and CC-BY-SA 3.0 for content.

## Acknowledgements 🤗

We thank the Luanti and Farama developers (and respective communities!) for their ongoing efforts to maintain and continuously improve these projects.

We also thank [minerl](minerl.readthedocs.io/), [MineDojo](https://minedojo.org/), and projects integrating Luanti and RL ([here](https://github.com/EleutherAI/minetest) and [here](https://github.com/Astera-org/minetest)) for serving as inspiration for this project.

We are especially grateful (☺️) to [@vadel](https://github.com/vadel) and [@abarrainkua](https://github.com/abarrainkua) for reading preliminary versions of the paper, and to _Pascu_ for the technical support.

Finally, we thank all Craftium contributors 🙌 for their dedication and support:

- [@enebas05](https://github.com/enebas05)
- [@francelico](https://github.com/francelico)
- [@Wolfxyz16](https://github.com/Wolfxyz16)
