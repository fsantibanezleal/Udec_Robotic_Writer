"""Entry point: Launch the Dash interactive frontend."""

from src.frontend.app import app

if __name__ == "__main__":
    print("Starting Robotic Writer Simulator...")
    print("Open http://localhost:8055 in your browser")
    app.run(debug=True, host="0.0.0.0", port=8055)
