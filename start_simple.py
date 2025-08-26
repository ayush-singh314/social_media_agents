#!/usr/bin/env python3
"""
Simple startup script to avoid ASGI factory warning
"""

import uvicorn
import os

if __name__ == "__main__":
    print("Starting Content Ideation Agent API Server (Simple Mode)...")
    print("Server will be available at:")
    print("  - Local: http://127.0.0.1:8000")
    print("  - Network: http://0.0.0.0:8000")
    print("  - Frontend: http://127.0.0.1:8000/static/")
    print("  - Test Page: http://127.0.0.1:8000/static/test.html")
    print("  - API Docs: http://127.0.0.1:8000/docs")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 50)
    
    # Start the server using the module approach
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
        access_log=True,
        reload=False
    )
