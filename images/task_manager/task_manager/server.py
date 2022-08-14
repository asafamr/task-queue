import task_manager.routers.internal as router_inner
import task_manager.routers.public as router_public
from fastapi import Body, FastAPI, Header
from task_manager.artifacts import get_artifacts_client
from task_manager.db import get_db_client

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

app.include_router(
    router_inner.router,
    prefix="/v1/internal",
    # include_in_schema=False
)
app.include_router(
    router_public.router,
    prefix="/v1/public",
)

@app.on_event("startup")
async def init_app():
    app.state.dbc = await get_db_client()
    app.state.ac = await get_artifacts_client()