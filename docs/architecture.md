# Architecture — Robotic Writer

System-level overview of how the Robotic Writer components fit together. For the full problem formulation, see [methodology.md](methodology.md); for derivations, see [equations/kinematics.md](equations/kinematics.md).

## 1. Layered View

```
┌─────────────────────────────────────────────────────────┐
│  Frontend (Dash + Plotly)         src/frontend/app.py   │
│  • Kinematics tab • Animation tab • Writer tab          │
└───────────────▲─────────────────────────────────────────┘
                │  HTTP / JSON
┌───────────────┴─────────────────────────────────────────┐
│  REST API (FastAPI)               src/api/main.py       │
│  /api/kinematics/{forward,inverse}  /api/writer/simulate│
│  /api/robot/state  /api/hardware/*  /api/health         │
└───────────────▲─────────────────────────────────────────┘
                │  Python calls
┌───────────────┴─────────────────────────────────────────┐
│  Core engine                      src/core/             │
│  • kinematics.py  — DH, FK, IK, joint limits            │
│  • robot.py       — ScorbotIII model + trajectory plan  │
│  • writer.py      — block circle / writing line / cycle │
│  • rrt_planner.py — collision-free motion planning      │
│  • cursive.py     — Bezier cursive character paths      │
└───────────────▲─────────────────────────────────────────┘
                │  optional, only when driving real HW
┌───────────────┴─────────────────────────────────────────┐
│  Hardware adapters                src/hardware/         │
│  base.py (interface) + matlab_adapter / arduino /       │
│  serial_adapter                                         │
└─────────────────────────────────────────────────────────┘
```

An SVG equivalent lives at [diagrams/system_architecture.svg](diagrams/system_architecture.svg).

## 2. Request Lifecycle — `POST /api/writer/simulate`

1. Frontend posts the text string and geometry parameters.
2. API validates the payload through Pydantic (`WriteRequest`).
3. API constructs `BlockCircle`, `WritingLine`, and `RoboticWriter`.
4. Writer runs the pick-and-place loop per character, delegating:
   - IK computation → `core.kinematics.InverseKinematics`
   - Joint-space trajectories → `core.robot.ScorbotIII.plan_trajectory`
   - Optional obstacle avoidance → `core.rrt_planner.RRTPlanner`
5. API returns a trajectory record (joint angles, EE positions, timestamps).
6. Frontend renders the animation from that record — **no** server round-trip per frame (this was the v2.6 fix).

## 3. Core Modules

| Module | Responsibility | Notes |
|---|---|---|
| `kinematics.py` | DH parameters, `ForwardKinematics`, `InverseKinematics`, `JointState`, `JOINT_LIMITS_DEG` | Closed-form analytic IK, elbow-up/down resolved by collision avoidance |
| `robot.py` | `ScorbotIII` robot facade | Wraps FK/IK + trajectory planning + joint-limit validation |
| `writer.py` | Writing pipeline | `BlockCircle`, `WritingLine`, `RoboticWriter` orchestrator |
| `rrt_planner.py` | Sampling-based planner | 1000-iteration limit + post-smoothing, used for non-trivial obstacles |
| `cursive.py` | Bezier curve generator | Per-character control points for cursive writing mode |
| `modes.py` | Text mode heuristics | Block vs cursive selection hints |

## 4. API Surface (stable v1)

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/writer/simulate` | Full pick-and-place trajectory for a string |
| POST | `/api/kinematics/forward` | FK from 5 joint angles |
| POST | `/api/kinematics/inverse` | IK from target (x, y, z, approach) |
| GET  | `/api/robot/state` | Current joint / gripper state |
| POST | `/api/hardware/connect` | Attach a hardware adapter |
| GET  | `/api/health` | Liveness probe |

Validation ranges (`block_radius_mm 200–400`, `writing_angular_spacing_deg 2–8`, etc.) live in Pydantic models in `src/api/main.py` — per the `API Defaults` rule, any frontend default should be checked against these bounds.

## 5. Hardware Adapter Contract

All adapters implement `HardwareAdapter` (`src/hardware/base.py`) with:

- `connect(**kwargs)` / `disconnect()`
- `send_command(cmd: str) -> str`
- `move_motor(joint_id: int, steps: int)`
- `emergency_stop()`

This lets the same `ScorbotIII` engine drive simulation **or** real hardware by swapping one dependency.

## 6. Extension Points

- **New letter glyphs** → add to `core/cursive.py` (Bezier control points).
- **New planner** → implement the same `plan(start, goal, obstacles)` signature as `RRTPlanner`.
- **New hardware** → subclass `HardwareAdapter`, register in `src/hardware/__init__.py`.
- **New API endpoint** → add route + Pydantic schema in `src/api/main.py`, cover with `tests/test_api.py`.

## 7. Test Strategy

- `test_kinematics.py` — FK/IK round-trips and joint-limit edge cases.
- `test_robot.py` — full `ScorbotIII` trajectory continuity (C¹).
- `test_rrt_planner.py` — path feasibility and smoothing invariants.
- `test_cursive.py` — character path topology.
- `test_api.py` — endpoint contracts via FastAPI TestClient.

## 8. Diagram Convention

Every SVG in this repository lives under [`docs/diagrams/`](diagrams/), **not** `docs/svg/` as suggested by the CAOS `project-quality-standards.md` convention. This divergence is intentional and preserved for three reasons:

1. **Semantic clarity** — the word *diagram* better describes the content here (kinematic frames, workspace layouts, timelines) than the generic *svg*, which only names a file format.
2. **Path stability** — 83 tests, the Dash frontend asset loader, and every `docs/*.md` + `README.md` link reference `docs/diagrams/...`. Renaming the directory would touch ~40 path strings across source, docs, and tests with no functional gain.
3. **History** — the folder predates the CAOS convention; the original laboratory note from 2004 already labelled its figures as *diagramas*.

**File-naming rules inside `docs/diagrams/` still follow the convention spirit:**

| Role | File |
|---|---|
| High-level system blocks | `system_architecture.svg` |
| End-to-end algorithm flow | `solution_flowchart.svg` |
| Per-character pick-and-place timeline | `pipeline.svg` |
| Kinematic reference frames | `dh_frames.svg` |
| Physical setup (top view) | `robot_setup.svg` |
| Reachable workspace envelope | `workspace.svg` |
| Joint-space / task-space trajectory | `trajectory.svg` |

New SVGs must be placed here and listed in both the Documentation table of the README and the most relevant `docs/*.md` reference.
