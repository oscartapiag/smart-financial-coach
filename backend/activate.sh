#!/bin/bash
# Script to activate the virtual environment and run the FastAPI server

echo "🚀 Activating virtual environment..."
source venv/bin/activate

echo "📦 Virtual environment activated!"
echo "💡 You can now run:"
echo "   python app.py"
echo "   python run_server.py"
echo "   uvicorn app:app --reload"
echo ""
echo "🌐 Server will be available at: http://localhost:8000"
echo "📚 API docs will be available at: http://localhost:8000/docs"
echo ""

# Optionally start the server automatically
read -p "Do you want to start the server now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔥 Starting FastAPI server..."
    python run_server.py
fi
