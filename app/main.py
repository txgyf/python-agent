from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import init_db
from app.routers import gpus


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="LLM Deployment Tracker", lifespan=lifespan)
app.include_router(gpus.router)
