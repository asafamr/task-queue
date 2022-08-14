from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class TaskStatus(str, Enum):
    REQUESTED = "REQUESTED"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"


class Task(BaseModel):
    uid: Optional[str]
    user_id: str
    task_type: str
    params: dict
    status: TaskStatus
    additional_info: dict = {}
    last_update: datetime
    finished: bool = False

    @staticmethod
    def from_db_dict(d):
        cp = dict(**d)
        uid = cp.pop("_id")
        return Task(uid=str(uid), **cp)


class TaskRequest(BaseModel):
    task_type: str
    params: dict


class TaskStatusUpdate(BaseModel):
    uid: str
    status: TaskStatus
    additional_info: dict = {}
