"""
PocketSmart AI Main Entry Point (main.py)
Re-exports the FastAPI app and starts Uvicorn when run directly.
"""
from app import app

if __name__ == "__main__":
    import os
    import uvicorn
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    print(f"Starting PocketSmart: AI Budget Planner on http://{host}:{port} ...")
    uvicorn.run("app:app", host=host, port=port, reload=True)
