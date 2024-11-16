import numpy as np
from gymnasium import ActionWrapper, Env
from gymnasium.spaces import MultiBinary, Discrete

from .craftium_env import ACTION_ORDER


def check_actions_valid(actions):
    # obtain valid action names
    mouse_actions = [f"mouse {ax}{sign}" for ax, sign in zip(["x", "y", "x", "y"], ["+", "-", "-", "+"])]
    valid_actions = ACTION_ORDER + mouse_actions
    del valid_actions[valid_actions.index("mouse")]

    # check if the provided action names are valid
    assert sum([a not in valid_actions for a in actions]) == 0, \
        f"Invalid action given. Valid actions are: {valid_actions}"


def clip_mouse(m):
    mouse_mov = np.clip(m, 0., 1.)
    if m != mouse_mov:
        print(f"Warning (DiscreteActionWrapper): mouse_mov \
        is {m}, clipping in range 0-1.")
    return mouse_mov


class BinaryActionWrapper(ActionWrapper):
    """A Gymnasium `ActionWrapper` that translates craftium's `Dict` action space into a binary (discretized) action space [`MultiBiniary`](https://gymnasium.farama.org/api/spaces/fundamental/#gymnasium.spaces.MultiBinary).

    :param env: The environment to wrap.
    :param actions: A list of strings containing the names of the actions that will consititute the new action space.
    :params mouse_mov: Magnitude of the mouse movement. Must be in the [0, 1] range, else it will be clipped.
    """
    def __init__(self, env: Env, actions: list[str], mouse_mov: float = 0.5):
        ActionWrapper.__init__(self, env)

        check_actions_valid(actions)
        self.actions = actions
        self.action_space = MultiBinary(len(actions))
        self.mouse_mov = clip_mouse(mouse_mov)

    def process(self, action):
        assert len(action) == len(self.actions), \
            f"Incorrect number of actions, got {len(action)} but expected {len(self.actions)}"

        res = {}
        mouse = [0, 0]
        for a, name in zip(action, self.actions):
            if a == 0:
                continue

            if name == "mouse x+":
                mouse[0] += self.mouse_mov
            elif name == "mouse x-":
                mouse[0] -= self.mouse_mov
            elif name == "mouse y+":
                mouse[1] += self.mouse_mov
            elif name == "mouse y-":
                mouse[1] -= self.mouse_mov
            else:
                res[name] = a

        res["mouse"] = mouse

        return res

    def action(self, action):
        if isinstance(action, list) or isinstance(action, np.ndarray):
            return [self.process(act) for act in action]
        return self.process(action)


class DiscreteActionWrapper(ActionWrapper):
    """A Gymnasium `ActionWrapper` that translates craftium's `Dict` action space into a discretized action space [`Discrete`](https://gymnasium.farama.org/api/spaces/fundamental/#gymnasium.spaces.Discrete).

    Unlike `DiscreteActionWrapper`, this wrapper adds an additional action to the action space in order to include the `NOP` action. This action is equivalent to `{}` in the `Dict` space or to a list of zeros in the `MultiBinary` space. The `NOP` action has index `0`, and the rest of the actions have the consecutive idexes. Thus, the number of actions of the environment will be `len(actions)+1`.

    :param env: The environment to wrap.
    :param actions: A list of strings containing the names of the actions that will consititute the new action space.
    :params mouse_mov: Magnitude of the mouse movement. Must be in the [0, 1] range, else it will be clipped.
    """
    def __init__(self, env: Env, actions: list[str], mouse_mov: float = 0.5):
        ActionWrapper.__init__(self, env)

        check_actions_valid(actions)

        self.actions = actions
        self.action_space = Discrete(len(actions)+1)
        self.mouse_mov = clip_mouse(mouse_mov)

    def process(self, action):
        assert action >= 0 and action <= len(self.actions), \
            f"Action out of bound, got {action} but expected 0 <= action <= {len(self.actions)}"

        # if the action has index 0, return an empty action (NOP)
        if action == 0:
            return {}

        res = {}

        name = self.actions[action-1]

        mouse = [0, 0]

        if name == "mouse x+":
            mouse[0] += self.mouse_mov
        elif name == "mouse x-":
            mouse[0] -= self.mouse_mov
        elif name == "mouse y+":
            mouse[1] += self.mouse_mov
        elif name == "mouse y-":
            mouse[1] -= self.mouse_mov
        else:
            res[name] = 1

        res["mouse"] = mouse

        return res

    def action(self, action):
        if isinstance(action, list) or isinstance(action, np.ndarray):
            return [self.process(act) for act in action]
        return self.process(action)
