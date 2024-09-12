import matplotlib.pyplot as plt
import gymnasium as gym
import craftium
from craftium.extra.random_map_generator import RandomMapGen

# Generate a random map using the random dungeon generator provided by craftium
mapgen = RandomMapGen(
        n_rooms=2,
        dispersion=0.4,
        room_min_size=5,
        room_max_size=10,
        max_monsters_per_room=3,
        monsters={"a": 0.4, "b": 0.3, "c": 0.2, "d": 0.1},
    )

ascii_map = mapgen.rasterize(wall_height=5)  # Convert map into string
# Show the intermediate layer of the map (where the player and mobs are placed)
print(ascii_map.split("-")[1])

# Set up environment's paramaters (these are all the relevant ones for this env.)
env_conf = dict(
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
    rwd_objective=1.0,  # Reward of collecting the objective item
    rwd_kill_monster=0.5,  # Reward of killing a monster
    ascii_map=ascii_map.replace("\n", "\\n"),
)

# Environment initialization
max_timesteps = 10_000
frameskip = 1
rgb_observations = True
env = gym.make(
    "Craftium/ProcDungeons-v0",
    # render_mode="human",
    frameskip=frameskip,
    rgb_observations=rgb_observations,
    minetest_conf=env_conf,
)

# Main loop
observation, info = env.reset()
ep_ret = 0
for t in range(max_timesteps//frameskip):
    action = env.action_space.sample()  # Random actions
    # action = 0  # NOP action

    plt.clf()
    if rgb_observations:
        plt.imshow(observation)
    else:
        plt.imshow(observation, cmap="gray")
    plt.pause(1e-2)

    observation, reward, terminated, truncated, _info = env.step(action)
    ep_ret += reward
    print(t, reward, ep_ret)

    if terminated or truncated:
        observation, info = env.reset()
        ep_ret = 0
env.close()
