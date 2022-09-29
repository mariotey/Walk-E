import numpy as np

def cal_twoD_angle(first, sec, third):
    u = np.array([first[0] - sec[0], first[1] - sec[1]])
    v = np.array([third[0] - sec[0], third[1] - sec[1]])

    uv = np.dot(u,v)
    mag_u, mag_v = np.linalg.norm(u), np.linalg.norm(v)

    radians = np.arccos(uv/(mag_u * mag_v))
    result = np.abs(radians * 180.0/np.pi)
 
    if result > 180.0:
        result = 360 - result

    return result

def cal_threeD_angle(first, sec, third):   
    u = np.array([first["x"] - sec["x"], first["y"] - sec["y"], first["z"] - sec["z"]])
    v = np.array([third["x"] - sec["x"], third["y"] - sec["y"], third["z"] - sec["z"]])

    uv = np.dot(u,v)
    mag_u, mag_v = np.linalg.norm(u), np.linalg.norm(v)

    radians = np.arccos(uv/(mag_u * mag_v))
    result = np.abs(radians * 180.0/np.pi)

    if result > 180.0:
        result = 360 - result

    return result

def cal_twoD_dist(first, sec):
    result = result = np.sqrt(((first[0] - sec[0])**2 + (first[1] - sec[1])**2))
    return result

def cal_threeD_dist(first, sec):
    result = np.sqrt(((first[0] - sec[0])**2 + (first[1] - sec[1])**2 + (first[0] - sec[0])**2))
    return result

def normalize_gait(time_list):
    new_list = []

    min_time = min(time_list)
    max_time = max(time_list)
    
    for elem in time_list:
        gait_value = (elem - min_time)/(max_time - min_time) * 100
        new_list.append(gait_value)

    print(new_list[0], new_list[-1])
    
    return new_list

# Equation of Sagittal Plane: 10x = 0
# Find the projection of vector onto normal vector (11, 0 ,0); Coefficients of the plane
# Projected vector = Vector - Normal Vector