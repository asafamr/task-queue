
import asyncio
import json
import os
from concurrent.futures import ThreadPoolExecutor

from minio import Minio


async def get_artifacts_client():
    executor = ThreadPoolExecutor()
    return await asyncio.get_running_loop().run_in_executor(
            executor, _do_get_client, executor)

def _do_get_client(executor: ThreadPoolExecutor):
    minio_client = Minio(os.getenv("MINIO_URL"),
        access_key="minio123", # should be hardend in prod
        secret_key="minio123",
        secure=False
    )
    return ArtifactsClient(minio_client, executor)
    
class ArtifactsClient():
    def __init__(self, minio_client:Minio, executor:ThreadPoolExecutor) -> None:
        self.minio_client = minio_client
        self.executor = executor
    
    async def get_signed_url(self, task_id):
        def do_get():
             return self.minio_client.get_presigned_url('GET', 'artifacts', task_id)
        return await asyncio.get_running_loop().run_in_executor(
            self.executor, do_get)
       