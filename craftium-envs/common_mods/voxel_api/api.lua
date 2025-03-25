voxel_api = {}

-- Internal use only

DEBUG = false
DEBUG_PRINT_ONCE = DEBUG

local function print_array_from_pos(array, minp, maxp, vox_area)
	local str = ""
	for z = minp.z, maxp.z do
		for y = minp.y, maxp.y do
			local vi = vox_area:index(minp.x, y, z)
			for x = minp.x, maxp.x do
				str = str .. array[vi] .. " "
				vi = vi + 1 -- Note: equivalent to local vi = vox_area:index(x, y, z), but more efficient
			end
			str = str .. "\n"
		end
	end
	str = str .. "\n"
	print(str)
end

-- Global
function voxel_api:get_voxel_data(pos, radius)
	local vm = VoxelManip()  --vm = core.get_mapgen_object("voxelmanip")
	pos = vector.round(pos)
	local p1 = vector.subtract(pos, radius)
	local p2 = vector.add(pos, radius)

	local minp, maxp = vm:read_from_map(p1, p2)
	local vox_area = VoxelArea:new({MinEdge = minp, MaxEdge = maxp})
	local voxel_data = vm:get_data()
	local voxel_light_data = vm:get_light_data()
	local voxel_param2_data = vm:get_param2_data()

	if DEBUG then
		voxel_api:print_nodes_in_view(voxel_data)
		if DEBUG_PRINT_ONCE then
			print("\nVoxelManip::get_data() [3D]: \n")
			print_array_from_pos(voxel_data, p1, p2, vox_area)
			print("\nVoxelManip::get_light_data() [3D]: \n")
			print_array_from_pos(voxel_light_data, p1, p2, vox_area)
			print("\nVoxelManip::get_param2_data() [3D]: \n")
			print_array_from_pos(voxel_param2_data, p1, p2, vox_area)
			DEBUG_PRINT_ONCE = false
		end
	end

	local voxel_data_trunc = {}
	local voxel_light_data_trunc = {}
	local voxel_param2_data_trunc = {}
	local index = 1
	for z = p1.z, p2.z do
		for y = p1.y, p2.y do
			for x = p1.x, p2.x do
				local vi = vox_area:index(x, y, z)
				voxel_data_trunc[index] = voxel_data[vi]
				voxel_light_data_trunc[index] = voxel_light_data[vi]
				voxel_param2_data_trunc[index] = voxel_param2_data[vi]
				index = index + 1
			end
		end
	end
	return voxel_data_trunc, voxel_light_data_trunc, voxel_param2_data_trunc
end

function voxel_api:print_nodes_in_view(voxel_data)
	local node_ids_in_view = {}
	for i = 1, #voxel_data do
		local node_id = voxel_data[i]
		if node_ids_in_view[node_id] == nil then
			node_ids_in_view[node_id] = 1
		else
			node_ids_in_view[node_id] = node_ids_in_view[node_id] + 1
		end
	end
	for node_id, count in pairs(node_ids_in_view) do
		node_name = minetest.get_name_from_content_id(node_id)
		print("Node ID: " .. node_id .. " | Node Name: " .. node_name .. " | Count: " .. count)
	end
end

function voxel_api:print_3d_vector(vector, name)
	print(name .. " = (" .. tostring(vector.x) .. ", " .. tostring(vector.y) .. ", " .. tostring(vector.z) .. ")")
end
