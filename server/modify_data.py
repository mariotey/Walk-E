import mediapipe as mp
import numpy as np
import dictkeys
import redis
import json

mp_pose = mp.solutions.pose

redis_client = redis.Redis(host="localhost", port=6379)

def request_lm(world_lm, time):
    new_data = {item: [] for item in dictkeys.gait_list}

    ref_time = time[0]
    
    for idx, images in enumerate(world_lm):
        new_data["ref_heel"].append(images[mp_pose.PoseLandmark["LEFT_HEEL"].value])
        new_data["left_shoulder"].append(images[mp_pose.PoseLandmark["LEFT_SHOULDER"].value])
        new_data["right_shoulder"].append(images[mp_pose.PoseLandmark["RIGHT_SHOULDER"].value])
        new_data["left_hip"].append(images[mp_pose.PoseLandmark["LEFT_HIP"].value])
        new_data["right_hip"].append(images[mp_pose.PoseLandmark["RIGHT_HIP"].value])
        new_data["knee"].append(images[mp_pose.PoseLandmark["LEFT_KNEE"].value])
        new_data["ankle"].append(images[mp_pose.PoseLandmark["LEFT_ANKLE"].value])
        new_data["toe"].append(images[mp_pose.PoseLandmark["LEFT_FOOT_INDEX"].value])
        new_data["time"].append(time[idx] - ref_time)
    
    return new_data

def add_points(joint_data, unit_space):
    new_jointdata = {item: [] for item in dictkeys.gait_list}

    # For each component of joint_data
    for bodykey in joint_data:
        if bodykey == "time":
            for index in range(len(joint_data["ref_heel"])-1):
                new_time = list(np.linspace(joint_data[bodykey][index],
                                       joint_data[bodykey][index+1],
                                       num=unit_space))

                new_jointdata["time"] += new_time
        else:
            # For each data set of a component of joint_data
            for index in range(len(joint_data[bodykey])-1):
                # Create a new list of x,y and z_coord
                new_x = list(np.linspace(joint_data[bodykey][index]["x"],
                                    joint_data[bodykey][index+1]["x"],
                                    num=unit_space))

                new_y = list(np.linspace(joint_data[bodykey][index]["y"],
                                    joint_data[bodykey][index+1]["y"],
                                    num=unit_space))

                new_z = list(np.linspace(joint_data[bodykey][index]["z"],
                                    joint_data[bodykey][index+1]["z"],
                                    num=unit_space))

                # Append the new x,y and z_coord into new_join_data              
                for index in range(len(new_x)):
                    new_jointdata[bodykey].append({"x": new_x[index],
                                                    "y": new_y[index],
                                                    "z": new_z[index]})
    
    return new_jointdata

def cache_lm(key, request_data):
    redis_client.hset(key, "pose_lm", request_data["poseLandmark"])
    redis_client.hset(key, "world_lm", request_data["worldLandmark"])
    redis_client.hset(key, "time", request_data["time"])

def get_lm(key):
    world_lm = json.loads(redis_client.hget(key, "world_lm").decode("utf-8"))
    time = json.loads(redis_client.hget(key, "time").decode("utf-8"))

    return world_lm, time