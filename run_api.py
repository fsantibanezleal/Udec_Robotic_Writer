"""Entry point: Launch the FastAPI backend server."""

import uvicorn

if __name__ == "__main__":
    print("Starting Robotic Writer API...")
    print("API docs: http://localhost:8005/docs")
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8005, reload=True)
