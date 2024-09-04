# Getting started

## Random agent
This tutorial showcases the basic usage of craftium by implementing a random agent, a good place to start and check everything is working as expected! For a tutorial on how to install craftium check this [guide](./installation.md).

First, import the necessary python packages for this example:

```python
import matplotlib.pyplot as plt
import numpy as np
import gymnasium as gym
import craftium
```

### Creating an environment

Although craftium can be thought of as a general environment creation framework for reinforcement learning, it comes with some predefined environments. Check the [environments](./environments.md) page for a list and description of all the provided environments.

In this example, we'll load the `Craftium/Room-v0` environment, where the objective is to reach a red block inside a closed room.

By default, craftium registers the provided environments as Gymnasium environments under the `Craftium/` prefix, this means that we can initialize craftium's environments using `gym.make` (check the [Register and Make](https://gymnasium.farama.org/api/registry/#gymnasium.register) page of the Gymnasium's docs for more info):

```python
env = gym.make("Craftium/ChopTree-v0")
```

### Interaction loop

The next step is to implement the agent-environment interaction loop. Again, as craftium implements the [Gymnasium API](https://gymnasium.farama.org/api/env/), it's as simple as:

```python
observation, info = env.reset()

for t in range(20):
    action = env.action_space.sample()

    # plot the observation
    plt.clf()
    plt.imshow(np.transpose(observation, (1, 0, 2)))
    plt.pause(0.02)  # wait for 0.02 seconds

    observation, reward, terminated, truncated, _info = env.step(action)

    if terminated or truncated:
        observation, info = env.reset()

env.close()
```

The code above just starts an episode calling `env.reset`, then samples a random action, plots the current observation, and executes the action using `env.step`. If the episode finishes, `env.reset` is called again to start a new episode. Finally, when the loop ends, `env.close` cleanly closes the environment.

Finally, check the [page](./obs-and-acts.md) on observations and actions for a complete description of the craftium's default observation and action spaces.

## Using `CraftiumEnv`

The example above employs Gymnasium's `make` utility to load the environments registered by craftium. In this section we explain how to load environments without using the `make` utility, directly employing `CraftiumEnv`. `CraftiumEnv` is craftium's main class, wrapping the modified minetest game in the Gymnasium API.

To import `CraftiumEnv` just:

```python
from craftium import CraftiumEnv
```

Then, to create an environment call `CraftiumEnv`'s initializer:

```python
env = CraftiumEnv(
    env_dir="path/to/env-dir",
    render_mode="human",
    obs_width=512,
    obs_height=512,
)
```

The first parameter, `env_dir` is the single mandatory parameter and specifies the path to the directory where the environment's data is located. For example, in the craftium's repo, these directories are inside [`craftium-env`](https://github.com/mikelma/craftium/tree/main/craftium-envs). If you are using a custom environment, this path should be set to your environment's directory, as specified in the tutorial on [creating custom environments](./creating-envs.md#using-the-custom-environment).

The rest of the parameters are optional, where the ones in the code section above are the most common. `render_mode` is a common parameter in Gymnasium environments (see [docs](https://gymnasium.farama.org/api/env/#gymnasium.Env.render) for more info) is used to set the rendering mode of the environment. Finally, `obs_width` and `obs_height` specify the size of the observations in pixels.

## Next steps

These are some resources that might be interesting for your next steps!

- [Creating custom environments](./creating-envs.md) page.
- [Wrappers](./wrappers.md) page.
- [Craftium training example](https://github.com/mikelma/craftium/blob/main/sb3_train.py).
- [Craftium environment implementation](https://github.com/mikelma/craftium/tree/main/craftium-envs).
