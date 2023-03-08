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

def cache_hw(key, dict_data):
    redis_client.hset(key, "distance", json.dumps(dict_data["distance"]).encode("utf-8"))
    redis_client.hset(key, "speed", json.dumps(dict_data["speed"]).encode("utf-8"))

def request_hw(key):
    try:
        data = {
            "dist": json.loads(redis_client.hget(key, "distance").decode("utf-8")),
            "speed": json.loads(redis_client.hget(key, "speed").decode("utf-8"))
        }
    except:
        data = {"dist": "-", "speed": "-"}

    return data

#################################################################################################