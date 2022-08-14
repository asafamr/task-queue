
import logging
import os
import sys
from typing import Dict, Optional

from celery import Celery
from celery.signals import setup_logging
from celery.schedules import timedelta
import requests

from task_dispatch.util import gen_batches
from .artifacts import upload_json_artifact
from .q_state import  get_all_task_statuses, is_task_existing, remove_tasks, set_tasks_status, try_global_lock

app = Celery('task-dispatcher')

app.conf.beat_schedule = {
    'sync': {
        'task': 'task_dispatch.q.sync_db_and_queue',
        'schedule': timedelta(seconds=10) # every k sec
    },
}

def on_success(task, result, celery_task_id, args, kwargs):
    set_tasks_status([kwargs['task_id']], 'SUCCEEDED')

def on_failure(task, error, celery_task_id, args, kwargs, exception):
    set_tasks_status([kwargs['task_id']], 'FAILED')

def before_start(task, celery_task_id, args, kwargs):
    set_tasks_status([kwargs['task_id']], 'RUNNING')

@app.task(on_success=on_success,before_start=before_start,on_failure=on_failure)
def http_task(task_id:str, task_type:str, params:dict):
    if not is_task_existing(task_id):
        raise Exception('Task is not registered. deleted?')
    task_url = os.getenv('HTTP_TASK_URL_TEMPLATE',
        'http://task-svc-{task_type}.default.svc.cluster.local/run').format(
            task_type=task_type
        )
    req = requests.post(task_url, json=params)
    req.raise_for_status()
    result = req.json()
    upload_json_artifact(task_id, result)
    return

@app.task
def sync_db_and_queue():
    with try_global_lock("DB_SYNC", ttl_sec=10*60) as got_lock:
        if not got_lock:
            raise Exception('Sync in progress, aborting...')
        batch_size = int(os.getenv('SYNC_DB_BATCH_SIZE','1000'))
        manager_url = os.getenv('MANAGER_URL', 'http://task-manager:8000')

        req_session = requests.Session()
        
        # queue -> db
        current_status = get_all_task_statuses()
        for batch in gen_batches(current_status.items(), batch_size):
            work_done = [{'status':status, 'uid':uid} for uid,status in batch]
            req = req_session.patch(manager_url+'/v1/internal/tasks/work', json=work_done, timeout=30)
            req.raise_for_status()
            remove_tasks([uid for uid,status in current_status.items() if status in ['FAILED', 'SUCCEEDED'] ])
        
        # db -> queue 
        last_retrived_uid = None
        while True:
            params = {'batch_size':batch_size}
            if last_retrived_uid:
                params['start_uid'] = last_retrived_uid
            req = req_session.get(manager_url+'/v1/internal/tasks/work',
                params=params, timeout=30)
            req.raise_for_status()
            all_running_tasks = req.json()
            new_tasks = [x for x in all_running_tasks if x['uid'] not in current_status]
            for new_task in new_tasks:
                http_task.delay(task_id=new_task['uid'], task_type=new_task['task_type'], params=new_task['params'])
            set_tasks_status([new_task['uid'] for new_task in new_tasks], 'QUEUED')
            all_running_tasks_uids = set(x['uid'] for x in all_running_tasks)
            deleted_tasks = [x for x in current_status if x not in all_running_tasks_uids]
            remove_tasks(deleted_tasks) 
            if len(all_running_tasks) < batch_size:
                break
            last_retrived_uid = new_tasks[-1]['uid']



@setup_logging.connect()
def config_loggers(*args, **kwargs):
    logging.basicConfig(stream=sys.stdout, level=os.getenv('LOGGING_LEVEL','INFO'))