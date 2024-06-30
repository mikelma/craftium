# Extensions to minetest's Lua API

Minetest has an extense and powerful Lua API (check docs [here](https://api.minetest.net/)) that can be used to modify the behavior of the game engine and create mods or entire games. Craftium extends this API to include several functions needed to create reinforcement learning environments (tutorial [here](./creating-envs.md)) such as the reward function and conditions for episode termination. The complete list of Lua functions added by craftium is provided below.

<br>
`set_reward(r: float)`: Sets the reward value to `r`. Note that the reward value is maintained for the following timesteps, until another call to a function that modifies the reward value is done.

<br>
`set_reward_once(r_now: float, r_after: float)`: Sets the reward to `r_now` for the current timestep, resetting it to `r_after` after (until a reward modification function is called).

<br>
`set_termination()`: Sets the termination flag to `True` in the current timestep.

<br>
`get_reward()`: Returns the value of the reward in the current timestep.

<br>
`get_termination()`: Returns `1.0` if the termination flag is set to `true` in the current timestep, otherwise `0.0`.
