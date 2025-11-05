from fastapi import FastAPI
from fastapi.responses import JSONResponse

from user.api.router import user_router
from task.api.router import task_router

app = FastAPI(title="TaskTracker API")


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


app.include_router(user_router)
app.include_router(task_router)
