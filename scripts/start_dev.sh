#!/bin/bash
echo "Starting IBM Migration Advisor..."

source .venv/bin/activate

sudo service redis-server start
echo "✓ Redis started"

mlflow server \
  --host 0.0.0.0 \
  --port 5000 \
  --backend-store-uri sqlite:///mlflow.db \
  --default-artifact-root ./mlartifacts \
  --serve-artifacts &> logs/mlflow.log &
echo "✓ MLflow at http://localhost:5000"

echo ""
echo "Dev environment ready."
echo "  Backend:  uvicorn backend.api.main:app --reload"
echo "  Frontend: cd frontend && npm run dev"
