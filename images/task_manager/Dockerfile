FROM python:3.10.6-slim-bullseye as prod

RUN groupadd -r app && useradd --no-log-init -m -r -g app app 

RUN apt-get update && apt-get install -y \
  curl \
  && rm -rf /var/lib/apt/lists/*

USER app
WORKDIR /home/app

COPY requirements.txt /home/app

RUN pip install --no-cache-dir -r /home/app/requirements.txt

COPY run_server.sh /home/app/
COPY --chown=app:app ./task_manager /home/app/task_manager

FROM prod as dev
RUN pip install --no-cache-dir debugpy
