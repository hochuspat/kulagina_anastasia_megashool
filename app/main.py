import uvicorn

from app.app import fastapi_app
from app.config import settings


def run():
    """
    Запуск сервера
    """
    host = settings.APP_ADDRESS
    port = settings.APP_PORT

    uvicorn_log_config = uvicorn.config.LOGGING_CONFIG
    del uvicorn_log_config["loggers"]

    uvicorn.run(
        app=fastapi_app,
        host=host,
        port=port,
        log_config=uvicorn_log_config,
    )

if __name__ == "__main__":
    run()