#!/bin/bash
# FastAPI Server Startup Script

echo "🚀 Starting FastAPI Student Management Server..."
echo "📍 Server will be available at: http://localhost:8000"
echo "📚 API Documentation at: http://localhost:8000/docs"
echo ""

cd /Users/prathyusha/agentic-systems-assignments
export PYTHONPATH=/Users/prathyusha/agentic-systems-assignments/fastapi-and-databases

python3 -m uvicorn crud_operations:app --host 0.0.0.0 --port 8000 --reload