import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)

subscribe_key="walkEStats"

print(redis_client.get(subscribe_key).decode('utf-8'))

while True:
    if redis_client.get(subscribe_key).decode('utf-8') == "false":
        pass
    else:
        break
    
print("Complete")
