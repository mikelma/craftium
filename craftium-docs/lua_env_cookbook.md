# Lua environment cookbook

This page is a collection of simple examples demonstrating how to accomplish several tasks from Lua mods implementing a Craftium environment. The code examples heavily use Luanti's Lua API, which is extensively documented in the [reference](https://api.luanti.org/).

For a complete guide on how to create custom Craftium environments visit the [tutorial](./creating-envs.md) and the [Luanti's modding book](https://rubenwardy.com/minetest_modding_book/en/basics/getting_started.html).

## Episode termination when the player dies

```lua
core.register_on_dieplayer(function(ObjectRef, reason)
      set_termination()
end)
```

## Hidding HUD elements

Check the [documentation](https://api.luanti.org/class-reference/#player-only-no-op-for-other-objects) for the complete list of valid flags for `hud_set_flags`.

```lua
core.register_on_joinplayer(function(player, _last_login)
      player:hud_set_flags({
            crosshair = false,
            basic_debug = false,
            chat = false,
      })
end)
```

## Setting the time of day when the episode starts

See Luanti's [time of day](https://wiki.luanti.org/Time_of_day) wiki page.

```lua
core.register_on_joinplayer(function(player, _last_login)
      -- Set time of day to midday
      core.set_timeofday(0.5)
end)
```

## Modifying player's inventory

Check [inventory](https://api.core.org/inventory/) page in the Luanti's API reference for all the available options and methods.

```lua
core.register_on_joinplayer(function(player, _last_login)
      -- Add 99 torches to the player's initial inventory
      local inv = player:get_inventory()
      for i=1, #init_tools do
         inv:add_item("main", "default:torch 64")
      end
end)
```

## Using env's random seed in Lua code

This example shows how to set the environment's random seed to the `seed` parameter specified in [`CraftiumEnv`](./reference.md) (or when constructing a registered Craftium environment using `gymnasium.make("Craftium/EnvName-vX", seed=42)`).

You should probably add this code snippet to the first lines of your `init.lua`.

```lua
-- Set the random seed
if core.settings:has("fixed_map_seed") then
   math.randomseed(core.settings:get("fixed_map_seed"))
end
```


## Get connected player's object

Check the [Player](https://api.luanti.org/class-reference/#player-only-no-op-for-other-objects) section in the Luanti's reference for more details.

```lua
local player = core.get_connected_players()[1]
if player == nil then
   return nil
end
```

or,

```lua
for _, player in pairs(core.get_connected_players()) do
   -- Do something with `player`
end
```

## Get the node (voxel) dug by the player

```lua
core.register_on_dignode(function(pos, node)
  -- Check if the name of the node contains "tree"
  if string.find(node["name"], "tree") then
     -- Do something
  end
end)
```

## Set player's initial position

```lua
core.register_on_joinplayer(function(player, _last_login)
      player:set_pos({x = x, y = y, z = z})
end)
```

Where `{x = x, y = y, z = z}` are Luanti world coordinates (see [Coordinates](https://wiki.luanti.org/Coordinates) in the wiki).
