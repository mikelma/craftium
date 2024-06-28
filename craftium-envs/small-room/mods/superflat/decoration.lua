-- Modify the parameters in parameter.lua!

-- Decoration engine
sflat = sflat or {}
sflat.biome = sflat.biome or {}
sflat.biome.list = {}
function sflat.biome.register(param)
	sflat.biome.list[param.name] = {
		decoration = param.decoration or false
	}
end

sflat.decoration = sflat.decoration or {}
sflat.decoration.list = {}

local c_air = minetest.get_content_id("air")
local c_ignore = minetest.get_content_id("ignore")

function sflat.decoration.generate(minp, maxp, LAYERS, data, area, seed, pr)
	local biome = sflat.biome.list[sflat.options.biome]
	local dcr = biome.decoration
	for i = 1, #dcr do
		local dcri = sflat.decoration.list[dcr[i][1]] or sflat.decoration.list["nil"]
		if LAYERS[#LAYERS][1] == dcri.grows_on then
			for z = minp.z, maxp.z do
			for x = minp.x, maxp.x do
				local vi = area:index(x, LAYERS[#LAYERS][3], z)
				local chance = dcr[i][2] or 1024
				if pr:next(1, chance) == 1 and data[vi] == c_air then
					sflat.decoration.list[dcr[i][1]].grow(
						{x = x, y = LAYERS[#LAYERS][3], z = z},
						data, area, seed,
						minp, maxp, pr
					)
				end
			end
			end
		end
	end
end

function sflat.decoration.register(param)
	sflat.decoration.list[param.name] = {
		chance = param.chance or 1024,
		grows_on = param.grows_on or "air",
		grow = param.grow or function() return nil end
	}
end

---------------------
-- Decoration Data --
---------------------

-- Biome definition (from cold to hot)

sflat.biome.register({
	name = ""
})
sflat.biome.register({
	name = "Frozen River"
})
sflat.biome.register({
	name = "River"
})

-- cold
sflat.biome.register({
	name = "Ice Plains"
})
sflat.biome.register({
	name = "Ice Plains Spikes",
	decoration = {{"ice_spike", 40}}
})

-- medium/lush
sflat.biome.register({
	name = "Flower Plains",
	decoration = {{"flowers", 20}, {"grass14", 80}}
})
sflat.biome.register({
	name = "Plains",
	decoration = {{"grass14", 40}, {"grass35", 15}, {"papyrus", 40}, {"flowers", 25}}
})
sflat.biome.register({
	name = "Forest",
	decoration = {{"normal", 29}, {"grass14", 70}, {"grass35", 15}, {"papyrus", 26}, {"flowers", 28}}
})
sflat.biome.register({
	name = "Jungle",
	decoration = {{"jungle", 21}, {"jungle_grass", 10}, {"papyrus", 25}, {"flowers", 25}}
})

-- hot
sflat.biome.register({
	name = "Desert",
	decoration = {{"cactus", 60}, {"dry_shrub", 60}}
})

-- Decoration definition

local c_dirt_grass = sflat.get_content_id("default:dirt_with_grass")
local c_tree = sflat.get_content_id("default:tree")
local c_leaves = sflat.get_content_id("default:leaves")
local c_apple = sflat.get_content_id("default:apple")
local c_jungletree = sflat.get_content_id("default:jungletree")
local c_jungleleaves = sflat.get_content_id("default:jungleleaves")
local c_snow = sflat.get_content_id("default:snow")

-- leaves
local function add_leaves(data, vi, c_leaf, other)
	local other = other or c_leaf
	if data[vi] == c_air or data[vi] == c_ignore or data[vi] == other then
		data[vi] = c_leaf
	end
end

-- normal tree
function sflat.decoration.normal_tree(pos, data, area, seed, minp, maxp, pr)
	local x, y, z = pos.x, pos.y, pos.z
	local is_apple_tree = false
	if pr:next(1, 100) < 25 then
		is_apple_tree = true
	end
	local th = pr:next(4, 5)
	
	for yy = y, y + th do
		local vi = area:index(x, yy, z)
		data[vi] = c_tree
	end
	
	local y = y + th - 1
	
	for xx = x - 1, x + 1 do
	for yy = y - 1, y + 1 do
	for zz = z - 1, z + 1 do
		if area:contains(xx, yy, zz) then
			local vi = area:index(xx, yy, zz)
			if pr:next(1, 100) > 25 then
				add_leaves(data, vi, c_leaves)
			else
				if is_apple_tree == true then
					add_leaves(data, vi, c_apple)
				else
					add_leaves(data, vi, c_leaves)
				end
			end
		end
	end
	end
	end
	
	for ii = 1, 8 do
		local xx = x + pr:next(-2, 2)
		local yy = y + pr:next(-1, 2)
		local zz = z + pr:next(-2, 2)
		for xxx = 0, 1 do
		for yyy = 0, 1 do
		for zzz = 0, 1 do
			if area:contains(xx + xxx, yy + yyy, zz + zzz) then
				local vi = area:index(xx + xxx, yy + yyy, zz + zzz)
				add_leaves(data, vi, c_leaves, c_leaves)
			end
		end
		end
		end
	end
end
sflat.decoration.register({
	name = "normal",
	chance = 15,
	grows_on = "default:dirt_with_grass",
	grow = function(pos, data, area, seed, minp, maxp, pr)
		sflat.decoration.normal_tree(pos, data, area, seed, minp, maxp, pr)
	end
})

-- jungle tree
function sflat.decoration.jungle_tree(pos, data, area, seed, minp, maxp, pr)
	local x, y, z = pos.x, pos.y, pos.z
	local th = pr:next(8, 12)
	
	for zz = z - 1, z + 1, maxp.z do
	for xx = x - 1, x + 1, maxp.x do
		if pr:next(1, 3) >= 2 and area:contains(xx, y, zz) then
			local vi = area:index(xx, y, zz)
			add_leaves(data, vi, c_jungletree)
		end
	end
	end
	
	for yy = y, y + th do
		local vi = area:index(x, yy, z)
		data[vi] = c_jungletree
	end
	
	local y = y + th - 1
	
	for xx = x - 1, x + 1 do
	for yy = y - 1, y + 1 do
	for zz = z - 1, z + 1 do
		if area:contains(xx, yy, zz) then
			local vi = area:index(xx, yy, zz)
			add_leaves(data, vi, c_jungleleaves)
		end
	end
	end
	end
	
	for ii = 1, 30 do
		local xx = x + pr:next(-3, 3)
		local yy = y + pr:next(-2, 2)
		local zz = z + pr:next(-3, 3)
		for xxx = 0, 1 do
		for yyy = 0, 1 do
		for zzz = 0, 1 do
			if area:contains(xx + xxx, yy + yyy, zz + zzz) then
				local vi = area:index(xx + xxx, yy + yyy, zz + zzz)
				add_leaves(data, vi, c_jungleleaves, c_jungleleaves)
			end
		end
		end
		end
	end
end
sflat.decoration.register({
	name = "jungle",
	chance = 10,
	grows_on = "default:dirt_with_grass",
	grow = function(pos, data, area, seed, minp, maxp, pr)
		sflat.decoration.jungle_tree(pos, data, area, seed, minp, maxp, pr)
	end
})

-- small plants

local c_cactus = sflat.get_content_id("default:cactus")
local c_dry_shrub = sflat.get_content_id("default:dry_shrub")
local c_papyrus = sflat.get_content_id("default:papyrus")
local c_junglegrass  = sflat.get_content_id("default:junglegrass")
local c_grass_1 = sflat.get_content_id("default:grass_1")
local c_grass_2 = sflat.get_content_id("default:grass_2")
local c_grass_3 = sflat.get_content_id("default:grass_3")
local c_grass_4 = sflat.get_content_id("default:grass_4")
local c_grass_5 = sflat.get_content_id("default:grass_5")
local c_grasses = {c_grass_1, c_grass_2, c_grass_3, c_grass_4, c_grass_5}

-- dry shrub
sflat.decoration.register({
	name = "dry_shrub",
	chance = 50,
	grows_on = "default:sand",
	grow = function(pos, data, area, seed, minp, maxp, pr)
		local x, y, z = pos.x, pos.y, pos.z
		local vi = area:index(x, y, z)
		if data[vi] == c_air or data[vi] == c_ignore then
			data[vi] = c_dry_shrub
		end
	end
})

-- cactus
sflat.decoration.register({
	name = "cactus",
	chance = 50,
	grows_on = "default:desert_sand",
	grow = function(pos, data, area, seed, minp, maxp, pr)
		local x, y, z = pos.x, pos.y, pos.z
		for yy = math.max(y, minp.y), math.min(y + pr:next(1, 4), maxp.y) do
			data[area:index(x, yy, z)] = c_cactus
		end
	end
})

-- papyrus
sflat.decoration.register({
	name = "papyrus",
	chance = 10,
	grows_on = "default:dirt_with_grass",
	grow = function(pos, data, area, seed, minp, maxp, pr)
		local x, y, z = pos.x, pos.y, pos.z
		for yy = math.max(y, minp.y), math.min(y + pr:next(2, 4), maxp.y) do
			data[area:index(x, yy, z)] = c_papyrus
		end
	end
})

-- jungle grass
sflat.decoration.register({
	name = "jungle_grass",
	chance = 25,
	grows_on = "default:dirt_with_grass",
	grow = function(pos, data, area, seed, minp, maxp, pr)
		local x, y, z = pos.x, pos.y, pos.z
		local vi = area:index(x, y, z)
		if data[vi] == c_air or data[vi] == c_ignore then
			data[vi] = c_junglegrass
		end
	end
})

-- grass 1-4
sflat.decoration.register({
	name = "grass14",
	chance = 60,
	grows_on = "default:dirt_with_grass",
	grow = function(pos, data, area, seed, minp, maxp, pr)
		local x, y, z = pos.x, pos.y, pos.z
		local vi = area:index(x, y, z)
		if data[vi] == c_air or data[vi] == c_ignore then
			data[vi] = c_grasses[pr:next(1, 4)]
		end
	end
})

-- grass 3-5
sflat.decoration.register({
	name = "grass35",
	chance = 5,
	grows_on = "default:dirt_with_grass",
	grow = function(pos, data, area, seed, minp, maxp, pr)
		local x, y, z = pos.x, pos.y, pos.z
		local vi = area:index(x, y, z)
		if data[vi] == c_air or data[vi] == c_ignore then
			data[vi] = c_grasses[pr:next(3, 5)]
		end
	end
})


local c_chrysanthemum_green = sflat.get_content_id("flowers:chrysanthemum_green")
local c_dandelion_white = sflat.get_content_id("flowers:dandelion_white")
local c_dandelion_yellow = sflat.get_content_id("flowers:dandelion_yellow")
local c_geranium = sflat.get_content_id("flowers:geranium")
local c_rose = sflat.get_content_id("flowers:rose")
local c_tulip = sflat.get_content_id("flowers:tulip")
local c_tulip_black = sflat.get_content_id("flowers:tulip_black")
local c_viola = sflat.get_content_id("flowers:viola")
local c_flowers = {
	c_chrysanthemum_green, c_dandelion_white, c_dandelion_yellow, c_geranium,
	c_rose, c_tulip, c_tulip_black, c_viola, c_flowers
}

-- flowers
sflat.decoration.register({
	name = "flowers",
	chance = 3,
	grows_on = "default:dirt_with_grass",
	grow = function(pos, data, area, seed, minp, maxp, pr)
		local x, y, z = pos.x, pos.y, pos.z
		local vi = area:index(x, y, z)
		if data[vi] == c_air or data[vi] == c_ignore then
			data[vi] = c_flowers[pr:next(1, 6)]
		end
	end
})

local c_ice = sflat.get_content_id("default:ice")

-- ice spikes
sflat.decoration.register({
	name = "ice_spike",
	chance = 25,
	grows_on = "default:dirt_with_snow",
	grow = function(pos, data, area, seed, minp, maxp, pr)
		local x, y, z = pos.x, pos.y, pos.z
		local vi = area:index(x, y, z)
		if data[vi] == c_air or data[vi] == c_ignore then
			local h = pr:next(4,7)
			for u = -1, 1 do
			for i = -1, 1 do
			local vi = area:index(x + u, y - 1, z + i)
			if data[vi] ~= c_air or data[vi] ~= c_ignore then
				for o = 0, h do
					local vi = area:index(x + u, y + o, z + i)
					data[vi] = c_ice
				end
			end
			end
			end
			j = h + pr:next(2, 3)
			for u = 0, 1 do
			for i = -1, 0 do
			local vi = area:index(x + u, y - 1, z + i)
			if data[vi] ~= c_air or data[vi] ~= c_ignore then
				for o = h, j do
					local vi = area:index(x + u, y + o, z + i)
					data[vi] = c_ice
				end
			end
			end
			end
			local vi = area:index(x, y + j, z)
			data[vi] = c_ice
		end
	end
})
