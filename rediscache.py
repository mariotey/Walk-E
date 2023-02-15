import redis
import json

import gait_process
import gait_calibrate

redis_client = redis.Redis(host="localhost", port=6379)

#################################################################################################

def cache_lm(key, request_data):
    pose_lm = json.loads(request_data["poseLandmark"])
    world_lm = json.loads(request_data["worldLandmark"])
    time_lm = json.loads(request_data["time"])

    processed_gait = gait_process.get_lm(world_lm, time_lm)

    if key == "calibration_data":
        offset = gait_calibrate.calibrate(processed_gait)
        redis_client.hset(key, "offset", json.dumps(offset).encode("utf-8"))
    
    if key == "testjoint_data":
        redis_client.hset(key, "joints", json.dumps(processed_gait).encode("utf-8"))

def request_lm(key):
    if key == "calibration_data":
        data = json.loads(redis_client.hget(key, "offset").decode("utf-8"))
    
    if key == "testjoint_data":
        data = json.loads(redis_client.hget(key, "joints").decode("utf-8"))
    
    return data

#################################################################################################

def cache_hw(key, dictkey, dict_data):
    redis_client.hset(key, dictkey, json.dumps(dict_data).encode("utf-8"))

def request_hw(key, dictkey):
    try:
        data = json.loads(redis_client.hget(key, dictkey).decode("utf-8"))
    except:
        data = {
            "speed": "-",
            "dist": "-",
        }

    return data

#################################################################################################