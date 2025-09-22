#!/usr/bin/env python3
"""
Script to run the Mental Health Chatbot server
"""
import uvicorn
import sys
import os

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    """Run the FastAPI server"""
    print("🚀 Starting Mental Health Chatbot Server...")
    print("📱 Chat Interface: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("🔧 Health Check: http://localhost:8000/health")
    print("\n" + "="*50)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()
