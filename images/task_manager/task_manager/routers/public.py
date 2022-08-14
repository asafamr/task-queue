import datetime
from typing import List
from fastapi import APIRouter, Header, Request, Body
from task_manager.artifacts import ArtifactsClient

from task_manager.db import DbClient
from task_manager.models import Task, TaskRequest, TaskStatus

router = APIRouter()

@router.put("/tasks")
async def schedule_user_task(request: Request, 
        task_request:TaskRequest= Body(embed=True), 
        user_id:str = Header(default='anonymous')) -> Task:
    new_task = Task(
        user_id=user_id, 
        task_type=task_request.task_type,
        params=task_request.params,
        last_update=datetime.datetime.now(datetime.timezone.utc),
        status=TaskStatus.REQUESTED
        )
    dbc:DbClient = request.app.state.dbc
    return await dbc.schedule_task(new_task)

@router.get("/tasks")
async def get_user_tasks(request: Request, user_id:str = Header(default='anonymous'))-> List[Task]:
    dbc:DbClient = request.app.state.dbc
    return await dbc.get_user_tasks(user_id=user_id)

@router.get("/tasks/{task_id}")
async def get_user_task(request: Request, task_id:str, user_id:str = Header(default='anonymous'))-> List[Task]:
    dbc:DbClient = request.app.state.dbc
    return await dbc.get_user_task(user_id=user_id, task_id=task_id)

@router.get("/tasks/{task_id}/results")
async def get_user_task_link(request: Request, task_id:str, user_id:str = Header(default='anonymous'))-> List[Task]:
    """
    just a POC - the signed hostname is set to cluster host (minio)
    """ 
    dbc:DbClient = request.app.state.dbc
    ac:ArtifactsClient = request.app.state.ac
    task = await dbc.get_user_task(user_id=user_id, task_id=task_id)
    if task and task.status == TaskStatus.SUCCEEDED:
        return await ac.get_signed_url(task_id)
    return None