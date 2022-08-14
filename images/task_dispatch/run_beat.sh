#!/bin/bash
python -m celery -A task_dispatch.q beat