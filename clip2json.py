import json
import numpy as np

f1 = open("/Users/acowe/Desktop/test_data/test_data_3D/ts.5.6.data.bin", mode="rb")
f2 = open("/Users/acowe/Desktop/test_data/test_data_3D/tessellation/voxelComponentIds.bin", mode="rb")
f3 = open("/Users/acowe/Desktop/test_data/test_data_3D/tessellation/voxelLayerIds.bin", mode="rb")
f4 = open("/Users/acowe/Desktop/test_data/test_data_3D/tessellation/voxelSiteIds.bin", mode="rb")
f5 = open("/Users/acowe/Desktop/test_data/test_data_3D/tessellation/siteComponentIds.bin", mode="rb")

data1 = f1.read()
data2 = f2.read()
data3 = f3.read()
data4 = f4.read()
data5 = f5.read()

raw_data = np.frombuffer(data1, dtype=np.float32) # read in data from bin file
voxelLayerIds = np.frombuffer(data3, dtype=np.int16)
voxelComponentIds = np.frombuffer(data2, dtype=np.int32)
voxelSiteIds = np.frombuffer(data4, dtype=np.int32)
siteCmptIds = np.frombuffer(data5,dtype=np.int32)

print(siteCmptIds, len(siteCmptIds))

temp_data_raw = raw_data[:6000000] # get temp data
OHs = raw_data[6000000:]

# From dims field of config file: 
# x,y,z dims of the data, assumed to be flattened such that the 1D index at (x,y,z) is x + y*XD + z*YD*XD
# if data is in order z + y*ZD + x*YD*ZD, then swap x and z dims

#temp_data_indices = np.fromfunction(lambda i : np.array([(i % 30000) % 100, (i % 30000) // 100, i // 30000], dtype=int), (6000000,))
temp_data = np.fromfunction(lambda x, y, z: temp_data_raw[(x + (100 * y) + (30000 * z)).astype(int)], (100, 300, 200), dtype=float)  # Assume XD = 100, YD = 300
OHs = np.fromfunction(lambda x, y, z: OHs[(x + (100 * y) + (30000 * z)).astype(int)], (100, 300, 200), dtype=float)  # Assume XD = 100, YD = 300
temp_data2 = np.fromfunction(lambda x, y, z: voxelLayerIds[(x + (100 * y) + (30000 * z)).astype(int)], (100, 300, 200), dtype=int)  # Assume XD = 100, YD = 300
temp_data3 = np.fromfunction(lambda x, y, z: voxelComponentIds[(x + (100 * y) + (30000 * z)).astype(int)], (100, 300, 200), dtype=int)  # Assume XD = 100, YD = 300
temp_data4 = np.fromfunction(lambda x, y, z: voxelSiteIds[(x + (100 * y) + (30000 * z)).astype(int)], (100, 300, 200), dtype=int)  # Assume XD = 100, YD = 300


# temp_data = np.reshape(temp_data_raw, (100, 300, 200)) 

clipping_selected = 45

first_clipping = temp_data[clipping_selected]
first_clipping = np.swapaxes(first_clipping , 0 , 1) # swap axes so y corresponds to X-axis on plot, z to Y-axis

OH_clipping = OHs[clipping_selected]
OH_clipping = np.swapaxes(OH_clipping , 0 , 1)

first_clipping2 = temp_data2[clipping_selected]
first_clipping2 = np.swapaxes(first_clipping2 , 0 , 1) # swap axes so y corresponds to X-axis on plot, z to Y-axis

first_clipping3 = temp_data3[clipping_selected]
first_clipping3 = np.swapaxes(first_clipping3 , 0 , 1)

first_clipping4 = temp_data4[clipping_selected]
first_clipping4 = np.swapaxes(first_clipping4 , 0 , 1)

#print(np.unique(first_clipping4))

first_clipping_flat = first_clipping.flatten().tolist()

OH_clipping_flat = OH_clipping.flatten().tolist()

first_clipping2_flat = first_clipping2.flatten().tolist()
first_clipping2_ids_flat = np.unique(first_clipping2_flat).tolist()

first_clipping3_flat = first_clipping3.flatten().tolist()
first_clipping3_ids_flat = np.unique(first_clipping3_flat).tolist()

first_clipping4_flat = first_clipping4.flatten().tolist()
first_clipping4_ids_flat = np.unique(first_clipping4_flat).tolist()




data = {
    "slice": clipping_selected,
    "OH_grid": OH_clipping_flat
    "vox_grid": first_clipping_flat, # vox_grid[][]
    "layer_grid": first_clipping2_flat, 
    "component_grid": first_clipping3_flat,
    "cell_grid": first_clipping4_flat,
    "vox_thresh": [11.0, 15.0, 18.0],
    "layer_thresh": first_clipping2_ids_flat,
    "component_thresh": first_clipping3_ids_flat,
    "cell_thresh": first_clipping4_ids_flat,
    "siteCmptIds": siteCmptIds.tolist()
}


json_str = json.dumps(data)

file_title = "temp_data_s" + str(clipping_selected) + ".json"
with open(file_title, "w") as outfile:
    outfile.write(json_str)

f1.close()
f2.close()
f3.close()
f4.close()
f5.close()



