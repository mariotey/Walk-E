import numpy as np

def cal_twoD_angle(first, sec, third):
    vector_u = [first[0] - sec[0], first[1] - sec[1]]
    vector_v = [third[0] - sec[0], third[1] - sec[1]]

    u_v = vector_u[0] * vector_v[0] + vector_u[1] * vector_v[1]

    mag_u = np.sqrt(vector_u[0]**2 + vector_u[1]**2)
    mag_v = np.sqrt(vector_v[0]**2 + vector_v[1]**2)

    radians = np.arccos(u_v/(mag_u * mag_v))
    result = np.abs(radians * 180.0/np.pi)
 
    if result > 180.0:
        result = 360 - result

    return result

def cal_threeD_angle(first, sec, third):
    vector_u = [first[0] - sec[0], first[1] - sec[1], first[2] - sec[2]]
    vector_v = [third[0] - sec[0], third[1] - sec[1], third[2] - sec[2]]

    u_v = vector_u[0] * vector_v[0] + vector_u[1] * vector_v[1] + vector_u[2] * vector_v[2]

    mag_u = np.sqrt(vector_u[0]**2 + vector_u[1]**2 + vector_u[2]**2)
    mag_v = np.sqrt(vector_v[0]**2 + vector_v[1]**2 + vector_v[2]**2)

    radians = np.arccos(u_v/(mag_u * mag_v))
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