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

    # Projected Vector on Normal
    normal = np.array([1,0,0])
    norm_mag = np.linalg.norm(normal)
    u_norm_proj, v_norm_proj = (np.dot(u, normal)/norm_mag) * u, (np.dot(v, normal)/norm_mag) * v

    # Projected Vector on Sagittal Plane
    u_proj = u - u_norm_proj
    v_proj = v - v_norm_proj

    uv_project = np.dot(u_proj, v_proj)
    u_proj_mag, v_proj_mag = np.linalg.norm(u_proj), np.linalg.norm(v_proj)

    radians = np.arccos(uv_project/(u_proj_mag * v_proj_mag))
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

    # print(time_list[0], "to", time_list[-1], ":", new_list[0], "to", new_list[-1], "\n")
    
    return new_list

