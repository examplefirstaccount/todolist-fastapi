#!/bin/bash

# Run migrations
echo "Running migrations..."
alembic upgrade head

# Start the FastAPI app with Gunicorn and Uvicorn workers
echo "Starting FastAPI app with Gunicorn..."
exec gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
