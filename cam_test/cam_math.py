import numpy as np
import math
from sklearn.metrics import mean_squared_error as mse

MAX_ITR = 10

def cal_twoD_angle(first, sec, third):
    u = np.array([first["x"] - sec["x"], first["y"] - sec["y"]])
    v = np.array([third["x"] - sec["x"], third["y"] - sec["y"]])

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

def threePt_threeD_angle(first, sec, third):   
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
    result = np.abs(math.degrees(radians))

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

    return new_list

def poly_fit(x,y):
    def poly_func(x,y,dof):
        curve = np.polyfit(x, y, dof)
        poly = np.poly1d(curve)
        new_x = sorted(x)

        return new_x, list(poly(new_x)), poly
    
    msq_dof = []

    for dof_itera in range(1, MAX_ITR):
        try:
            msq = mse(y, poly_func(x,y,dof_itera)[1]) 
            msq_dof.append([msq, dof_itera])
        except:
            pass
        
    mse_dof = min(msq_dof, key=lambda x:x[0])[1]

    return poly_func(x,y,mse_dof)

def average_fit(poly_list, offset):
    x = [i for i in range(0, 101, 1)]
    y = []

    for coord in x:
        ys = []
        for poly in poly_list:
            ys.append(poly(coord) - offset)
        y.append(np.mean(ys))

    new_x, new_y, poly = poly_fit(x,y)

    return {"x": new_x, "y": new_y}

