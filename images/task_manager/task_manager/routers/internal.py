from typing import List, Optional

from fastapi import APIRouter, Body, Request
from task_manager.db import DbClient
from task_manager.models import Task, TaskStatusUpdate

router = APIRouter()


@router.get("/tasks/work")
async def get_tasks_work_batch(
    request: Request, batch_size: int = 100, start_uid: Optional[str] = None
) -> List[Task]:
    dbc: DbClient = request.app.state.dbc
    return await dbc.get_workable_batch(batch_size=batch_size, start_uid=start_uid)


@router.patch("/tasks/work")
async def update_tasks_work_batch(
    request: Request, work_done: List[TaskStatusUpdate] = Body()
):
    dbc: DbClient = request.app.state.dbc
    return await dbc.update_work_batch(work_done)
