from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import PlainTextResponse
from starlette import status
from app.core.config import settings
from app.db.init_db import init_db
from app.router import auth, staff, customer
from app.router.frontend import frontend


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
app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(frontend.router, prefix="/frontend", tags=["frontend"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(staff.router, prefix="/staffs", tags=["staffs"])
app.include_router(customer.router, prefix="/customers", tags=["customers"])


@app.exception_handler(Exception)
async def custom_exception_handler(request: Request, exc: Exception):
    # Log the error for debugging purposes (optional but recommended)
    print(f"Unhandled server error occurred: {exc}")

    # Use PlainTextResponse to safely return a string
    return PlainTextResponse(
        "Unhandled Server Exception", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )