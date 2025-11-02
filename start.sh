#!/bin/bash

# Unified startup script for Stellest AI Platform
# This script starts both backend and frontend servers

echo "🚀 Starting Stellest AI Platform..."
echo ""

# Function to handle cleanup on exit
cleanup() {
    echo ""
    echo "⚠️  Shutting down servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Start backend server
echo "📡 Starting Backend API Server (Port 8000)..."
cd "$(dirname "$0")"
python3 api_server.py > /tmp/stellest_backend.log 2>&1 &
BACKEND_PID=$!

# Wait for backend to be ready
sleep 3

# Check if backend started successfully
if curl -s http://localhost:8000/ > /dev/null 2>&1; then
    echo "✅ Backend API Server is running"
else
    echo "❌ Backend server failed to start. Check /tmp/stellest_backend.log"
    exit 1
fi

# Start frontend server
echo "🌐 Starting Frontend Server (Port 3000)..."
cd web-app
npm run dev > /tmp/stellest_frontend.log 2>&1 &
FRONTEND_PID=$!

# Wait for frontend to be ready
sleep 5

echo ""
echo "════════════════════════════════════════════════════════"
echo "✅ Stellest AI Platform is now running!"
echo ""
echo "📍 Access the platform at:"
echo "   http://localhost:3000"
echo ""
echo "📊 Backend API (for debugging):"
echo "   http://localhost:8000"
echo ""
echo "⚠️  Press Ctrl+C to stop both servers"
echo "════════════════════════════════════════════════════════"
echo ""

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID

