ARG ARG_PYTHON_IMAGE=python:3.13.1

FROM ${ARG_PYTHON_IMAGE}

SHELL ["/bin/bash", "-c"]

ARG WORKDIR_ARG="/app"
WORKDIR $WORKDIR_ARG

COPY ./pyproject.toml ./
COPY ./poetry.lock ./

COPY ./app ./app

COPY ./entrypoint.sh ./
COPY ./start.sh ./

ARG VENV_PATH_ARG="/opt/venv"
ENV VENV_PATH=$VENV_PATH_ARG

RUN python -m venv "$VENV_PATH"
ENV PATH="$VENV_PATH/bin:$PATH"

RUN source "$VENV_PATH/bin/activate" && pip install poetry
RUN source "$VENV_PATH/bin/activate" && poetry config virtualenvs.create false
RUN source "$VENV_PATH/bin/activate" && poetry install --no-root --only main

ENV PYTHONUNBUFFERED=1

RUN chmod +x "./entrypoint.sh"
ENTRYPOINT ["./entrypoint.sh"]

RUN chmod +x "./start.sh"
CMD ["./start.sh"]
