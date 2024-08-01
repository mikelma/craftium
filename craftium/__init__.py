from .craftium_env import CraftiumEnv
from .wrappers import BinaryActionWrapper, DiscreteActionWrapper

from gymnasium.envs.registration import register, WrapperSpec


#
# Environment registrations:
# ~~~~~~~~~~~~~~~~~~~~~~~~~~

import os
from .minetest import is_minetest_build_dir


# get the craftium's root directory, where the craftium-envs directory
# containing all the environments is located
if is_minetest_build_dir(os.getcwd()):
    root_path = os.getcwd()
else:  # in this case, this module might be running as an installed python package
    # get the path location of the parent of this module
    root_path = os.path.dirname(__file__)

register(
    id="Craftium/Room-v0",
    entry_point="craftium.craftium_env:CraftiumEnv",
    additional_wrappers=[
        WrapperSpec(
            name="DiscreteActionWrapper",
            entry_point="craftium.wrappers:DiscreteActionWrapper",
            kwargs=dict(
                actions=["forward", "mouse x+", "mouse x-"],
                mouse_mov=0.5,
            ),
        )
    ],
    # kwargs
    kwargs=dict(
        env_dir=os.path.join(root_path, "craftium-envs/room"),
        obs_width=64,
        obs_height=64,
        max_timesteps=2000,
        init_frames=200,
    )
)

register(
    id="Craftium/SmallRoom-v0",
    entry_point="craftium.craftium_env:CraftiumEnv",
    additional_wrappers=[
        WrapperSpec(
            name="DiscreteActionWrapper",
            entry_point="craftium.wrappers:DiscreteActionWrapper",
            kwargs=dict(
                actions=["forward", "mouse x+", "mouse x-"],
                mouse_mov=0.5,
            ),
        )
    ],
    # kwargs
    kwargs=dict(
        env_dir=os.path.join(root_path, "craftium-envs/small-room"),
        obs_width=64,
        obs_height=64,
        max_timesteps=1000,
        init_frames=200,
    )
)

register(
    id="Craftium/ChopTree-v0",
    entry_point="craftium.craftium_env:CraftiumEnv",
    additional_wrappers=[
        WrapperSpec(
            name="DiscreteActionWrapper",
            entry_point="craftium.wrappers:DiscreteActionWrapper",
            kwargs=dict(
                actions=["forward", "jump", "dig", "mouse x+", "mouse x-", "mouse y+", "mouse y-"],
                mouse_mov=0.5,
            ),
        )
    ],
    # kwargs
    kwargs=dict(
        env_dir=os.path.join(root_path, "craftium-envs/chop-tree"),
        obs_width=64,
        obs_height=64,
        max_timesteps=2000,
        init_frames=200,
        minetest_conf=dict(
            give_initial_stuff=True,
            initial_stuff="default:axe_steel",
        ),
    )
)

register(
    id="Craftium/Speleo-v0",
    entry_point="craftium.craftium_env:CraftiumEnv",
    additional_wrappers=[
        WrapperSpec(
            name="DiscreteActionWrapper",
            entry_point="craftium.wrappers:DiscreteActionWrapper",
            kwargs=dict(
                actions=["forward", "jump", "mouse x+", "mouse x-",
                         "mouse y+", "mouse y-"],
                mouse_mov=0.5,
            ),
        )
    ],
    # kwargs
    kwargs=dict(
        env_dir=os.path.join(root_path, "craftium-envs/speleo"),
        obs_width=64,
        obs_height=64,
        max_timesteps=3000,
        init_frames=200,
    )
)

register(
    id="Craftium/SpidersAttack-v0",
    entry_point="craftium.craftium_env:CraftiumEnv",
    additional_wrappers=[
        WrapperSpec(
            name="DiscreteActionWrapper",
            entry_point="craftium.wrappers:DiscreteActionWrapper",
            kwargs=dict(
                actions=["forward", "left", "right", "jump", "dig", "mouse x+", "mouse x-",
                         "mouse y+", "mouse y-"],
                mouse_mov=0.5,
            ),
        )
    ],
    # kwargs
    kwargs=dict(
        env_dir=os.path.join(root_path, "craftium-envs/spiders-attack"),
        obs_width=64,
        obs_height=64,
        max_timesteps=4000,
        init_frames=200,
        minetest_conf=dict(
            give_initial_stuff=True,
            initial_stuff="default:sword_steel",
        ),
    )
)
