#!/bin/sh
set -e

export $(grep -v '^#' .env | xargs)

MODULE_NAME=${MODULE_NAME:-app.app}
VARIABLE_NAME=${VARIABLE_NAME:-fastapi_app}
export APP_MODULE=${APP_MODULE:-"$MODULE_NAME:$VARIABLE_NAME"}

HOST=${HOST:-0.0.0.0}
PORT=${PORT:-8080}
LOG_LEVEL=${LOG_LEVEL:-info}


# Start Uvicorn with live reload
exec uvicorn --reload --host $HOST --port $PORT --log-level $LOG_LEVEL "$APP_MODULE"
