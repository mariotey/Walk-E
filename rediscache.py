import redis
import json

redis_client = redis.Redis(host="localhost", port=6379)

def cache_lm(key, request_data):
    redis_client.hset(key, "pose_lm", request_data["poseLandmark"])
    redis_client.hset(key, "world_lm", request_data["worldLandmark"])
    redis_client.hset(key, "time", request_data["time"])

def cache_hw(key, dictkey, dict_data):
    redis_client.hset(key, dictkey, json.dumps(dict_data).encode("utf-8"))

def request_lm(key):
    world_lm = json.loads(redis_client.hget(key, "world_lm").decode("utf-8"))
    time = json.loads(redis_client.hget(key, "time").decode("utf-8"))

    return world_lm, time

def request_hw(key, dictkey):
    try:
        data = json.loads(redis_client.hget(key, dictkey).decode("utf-8"))
    except:
        data = {
            "speed": "-",
            "dist": "-",
        }

    return data