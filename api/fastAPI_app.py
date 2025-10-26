from fastapi import FastAPI
from fastapi.responses import JSONResponse

from api.bot.bot_router import bot_router

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

app.include_router(bot_router)
