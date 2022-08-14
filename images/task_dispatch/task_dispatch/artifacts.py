import io
import json
import os
from minio import Minio

def upload_json_artifact(artifcat_name, obj):
    client = Minio(os.getenv("MINIO_URL"),
        access_key="minio123",
        secret_key="minio123",
        secure=False
    )
    to_send = json.dumps(obj).encode('utf8')
    result = client.put_object(
        "artifacts", artifcat_name, io.BytesIO(to_send), length=len(to_send),
    )
    assert result.etag

