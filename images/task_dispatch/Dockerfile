FROM python:3.10.6-slim-bullseye as prod

RUN groupadd -r app && useradd --no-log-init -m -r -g app app 

RUN apt-get update && apt-get install -y \
  curl \
  && rm -rf /var/lib/apt/lists/*

RUN curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin

USER app
WORKDIR /home/app

COPY requirements.txt /home/app

RUN pip install --no-cache-dir -r /home/app/requirements.txt

COPY run_flower.sh run_worker.sh run_beat.sh /home/app/
COPY --chown=app:app ./task_dispatch /home/app/task_dispatch 
