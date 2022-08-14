#!/bin/bash
python -m celery -A task_dispatch.q flower --address= --port=5566