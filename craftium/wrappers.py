import numpy as np
from gymnasium import ActionWrapper, Env
from gymnasium.spaces import MultiDiscrete

from .env import ACTION_ORDER


class DiscreteActionWrapper(ActionWrapper):
    """A Gymnasium `ActionWrapper` that translates craftium's `Dict` action space into a binary (discretized) action space.
    Specifically into the `MultiDiscrete` space.

    :param env: The environment to wrap.
    :param actions: A list of strings containing the names of the actions that will consititute the new action space.
    :params mouse_mov: Magnitude of the mouse movement. Must be in the [0, 1] range, else it will be clipped.
    """
    def __init__(self, env: Env, actions: list[str], mouse_mov: float = 0.5):
        ActionWrapper.__init__(self, env)

        self.actions = actions

        # obtain valid action names
        mouse_actions = [f"mouse {ax}{sign}" for ax, sign in zip(["x", "y", "x", "y"], ["+", "-", "-", "+"])]
        valid_actions = ACTION_ORDER + mouse_actions
        del valid_actions[valid_actions.index("mouse")]

        # check if the provided action names are valid
        assert sum([a not in valid_actions for a in actions]) == 0, \
            f"Invalid action given. Valid actions are: {valid_actions}"

        # define the action space for gymnasium
        self.action_space = MultiDiscrete(np.full(len(actions), 2))

        # clip the mouse movement if needed
        self.mouse_mov = np.clip(mouse_mov, 0., 1.)
        if self.mouse_mov != mouse_mov:
            print(f"Warning (DiscreteActionWrapper): mouse_mov \
            is {mouse_mov}, clipping in range 0-1.")

    def action(self, action):
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
