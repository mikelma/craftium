function rand(lower, greater)
    return lower + math.random()  * (greater - lower);
end

-- Executed when the player joins the game
minetest.register_on_joinplayer(function(player, _last_login)
      -- Place the player in a random position inside the rooom
      player:set_pos({x = rand(-13.2, 4.2), z = rand(-24.2, -10,0), y = 6 })

      --- Spawn a red block inside the room in a random position
      target_pos = {x = rand(-13.2, 4.2), z = rand(-9.0, -0.8), y = 5.5 }
      minetest.set_node(target_pos, { name = "default:coral_orange" })

      -- Disable HUD elements
      player:hud_set_flags({
            hotbar = false,
            crosshair = false,
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

      local player_pos = player:get_pos()

      distance = math.pow(target_pos.x-player_pos.x, 2) +
         math.pow(target_pos.z-player_pos.z, 2)

      set_reward(0.1*(1-(distance/850.32)))

      if distance < 2.0 then
         set_reward(100.0)
         set_termination()
      end
end)
