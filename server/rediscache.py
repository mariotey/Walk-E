import redis
import json

redis_client = redis.Redis(host="localhost", port=6379)

def cache_lm(key, request_data):
    redis_client.hset(key, "pose_lm", request_data["poseLandmark"])
    redis_client.hset(key, "world_lm", request_data["worldLandmark"])
    redis_client.hset(key, "time", request_data["time"])

def request_lm(key):
    world_lm = json.loads(redis_client.hget(key, "world_lm").decode("utf-8"))
    time = json.loads(redis_client.hget(key, "time").decode("utf-8"))

    return world_lm, time