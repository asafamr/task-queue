#!/bin/bash
python -m uvicorn --host 0.0.0.0 syft_task.server:app 