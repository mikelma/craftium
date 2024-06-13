-- Modify the parameters in parameter.lua!

----------------------------
-- Text Parser for BLOCKS --
----------------------------

-- Minetest library
function string:split(sep)local sep,fields=sep or ",",{} local pattern=string.format("([^%s]+)", sep) self:gsub(pattern,function(c)fields[#fields+1]=c end) return fields end
function file_exists(filename)local f=io.open(filename, "r") if f==nil then return false else f:close() return true end end

function sflat.parsetext(text)
	if text:split(";")[2] ~= nil then
		local options = text:split(";")[2]:split(",")
		if options[1] ~= nil or options[1] ~= "" then
			sflat.options.biome = options[1]
			if options[2] == "decoration" then
				sflat.options.decoration = true
			end
		end
	end
	
	local text, layers = text:split(";")[1]:split(","), {}
	local y = sflat.Y_ORIGIN
	for a = 1, #text do
		local node, amount = string.match(text[a], "^([a-zA-Z0-9_:]+)=?([0-9]*)$")
		if node ~= nil and amount ~= nil then
			if amount == "" then amount = 1 end
			y = y + amount
			layers[#layers + 1] = {node, sflat.get_content_id(node), y}
		end
	end
	return layers
end
