"""
Standalone executable entry point for Udec_Robotic_Writer.

When frozen by PyInstaller, this script:
1. Sets the working directory to the executable's location
2. Starts the FastAPI backend on port 8005
3. Starts the Dash frontend on port 8055
4. Opens the default browser at http://127.0.0.1:8055

Usage (development):
    python run_app.py [--api-port 8005] [--frontend-port 8055] [--no-browser]

Usage (frozen):
    ./Udec_Robotic_Writer.exe [--api-port 8005] [--frontend-port 8055] [--no-browser]
"""
import sys
import os
import argparse
import webbrowser
import threading
from pathlib import Path


def _exe_dir() -> Path:
    """Return the directory containing the executable (frozen) or script (dev)."""
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent


def _run_api(host: str, port: int):
    """Start the FastAPI backend server in a thread."""
    import uvicorn
    uvicorn.run("src.api.main:app", host=host, port=port, log_level="info")


def _run_frontend(host: str, port: int):
    """Start the Dash frontend server in a thread."""
    from src.frontend.app import app
    app.run(host=host, port=port, debug=False)


def main():
    parser = argparse.ArgumentParser(description="Udec_Robotic_Writer")
    parser.add_argument('--api-port', type=int, default=8005)
    parser.add_argument('--frontend-port', type=int, default=8055)
    parser.add_argument('--host', type=str, default='127.0.0.1')
    parser.add_argument('--no-browser', action='store_true')
    args = parser.parse_args()

    # Set working directory for stable relative paths
    os.chdir(str(_exe_dir()))

    api_url = f"http://{args.host}:{args.api_port}"
    frontend_url = f"http://{args.host}:{args.frontend_port}"

    print(f"Starting Udec_Robotic_Writer")
    print(f"  API backend:  {api_url}")
    print(f"  Dash frontend: {frontend_url}")

    # Thread 1: FastAPI backend
    api_thread = threading.Thread(
        target=_run_api,
        args=(args.host, args.api_port),
        daemon=True,
    )
    api_thread.start()

    # Open browser to Dash frontend
    if not args.no_browser:
        threading.Timer(2.0, lambda: webbrowser.open(frontend_url)).start()

    # Thread 2 (main thread): Dash frontend
    _run_frontend(args.host, args.frontend_port)


if __name__ == "__main__":
    main()
