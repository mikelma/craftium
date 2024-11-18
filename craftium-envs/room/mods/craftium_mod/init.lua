-- Set the random seed
if minetest.settings:has("fixed_map_seed") then
   math.randomseed(minetest.settings:get("fixed_map_seed"))
end

function rand(lower, greater)
    return lower + math.random()  * (greater - lower);
end

reset_environment = function()
   local player = minetest.get_connected_players()[1]
   -- Room environment:
   --
   -- ________< (x=4.2, z=-0.8)
   -- | b    |
   -- |_ _ _ |  --> Box spawn area
   -- |      |  --> Agent's spawn area
   -- |  a   |
   -- |______|< (x=4.2, z=-24.2)
   -- ^(z=-13.2, z=-24.2)

   -- Place the player in a random position inside the rooom
   player:set_pos({x = rand(-13.2, 4.2), z = rand(-15.2, -10.0), y = 6 })

   -- Remove the previously spawned block (if any)
   if target_pos ~= nil then
      minetest.remove_node(target_pos)
   end

   --- Spawn a red block inside the room in a random position
   target_pos = {x = rand(-13.2, 4.2), z = rand(-9.0, -0.8), y = 5.5 }

   minetest.set_node(target_pos, { name = "default:coral_orange" })

   -- Disable HUD elements
   player:hud_set_flags({
         hotbar = false,
         crosshair = false,
         healthbar = false,
   })
end

-- Executed when the player joins the game
minetest.register_on_joinplayer(function(player, _last_login)
      reset_environment()
end)

minetest.register_globalstep(function(dtime)
      -- set timeofday to midday
      minetest.set_timeofday(0.5)

      -- get the first connected player
      local player = minetest.get_connected_players()[1]

      -- if the player is not connected end here
      if player == nil then
         return nil
      end

      -- Reset the environment if requested by the python interface
      if get_soft_reset() == 1 then
         reset_environment()
         reset_termination()
      end

      -- if the player is connected:

      -- get the position of the player and compute its
      -- distance to he target
      local player_pos = player:get_pos()

      local distance = math.pow(target_pos.x-player_pos.x, 2) +
         math.pow(target_pos.z-player_pos.z, 2)

      -- the reward at each timestep is -1
      set_reward(-1.0)

      -- terminate the episode if the distance to the target is
      -- less than a threshold
      if distance < 5.0 then
         set_termination()
      end
end)
