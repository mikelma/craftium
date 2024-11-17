local channel = minetest.mod_channel_join("craftium_channel")

num_players = 0

reset_player = function(player)
   -- Set the name tag color to transparent
   player:set_nametag_attributes({color = {a = 0, r = 0, g = 0, b = 0}})

   player:set_hp(20, {type = "set_hp", from = "mod" })

   -- Set the player's initial position and yaw
   if player:get_player_name() == "agent0" then
      player:set_pos({x = -2.5, y = 4.5, z = -1.7})
      player:set_look_horizontal(3.1416)
   else
      player:set_pos({x = -2.5, y = 4.5, z = -8.5})
      player:set_look_horizontal(0)
   end

   -- Disable HUD elements
   player:hud_set_flags({
         hotbar = false,
         crosshair = false,
         healthbar = false,
         chat = false,
   })
end

minetest.register_on_joinplayer(function(player, _last_login)
    num_players = num_players + 1
    reset_player(player)
end)

minetest.register_globalstep(function(dtime)
      -- Set timeofday to midday
      minetest.set_timeofday(0.5)
end)

minetest.register_on_modchannel_message(function(channel, sender, str_message)
      if channel ~= "craftium_channel" then
         return
      end

      local msg = minetest.deserialize(str_message)

      if msg.agent ~= "server" then
         return
      end

      if msg.reset == true then
         for _, player in pairs(minetest.get_connected_players()) do
            reset_player(player)
         end
      end
end)

minetest.register_on_punchplayer(function(player, hitter, time_from_last_punch, tool_capabilities, dir, damage)
      -- Get the names of both players involved
      local player_name = player:get_player_name()
      -- local hitter_name = hitter:get_player_name()

      -- NOTE The player's health is updated after this callback, so the real hp will be get_hp()-1
      channel:send_all(
         minetest.serialize({
               agent = hitter:get_player_name(),
               termination = (player:get_hp() - 1) <= 5
         })
      )
end)
