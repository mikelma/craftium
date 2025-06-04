from .minetest import is_minetest_build_dir
import os
from .craftium_env import CraftiumEnv
from .multiagent_env import MarlCraftiumEnv
from .wrappers import BinaryActionWrapper, DiscreteActionWrapper

from gymnasium.envs.registration import register, WrapperSpec
from typing import Any, Optional


DEFAULT_PROCDUNGEONS_CONF = dict(
    give_initial_stuff=True,
    initial_stuff="default:sword_steel",
    performance_tradeoffs=True,
    monster_type_a="mobs_monster:sand_monster",
    monster_type_b="mobs_monster:spider",
    monster_type_c="mobs_monster:stone_monster",
    monster_type_d="mobs_monster:mese_monster",
    wall_material="default:steelblock",
    objective_item="default:diamond",
    rwd_objective=10.0,
    rwd_kill_monster=0.5,
)


def make_dungeon_env(
        ascii_map: Optional[str] = None,
        mapgen_kwargs: dict[str, Any] = dict(),
        wall_height: int = 5,
        return_map_str: bool = False,
        **kwargs
):
    """Utility function to instantiate procedurally generated dungeon environments (see [`Craftium/ProcDungeons-v0`](https://craftium.readthedocs.io/en/latest/environments/#procedural-environment-generation)).

    :param ascii_map: ASCII representation of the map. This is optional, and if not given, a random map will be generated using `RandomMapGen`.
    :param mapgen_kwargs: Arguments for  `RandomMapGen`. The arguments provided via this parameter will overwrite the default values of `RandomMapGen`. This argument is only used if `ascii_map` is `None`.
    :param wall_height: The height of the walls. This argument is only used if `ascii_map` is `None`.
    :param return_map_str: If set to `True` the function returs the generated map as second return value.
    :param **kwargs: Extra arguments to provide to `gymnasium.make`. If the `minetest_conf` argument is set, it's values will overwrite the default parameters of the environment.
    """
    import gymnasium as gym
    from .extra.random_map_generator import RandomMapGen

    # generate the map
    if ascii_map is None:
        mapgen = RandomMapGen(**mapgen_kwargs)
        ascii_map = mapgen.rasterize(wall_height=wall_height)

    minetest_conf = DEFAULT_PROCDUNGEONS_CONF
    if "minetest_conf" in kwargs:
        for key, value in kwargs["minetest_conf"].items():
            minetest_conf[key] = value

    minetest_conf["ascii_map"] = ascii_map.replace("\n", "\\n")
    kwargs["minetest_conf"] = minetest_conf

    env = gym.make("Craftium/ProcDungeons-v0", **kwargs)

    if return_map_str:
        return env, ascii_map
    return env


#
# Environment registrations:
# ~~~~~~~~~~~~~~~~~~~~~~~~~~


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
        max_timesteps=1000,
        init_frames=200,
        soft_reset=True,
        _voxel_obs_available=True,
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
        max_timesteps=500,
        init_frames=200,
        soft_reset=True,
        _voxel_obs_available=True,
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
                actions=["forward", "jump", "dig", "mouse x+",
                         "mouse x-", "mouse y+", "mouse y-"],
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
        _minetest_conf=dict(
            give_initial_stuff=True,
            initial_stuff="default:axe_steel",
        ),
        _voxel_obs_available=True,
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
        max_timesteps=500,
        init_frames=200,
        _voxel_obs_available=True,
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
        _minetest_conf=dict(
            give_initial_stuff=True,
            initial_stuff="default:sword_steel",
        ),
        _voxel_obs_available=True,
    )
)

register(
    id="Craftium/OpenWorld-v0",
    entry_point="craftium.craftium_env:CraftiumEnv",
    additional_wrappers=[
        WrapperSpec(
            name="DiscreteActionWrapper",
            entry_point="craftium.wrappers:DiscreteActionWrapper",
            kwargs=dict(
                actions=["forward", "backward", "left", "right", "jump", "sneak",
                         "dig", "place", "slot_1", "slot_2", "slot_3", "slot_4",
                         "slot_5", "mouse x+", "mouse x-", "mouse y+", "mouse y-"],
                mouse_mov=0.1,
            ),
        )
    ],
    # kwargs
    kwargs=dict(
        env_dir=os.path.join(root_path, "craftium-envs/voxel-libre2"),
        obs_width=320,
        obs_height=180,
        max_timesteps=10_000,
        init_frames=200,
        game_id="VoxeLibre",
        _minetest_conf=dict(
            max_block_generate_distance=3, # 16x3 blocks
            mcl_logging_mobs_spawn=True,
            hud_scaling=0.5,
            fov=90,
            console_alpha=0,
            ### Graphics Effects
            smooth_lighting=False,
            performance_tradeoffs=True,
            enable_particles=False,
        ),
        _voxel_obs_available=True,
    )
)

register(
    id="Craftium/ProcDungeons-v0",
    entry_point="craftium.craftium_env:CraftiumEnv",
    additional_wrappers=[
        WrapperSpec(
            name="DiscreteActionWrapper",
            entry_point="craftium.wrappers:DiscreteActionWrapper",
            kwargs=dict(
                actions=["forward", "left", "right", "jump", "dig",
                         "mouse x+", "mouse x-", "mouse y+", "mouse y-"],
                mouse_mov=0.1,
            ),
        )
    ],
    # kwargs
    kwargs=dict(
        env_dir=os.path.join(root_path, "craftium-envs/procgen-dungeons"),
        obs_width=64,
        obs_height=64,
        max_timesteps=4000,
        init_frames=200,
        soft_reset=True,
        _minetest_conf=dict(
            give_initial_stuff=True,
            initial_stuff="default:sword_steel",  # Provide the player with a sword
            performance_tradeoffs=True,
            # Monster types are a,b,c, and d (ordered in increasing difficulty)
            monster_type_a="mobs_monster:sand_monster",
            monster_type_b="mobs_monster:spider",
            monster_type_c="mobs_monster:stone_monster",
            monster_type_d="mobs_monster:mese_monster",
            wall_material="default:steelblock",
            objective_item="default:diamond",  # item to serve as objective
            rwd_objective=10.0,  # Reward of collecting the objective item
            rwd_kill_monster=0.5,  # Reward of killing a monster
            ascii_map="""
#######
#######
#######
#######
########
#########
##########
     ######
       ############
        ###########
         ##########
         ##########
         ##########
         ##########
         ##########
         ##########
         ##########
-
#######
#     #
# b   #
#  O  #
#      #
#       #
#####    #
     ##   #
       #   ########
        #         #
         #        #
         #        #
         #    @   #
         #        #
         #        #
         #        #
         ##########
-
#######
#     #
#     #
#     #
#      #
#       #
#####    #
     ##   #
       #   ########
        #         #
         #        #
         #        #
         #        #
         #        #
         #        #
         #        #
         ##########
-
#######
#     #
#     #
#     #
#      #
#       #
#####    #
     ##   #
       #   ########
        #         #
         #        #
         #        #
         #        #
         #        #
         #        #
         #        #
         ##########
                    """.replace("\n", "\\n"),
        ),
        _voxel_obs_available=True,
    )
)
