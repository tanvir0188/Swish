# test_redis.py
import redis
import asyncio
from channels_redis.core import RedisChannelLayer

# Test basic Redis connection
r = redis.Redis(host='localhost', port=6380, decode_responses=True)
print("Redis ping:", r.ping())

# Test the specific command
try:
    result = r.execute_command('BZPOPMIN', 'test_key', '1')
    print("BZPOPMIN works:", result)
except Exception as e:
    print("BZPOPMIN error:", e)

# Test channels-redis
async def test_channels_redis():
    channel_layer = RedisChannelLayer(hosts=[("127.0.0.1", 6380)])
    try:
        await channel_layer.group_add("test_group", "test_channel")
        print("Channels Redis works!")
    except Exception as e:
        print("Channels Redis error:", e)

# Run the async test
asyncio.run(test_channels_redis())