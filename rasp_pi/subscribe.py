import redis
import json

redis_client = redis.Redis(host="192.168.1.69", port=5000)

cachedata = redis_client.hget("testjoint_data", "time")

print("complete")
