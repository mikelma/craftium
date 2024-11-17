channel_name = "craftium_channel"
mod_channel = nil

minetest.register_globalstep(function(dtime)
      -- If soft-reset is requested by craftium, thoen send a message to
      -- the server to reset the environment
      if get_soft_reset() == 1 and mod_channel ~= nil then
         mod_channel:send_all(
            minetest.serialize({
                  agent = "server",
                  reset = true,
            })
         )
         reset_termination()
      end
end)

-- Function to check if the client has fully loaded
wait_for_client_ready = function()
    if minetest.localplayer then
        -- Client has joined the server and is fully loaded
        callback()
    else
        -- Retry after a short delay if not yet fully initialized
        minetest.after(0.01, function() wait_for_client_ready() end)
    end
end

-- Callback executed once the client is fully initialized
callback = function()
    -- Join the mod channel and set up listeners here
    mod_channel = minetest.mod_channel_join(channel_name)

    minetest.register_on_modchannel_message(function(channel, sender, str_message)
          if channel ~= channel_name then
             return
          end

          local msg = minetest.deserialize(str_message)

          if msg.agent == "server" then
             return
          end

          if msg.agent == minetest.localplayer:get_name() then
             set_reward_once(1.0, 0.0)
          else
             set_reward_once(-0.1, 0.0)
          end

          if msg.termination == true then
             set_termination()
          end
    end)
end

wait_for_client_ready()
