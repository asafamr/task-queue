
import os
from contextlib import contextmanager
from functools import lru_cache

import redis


# memoized
@lru_cache
def get_redis_connection() -> redis.StrictRedis:
    return redis.StrictRedis.from_url(os.getenv('REDIS_URL'), decode_responses=True)

def set_tasks_status(task_ids, status):
    if len(task_ids):
        client=get_redis_connection()
        pipeline = client.pipeline()
        for task_id in task_ids:
            pipeline.hset('STATUS', task_id, status)
        pipeline.execute()

def remove_tasks(task_ids):
    if len(task_ids):
        client=get_redis_connection()
        pipeline = client.pipeline()
        for task_id in task_ids:
            pipeline.hdel('STATUS', task_id)
        pipeline.execute()

def get_all_task_statuses():
    client=get_redis_connection()
    return client.hgetall('STATUS')

def is_task_existing(task_id):
    client=get_redis_connection()
    return client.hexists('STATUS', task_id) == 1

@contextmanager
def try_global_lock(lock_name, ttl_sec=10*60):
    client = get_redis_connection()
    lock = client.lock('LOCK_'+lock_name, timeout=ttl_sec)
    acquired = lock.acquire(blocking=False, )
    try:
        yield acquired
    finally:
        if acquired:
            lock.release()
   

