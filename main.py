from fastapi import FastAPI

from application.exception_handlers import CUSTOM_EXCEPTION_HANDLERS
from user.api.router import user_router
from task.api.router import task_router


app = FastAPI(
    title="TaskTracker API",
    exception_handlers=CUSTOM_EXCEPTION_HANDLERS    
)
app.include_router(user_router)
app.include_router(task_router)

