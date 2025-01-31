from fastapi import FastAPI

from app.config import settings
from app.endpoints.request import api_router

fastapi_app = FastAPI(
            title=settings.APP_NAME,
            description="Проект для мегашколы",
            version=settings.APP_VERSION,
            debug=settings.ENABLE_DEBUG
        )

fastapi_app.include_router(api_router, prefix=settings.API_PREFIX)