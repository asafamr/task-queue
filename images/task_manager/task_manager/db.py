import datetime
import os
from typing import Any, Dict, List, Optional

import pymongo
from bson.objectid import ObjectId
from motor.core import AgnosticCollection
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import UpdateOne
from task_manager.models import Task, TaskStatus, TaskStatusUpdate


async def get_db_client():
    mongo_client = AsyncIOMotorClient(os.getenv("MONGO_URL", "mongodb://mongo:27017"))
    await mongo_client.tasks.tasks.create_index(
        [("finished", pymongo.ASCENDING)],
        partialFilterExpression={"finished": {"$eq": False}},
        background=True,
    )
    await mongo_client.tasks.tasks.create_index([("user_id", pymongo.ASCENDING)])
    return DbClient(mongo_client)


class DbClient:
    def __init__(self, client) -> None:
        self.db = client.tasks

    async def get_user_tasks(self, user_id: str) -> List[Task]:
        collection: AgnosticCollection = self.db.tasks
        cursor = collection.find({"user_id": {"$eq": user_id}})
        return [Task.from_db_dict(x) async for x in cursor]

    async def get_user_task(self, user_id: str, task_id: str) -> Optional[Task]:
        collection: AgnosticCollection = self.db.tasks
        ret = await collection.find_one(
            {"user_id": {"$eq": user_id}, "_id": {"$eq": ObjectId(task_id)}},
        )
        if not ret:
            return None
        return Task.from_db_dict(ret)

    async def schedule_task(self, task: Task) -> str:
        collection: AgnosticCollection = self.db.tasks
        d = task.dict()
        d.pop("uid")
        inserted = await collection.insert_one(d, {"w": 1})
        return str(inserted.inserted_id)

    async def get_workable_batch(
        self,
        batch_size=100,
        start_uid=None,
        stale_task_after_sec=5 * 60,
    ) -> str:
        collection: AgnosticCollection = self.db.tasks
        filters = [
            {"finished": {"$eq": False}},
            #  {'$or':[ TODO: optimize to send only not-recently update
            #      {'status': { '$eq': TaskStatus.REQUESTED }},
            #      {'last_update': {'$lt': datetime.datetime.now(datetime.timezone.utc)
            #         - datetime.timedelta(seconds=stale_job_after_sec)}}
            #      ]}
        ]

        if start_uid:
            filters.append({"_id": {"$gt": ObjectId(start_uid)}})

        cursor = collection.find({"$and": filters}).limit(batch_size)
        return [Task.from_db_dict(x) async for x in cursor]

    async def update_work_batch(self, work_done: List[TaskStatusUpdate]) -> str:
        collection: AgnosticCollection = self.db.tasks
        # now_date = datetime.datetime.now(datetime.timezone.utc)
        res = await collection.bulk_write(
            [
                UpdateOne(
                    {"_id": ObjectId(x.uid)},
                    {
                        "$set": {
                            "status": x.status,
                            # 'last_update':now_date,
                            "finished": x.status
                            in [TaskStatus.FAILED, TaskStatus.SUCCEEDED],
                            "additional_info": x.additional_info,
                        }
                    },
                )
                for x in work_done
            ],
            ordered=False,
        )
        return res.matched_count
