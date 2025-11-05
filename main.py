from fastapi import FastAPI
from fastapi.responses import JSONResponse

from user.api.router import user_router
from task.api.router import task_router
from exceptions import UserNotFoundError, TaskNotFoundError


app = FastAPI(title="TaskTracker API")
app.include_router(user_router)
app.include_router(task_router)


@app.exception_handler(ValueError)
async def value_error_exception_handler(request, exc: ValueError):
    """
    Этот обработчик будет ловить ВСЕ ошибки ValueError,
    вылетающие из твоего приложения, и превращать их в 400 Bad Request.
    """
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)},
    )


@app.exception_handler(UserNotFoundError)
async def user_not_found_exception_handler(request, exc: ValueError):

    return JSONResponse(
        status_code=404,
        content={"detail": str(exc)},
    )


@app.exception_handler(TaskNotFoundError)
async def task_not_found_exception_handler(request, exc: ValueError):

    return JSONResponse(
        status_code=404,
        content={"detail": str(exc)},
    )
