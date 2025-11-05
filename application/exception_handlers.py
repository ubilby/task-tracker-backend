from exceptions import UserNotFoundError, TaskNotFoundError
from fastapi.responses import JSONResponse


async def value_error_exception_handler(request, exc: ValueError):
    """Преобразует Python's ValueError в HTTP 400 Bad Request."""
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)},
    )


async def user_not_found_exception_handler(request, exc: UserNotFoundError):
    """Преобразует UserNotFoundError в HTTP 404 Not Found."""
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc)},
    )


async def task_not_found_exception_handler(request, exc: TaskNotFoundError):
    """Преобразует TaskNotFoundError в HTTP 404 Not Found."""
    return JSONResponse(
        status_code=404,
        content={"detail": str(exc)},
    )


CUSTOM_EXCEPTION_HANDLERS = {
    ValueError: value_error_exception_handler,
    UserNotFoundError: user_not_found_exception_handler,
    TaskNotFoundError: task_not_found_exception_handler,
}
