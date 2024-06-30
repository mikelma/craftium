-- Executed when the player joins the game
minetest.register_on_joinplayer(function(player, _last_login)
      -- Set the players initial position
      player:set_pos({x = 24.3, y = 5.5, z=-36.3})

      -- Disable HUD elements
      player:hud_set_flags({
            hotbar = false,
            crosshair = false,
            healthbar = false,
      })
end)

minetest.register_globalstep(function(dtime)
      -- get the first connected player
      local player = minetest.get_connected_players()[1]

      -- if the player is not connected end here
      if player == nil then
         return nil
      end

      -- if the player is connected:

      -- get the position of the player
      local player_pos = player:get_pos()

      -- set the reward to the inverse of the player's
      -- position on the Y axis (depth)
      set_reward(-player_pos.y)
end)

minetest.register_on_dieplayer(function(_player, _reason)
      -- End episode if the player dies
      set_termination()
end)
