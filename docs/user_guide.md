# User Guide — Robotic Writer

End-to-end walkthrough for running the Robotic Writer in simulation or against real hardware. Aimed at a first-time user who already has Python 3.12+ and Git installed.

## 1. Install

```bash
git clone https://github.com/fsantibanezleal/Udec_Robotic_Writer.git
cd Udec_Robotic_Writer
python -m venv .venv
# Windows:  .venv\Scripts\activate
# Unix:     source .venv/bin/activate
pip install -r requirements.txt
```

## 2. Start the GUI (simulation only)

```bash
python run_frontend.py
```

Open http://localhost:8055. The GUI has three tabs:

| Tab | What you can do |
|---|---|
| **Kinematics** | Slide joint angles, read live FK; enter a target (x,y,z) and read IK; see joint limits highlighted in red if out of range. |
| **Writer** | Type a string (≤ 50 chars), adjust block radius / angular separation / writing offset, click **Run Simulation**. |
| **Animation** | Play / pause / seek through the trajectory recorded by the writer. |

Recommended first run: **Writer tab → type `HELLO` → Run Simulation → switch to Animation**.

## 3. Start the API (optional)

In a separate terminal:

```bash
python run_api.py
```

Open http://localhost:8005/docs for the auto-generated Swagger UI. The most useful endpoint for scripting is `POST /api/writer/simulate`:

```bash
curl -X POST http://localhost:8005/api/writer/simulate \
     -H "Content-Type: application/json" \
     -d '{"text":"HELLO","block_radius_mm":280,"writing_angular_spacing_deg":4}'
```

The response contains the full joint-angle trajectory plus end-effector positions and timestamps — see [architecture.md §2](architecture.md) for the request lifecycle.

## 4. Drive Real Hardware

Pick one backend.

### 4.1 Scorbot III (direct serial)

```python
from src.hardware import SerialAdapter
a = SerialAdapter()
a.connect(port="COM1", baud=9600)   # adjust to your port
a.move_motor(1, 500)                # +500 steps on base joint
a.disconnect()
```

### 4.2 Arduino stepper rig

Flash the firmware in [arduino_firmware.md](arduino_firmware.md), then:

```python
from src.hardware import ArduinoAdapter
a = ArduinoAdapter()
a.connect(port="COM3", baud=115200)
a.move_motor(1, 500)
a.disconnect()
```

### 4.3 MATLAB Engine (legacy Scorbot scripts)

```bash
pip install matlabengine        # requires local MATLAB install
```

```python
from src.hardware import MatlabAdapter
a = MatlabAdapter()
a.connect()                     # starts MATLAB session
a.move_motor(1, 500)
a.disconnect()
```

## 5. Common Workflows

| Goal | Steps |
|---|---|
| **Check if a point is reachable** | Kinematics tab → type the target → if no red joint-limit warning, it's reachable |
| **Tune block spacing** | Writer tab → increase `min_angular_separation_deg` until the 3D view shows clear gaps |
| **Compare block vs cursive** | Writer tab → toggle writing mode → Run Simulation → compare Animation tab |
| **Debug an IK failure** | Call `POST /api/kinematics/inverse` directly — the error message tells you which joint hit a limit |

## 6. Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| GUI shows "Connection refused" | API not running | Start `python run_api.py` in a second terminal |
| Animation stutters | Old browser / low GPU | Reduce trajectory density or shorten the input text |
| IK returns error | Target outside workspace | Reduce block radius or lift z slightly |
| `Port in use` on 8005 / 8055 | Another instance running | Kill the process or change the port in `run_api.py` / `run_frontend.py` |
| Real robot doesn't move | Wrong COM port / baud | Verify in Device Manager (Windows) or `ls /dev/tty*` (Unix) |

## 7. Tests

```bash
pip install pytest
pytest tests/ -v
```

Expect 83 tests to pass (see the [README metrics table](../README.md#project-metrics--status)).

## 8. Where to Go Next

- [methodology.md](methodology.md) — the problem the robot is solving.
- [architecture.md](architecture.md) — how the pieces fit together.
- [equations/kinematics.md](equations/kinematics.md) — the math.
- [references.md](references.md) — external reading.
