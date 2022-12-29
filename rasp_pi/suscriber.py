import redis

redis_client = redis.Redis(host='192.168.1.69', port=6379, db=0)

print(redis_client.keys())
# subscribe_key="walkEStats"

# redis_data = redis_client.keys()

# while True:
#     if redis_client.get(subscribe_key).decode('utf-8') == "false":
#         pass
#     else:
#         break
    
print("Complete")
