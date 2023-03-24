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

        # Ground Configuration
        # data["hipflex"] += 50
        # data["kneeflex"] += -70
        # data["ankleflex"] += 3
        # data["shoulder"] += 2
        # data["hip"] += -0.5

        # Stand Configuration
        # data["hipflex"] += 30
        # data["kneeflex"] += -20
        # data["ankleflex"] += 110
        # data["shoulder"] += -2.8
        # data["hip"] += 0

        # Video Configuration
        data["hipflex"] += 0
        data["kneeflex"] += 0
        data["ankleflex"] += 0
        data["shoulder"] += 0
        data["hip"] += 0
    
    if key == "testjoint_data":
        data = json.loads(redis_client.hget(key, "joints").decode("utf-8"))
    
    return data

#################################################################################################

def cache_encode(key, encoder_list):
    
    encoder_list.pop(0)

    def cache_data(count_key, dict_name):
        
        processed_encoder = {
            "count": [data[count_key] for data in encoder_list],
            "dist_status": [data["dist_status"] for data in encoder_list],
            "time": [data["time"] for data in encoder_list]
        }
        
        redis_client.hset(key, dict_name, json.dumps(processed_encoder).encode("utf-8"))

    cache_data("count_one", "encoder_one")
    cache_data("count_two", "encoder_two")

def request_encode(key):
    try:
        return {
            "encoder_one": json.loads(redis_client.hget(key, "encoder_one").decode("utf-8")),
            "encoder_two": json.loads(redis_client.hget(key, "encoder_two").decode("utf-8"))
        }
    except:
        return ""

#################################################################################################

def cache_proxy(key, hiplen_list):
    result = {
        "hiplen": [data["hiplen"] for data in hiplen_list],
        "time": [data["time"] for data in hiplen_list]
    }

    redis_client.hset(key, "proxy", json.dumps(result).encode("utf-8"))

def request_proxy(key):
    data = json.loads(redis_client.hget(key, "proxy").decode("utf-8"))

    return data