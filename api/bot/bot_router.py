from fastapi import APIRouter
from api.bot.routers.task_router import task_router
from api.bot.routers.user_router import user_router


bot_router = APIRouter(prefix="/bot", tags=["bot"])
bot_router.include_router(user_router)
bot_router.include_router(task_router)
