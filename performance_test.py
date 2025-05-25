import time
from craftium import CraftiumEnv


#env_dirs =["./craftium-envs/voxel-libre2_noinfo","./craftium-envs/chop-tree","./craftium-envs/small-room"]
env_dirs =["./craftium-envs/voxel-libre2","./craftium-envs/chop-tree_info","./craftium-envs/small-room_info"]

steps = 5000
iters = 10

for env_dir in env_dirs:
    avg_time = 0
    print("\n\ntesting ",env_dir)
    for iter in range(iters):
        print(iter)
        total_time = 0.0
        env = CraftiumEnv(
            env_dir=env_dir,
            #render_mode="human",
            obs_width=512,
            obs_height=512,
            minetest_dir="/home/enebas/Documents/tfg/craftium_eneko/craftium",
            frameskip = 4,
            fps_max = 1000,
            # sync_mode=True,
            # pipe_proc=False,
        )

        
        from craftium.wrappers import DiscreteActionWrapper
        #only allows for one action
        env = DiscreteActionWrapper(
            env,
            actions=["forward", "left", "right", "backward"],
            mouse_mov=0.5,
        )

        observation, info = env.reset()

        start = time.time()
        for step in range(steps):
            action = env.action_space.sample()
            observation, reward, terminated, truncated, info = env.step(action)
            
            if terminated or truncated:
                print("reset")
                end = time.time()
                total_time+=end-start
                observation, info = env.reset()
                start=time.time()
        end = time.time()
        total_time+=end-start
        print(total_time)
        env.close()
        avg_time+=total_time
    avg_time/=iters
    print("average time of env ",env_dir," : ", avg_time, "\niters : ", iters, "\nsteps : ", steps, "\nsteps/second : ",steps/avg_time)
