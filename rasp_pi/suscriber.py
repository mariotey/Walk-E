import redis

redis_client = redis.Redis("localhost", port = 6379)
redis_p = redis_client.pubsub()
redis_p.subscribe("dev")


while True:
    message = redis_p.get_message()
    
    if message and not message['data'] == 1:
        message = message['data'].decode('utf-8')
        print(f'Received command: {message}')
