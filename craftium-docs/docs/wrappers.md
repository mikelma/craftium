# Action wrappers

`CraftiumEnv` environments define a fairly large action space with discrete and continuous values (see the dedicated [page](./obs-and-acts.md#action-space)). However, many tasks don't require the complete action space and can be greatly simplified by considering only the relevant actions to solve the task at hand. For this reason, craftium comes with `BinaryActionWrapper` and `DiscreteActionWrapper` (see API [docs](./reference.md)), that can be used to convert the default [`Dict`](https://gymnasium.farama.org/api/spaces/composite/#dict) action space into a simplified space.

For example,

```python
from craftium.wrappers import BinaryActionWrapper

env = BinaryActionWrapper(
    env,
    actions=["forward", "mouse x+", "mouse x-"],
    mouse_mov=0.5,
)
```

## BinaryActionWrapper

`BinaryActionWrapper` takes the `CraftiumEnv` to wrap as the first argument. Then, the `actions` parameters can be used to select the set of actions from the original action space that will be available in the wrapped environment (see the section on the [action space](./obs-and-acts.md#action-space) for the list of all available action names). In this example, the wrapped environment will only have 3 discrete actions: forward, move the mouse left, and move the mouse right. The last parameter, `mouse_mov` defines the magnitude of the mouse movement (must be in the [0, 1] range).

If we print `env.action_space` before applying the wrapper, we get the following Gymnasium space:
```python
Dict('aux1': Discrete(2), 'backward': Discrete(2), 'dig': Discrete(2), 'drop': Discrete(2), 'forward': Discrete(2), 'inventory': Discrete(2), 'jump': Discrete(2), 'left': Discrete(2), 'mouse': Box(-1.0, 1.0, (2,), float32), 'place': Discrete(2), 'right': Discrete(2), 'slot_1': Discrete(2), 'slot_2': Discrete(2), 'slot_3': Discrete(2), 'slot_4': Discrete(2), 'slot_5': Discrete(2), 'slot_6': Discrete(2), 'slot_7': Discrete(2), 'slot_8': Discrete(2), 'slot_9': Discrete(2), 'sneak': Discrete(2), 'zoom': Discrete(2))
```

After wrapping `env` with `BinaryActionWrapper`, we get that `env.action_space` is:
```python
MultiBinary(3)
```

The default action space has been reduced to a binary vector of only 3 elements (see [`MultiBinary`](https://gymnasium.farama.org/api/spaces/fundamental/#gymnasium.spaces.MultiBinary)). Note that `BinaryActionWrapper` allows for simultanaous actions. In the example above, the action `[1, 0, 1]` whould generate a forward movement action and a mouse (camera) rotation at the same time.

## DiscreteActionWrapper

Another way of reducing the action space of tasks is to discretize them as unique indices. For example, the actions `["forward", "mouse x+", "mouse x-"]` would be translated to three different actions: `1`, `2`, and `3`, in other words: *a* ∈ {1,2,3}. `DiscreteActionWrapper` converts the default `Dict` space into [`Discrete`](https://gymnasium.farama.org/api/spaces/fundamental/#gymnasium.spaces.Discrete). Let's try:

```python
from craftium.wrappers import DiscreteActionWrapper

env = DiscreteActionWrapper(
    env,
    actions=["forward", "mouse x+", "mouse x-"],
    mouse_mov=0.5,
)

print(env.action_space)
```

The program returns: `Discrete(4)`. What a surprise! We provided three valid actions to the wrapper but it returned an action space of four unique actions 🤔. This is because `DiscreteActionWrapper` adds an extra action (with index `0`) that does nothing (equivalent to the `NOP` action in other environments).

Finally, note that many of the [environments provided](./environments.md) by craftium employ `DiscreteActionWrapper` to simplify their optimization.
