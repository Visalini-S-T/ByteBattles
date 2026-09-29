from functools import cache
from redis import Redis
from config import REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_JOB_LIST

redis_client = Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

@cache
def get_redis_client():
    return Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        decode_responses=True,
    )

def enqueue_job(submission_id: int):
    get_redis_client().lpush(REDIS_JOB_LIST, submission_id)

def check_submission_rate_limit(
    user_id: int,
    limit: int = 5,
    window_seconds: int = 60
) -> bool:
    key = f"rate_limit:submissions:{user_id}"

    client = get_redis_client()
    count = client.incr(key)

    if count == 1:
        client.expire(key, window_seconds)

    return count <= limit
