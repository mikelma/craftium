-- Set the random seed
seed = minetest.settings:get("fixed_map_seed")
if seed ~= nil then
   math.randomseed(seed)
end

function rand(lower, greater)
    return lower + math.random()  * (greater - lower);
end

SIZE = 10 -- size of the room in blocks
FLOOR = 4.5

-- Executed when the player joins the game
minetest.register_on_joinplayer(function(player, _last_login)
      -- Set the players initial position
      player:set_pos({x = SIZE / 2, z = 1, y = FLOOR + 1})

      -- Place the player in a random position inside the rooom
      --
      -- --- Spawn a red block inside the room in a random position
      target_pos = {x = rand(1, SIZE-1), z = rand(5, SIZE-1), y = 5.5 }
      minetest.set_node(target_pos, { name = "default:coral_orange" })

      -- Disable HUD elements
      player:hud_set_flags({
            hotbar = false,
            crosshair = false,
            healthbar = false,
      })
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

      -- if the player is connected:

      -- get the position of the player and compute its
      -- distance to he target
      local player_pos = player:get_pos()

      distance = math.pow(target_pos.x-player_pos.x, 2) +
         math.pow(target_pos.z-player_pos.z, 2)

      -- the reward at each timestep is -1
      set_reward(-1.0)

      -- terminate the episode if the distance to the target is
      -- less than a threshold
      if distance < 5.0 then
         set_termination()
      end
end)
