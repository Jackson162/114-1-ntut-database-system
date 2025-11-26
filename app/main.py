from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.config import settings
from app.db.init_db import init_db
from app.router import auth, frontend


@asynccontextmanager
async def lifespan(app: FastAPI):
    # executed before the application starts taking requests,
    # during the startup.
    if settings.DO_INIT_DB:
        await init_db(app)
    yield
    # This code will be executed after the application
    # finishes handling requests, right before the shutdown.


app = FastAPI(lifespan=lifespan)

app.include_router(frontend.router, prefix="/frontend")
app.include_router(auth.router, prefix="/auth")
