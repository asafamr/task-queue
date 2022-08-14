#!/bin/bash
python -m uvicorn --host 0.0.0.0 task_manager.server:app