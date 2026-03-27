# Methodology History

Reverse-chronological log of design decisions, changes, equations, and improvements applied to the Robotic Writer project. Most recent changes appear first.

---

## v2.7 — Writing Radial Offset Control (2026-03-26)

Added slider **"Writing Radial Offset (mm)"** (range 20–150, default 60) to control the radial distance between the block circle and the writing arc. The writing arc radius is computed as `block_radius + offset`. This replaces the previous hardcoded `+20mm` and allows clear visual separation between the two zones.

---

## v2.6 — Animation Performance Fix (2026-03-26)

### Problem

Play button and speed controls were unresponsive. The Python server round-trip for each frame tick (~80ms interval) could not keep up with the 3D render cycle, causing stalls.

### Solution

- Replaced the server-side `update_frame` callback with a **clientside callback** (JavaScript) that runs directly in the browser with zero latency.
- Increased interval period from 80ms to **250ms** to allow the browser time to render each 3D frame.
- Speed radio values now represent actual frames-per-tick: 1x=5, 2x=10, 5x=25, 10x=50, Max=100.

---

## v2.5 — UI/UX Improvements (2026-03-26)

### Camera preservation

Added `uirevision="constant"` to the Plotly figure layout. This preserves the user's camera position, zoom, and rotation when the figure data updates (e.g., during animation playback).

### Dark mode slider visibility

- Created `assets/custom.css` with white tooltip text on dark background.
- Increased vertical spacing between sliders (`marginBottom: 30px`) to prevent tooltip overlap with next component.
- Animation frame slider spacing increased to 36px.

### Animation speed control

Added `RadioItems` speed selector (1x, 2x, 5x, 10x, Max) controlling frames-per-tick for Play and step buttons.

### Block colors

- Available blocks: **green** (#44ff44)
- Used blocks: **blue** (#448AFF) — previously red, changed to avoid confusion with errors.

### Writing arc angle control

Added slider "Writing Arc Angle (deg)" ranging -90 to 90 (default -25) to allow the user to position the writing zone at any angle around the robot, separating it visually from the block circle.

---

## v2.4 — Infinite Block Replacement (2026-03-26)

### Problem

In the original behavior, each letter block can only be used once. Words with repeated letters (e.g., "HELLO" has two L's) would skip the second occurrence.

### Solution

Added `infinite_replacement` flag to `RoboticWriter`:

- **`True` (default)**: Blocks are never consumed. After picking a block, it remains available for future use. Used characters are tracked in a `_used_characters` set for visualization only (displayed in blue).
- **`False`**: Original behavior. `block.is_available = False` after pick. Second use of same letter is skipped.

Frontend toggle: `dbc.Switch` labeled "Infinite block replacement".

---

## v2.3 — Writing Modes: Tutorial and Ouija (2026-03-26)

### Tutorial mode

User types a phrase, the robot writes it letter by letter. Direct transcription with full pick-and-place simulation.

### Ouija mode

User asks a question, the system generates a "spirit response" from curated pools. Questions are classified by type:

| Question type | Detection | Example pool |
|---|---|---|
| Greeting | First word in {HI, HELLO, HEY, ...} | "GREETINGS", "I SEE YOU" |
| Yes/No | Starts with IS, ARE, DO, WILL, CAN, ... | "YES", "MAYBE", "DOUBTFUL" |
| Who | Starts with WHO | "A FRIEND", "A GHOST" |
| When | Starts with WHEN | "TONIGHT", "IN A DREAM" |
| Where | Starts with WHERE | "BEHIND YOU", "NOWHERE" |
| What | Starts with WHAT/WHICH/WHY | "THE TRUTH", "A SECRET" |
| How | Starts with HOW | "SLOWLY", "WITH CARE" |
| Mysterious | Fallback / 20% random override | "BEWARE", "WAKE UP" |

20% of all responses randomly bypass the category and return a "mysterious" response regardless of question type.

---

## v2.2 — Writing Line: Linear to Arc (2026-03-26)

### Problem

The linear writing line extended too far from the robot. For long words like "HELLO WORLD" (11 chars), the last slot at `(300 + 10*30, -200, 50) = (600, -200, 50)` was far beyond the arm's reach (~440mm effective).

### Solution

Replaced `WritingLine` from a straight line to an **arc at constant radius** from the robot base. This guarantees all slot positions are at the same distance from the robot, always within the workspace.

```python
# Arc-based slot positioning:
angle = center_angle + index * angular_spacing
x = radius * cos(angle)
y = radius * sin(angle)
z = height
```

Parameters:
- `radius_mm`: distance from base (default: block_radius + offset)
- `center_angle_deg`: angular center of the writing arc (configurable, default -25 deg)
- `angular_spacing_deg`: angle between adjacent slots (default 4 deg)

### Workspace analysis

Approach angle was changed from -90 deg (straight down) to **-70 deg** for better reachability. The safe height was reduced from 150mm to 75mm. Systematic testing confirmed positions at radius 250-375mm, z=50-80mm are reachable at -70 deg approach.

---

## v2.1 — IK Bug Fix: theta234 Formula (2026-03-26)

### Problem

The inverse kinematics `theta234` calculation was producing incorrect values. At home position (all joints = 0), the FK gives approach vector `[0, 0, -1]` (gripper pointing down), and `theta234` should equal `0`. However, the formula computed `pi/2`.

### Root cause

The original MATLAB formula:
```
theta234 = atan2(-uz/cos5, (ux*cos1+uy*sin1)/cos5)
```

This was ported directly, but the `atan2(y, x)` argument order was wrong for this DH convention. Verification showed:

| Expected theta234 | uz | ux | atan2(-uz, ux) | atan2(-ux, -uz) |
|---|---|---|---|---|
| 0 | -1.0 | 0.0 | 90 | **0** |
| -30 | -0.866 | 0.5 | 60 | **-30** |
| -90 | 0.0 | 1.0 | 0 | **-90** |

### Fix

```python
# Before (wrong):
theta234 = math.atan2(-uz / cos5, (ux*cos1 + uy*sin1) / cos5)

# After (correct for this DH convention):
ux_eff = (ux * cos(theta1) + uy * sin(theta1)) / cos5
uz_eff = -uz / cos5
theta234 = math.atan2(-ux_eff, uz_eff)
```

---

## v2.0 — Python Modernization (2026-03-26)

### Architecture redesign

- **Backend**: FastAPI REST API (`src/api/main.py`)
- **Frontend**: Dash + Plotly 3D interactive GUI (`src/frontend/app.py`)
- **Core engine**: Pure NumPy kinematics (`src/core/kinematics.py`)
- **Hardware layer**: Abstract adapter pattern supporting MATLAB Engine, Arduino serial, and direct Scorbot III serial (`src/hardware/`)

### Key equations preserved

All original DH parameters and kinematic equations were ported to Python with NumPy matrix operations. Each homogeneous transformation is the product of four elementary transforms:

```
A_i = Rz(theta_i) * Tz(d_i) * Tx(a_i) * Rx(alpha_i)
```

Expanded as a single 4x4 matrix:

```
A_i = [[cos(t), -cos(a)*sin(t),  sin(a)*sin(t), a_i*cos(t)],
       [sin(t),  cos(a)*cos(t), -sin(a)*cos(t), a_i*sin(t)],
       [0,       sin(a),         cos(a),         d_i       ],
       [0,       0,              0,              1         ]]
```

Forward kinematics chain:

```
T_05 = A_1 * A_2 * A_3 * A_4 * A_5
```

Inverse kinematics (analytical closed-form):

```
theta1 = atan2(qy, qx)
theta5 = asin(ux*sin(theta1) - uy*cos(theta1))
theta234 = atan2(-ux_eff, uz_eff)
theta3 = acos((k1^2 + k2^2 - a2^2 - a3^2) / (2*a2*a3))
theta2 = atan2(sin2, cos2)
theta4 = theta234 - theta2 - theta3
```

### Block Circle geometry

Blocks placed on a symmetric arc centered at theta=0:
```
theta_start = -(N-1) * delta_theta / 2
block_i_angle = theta_start + i * delta_theta
x_i = R * cos(block_i_angle)
y_i = R * sin(block_i_angle)
z_i = h_table
```

### Writing Line (initial: linear)

Initially implemented as a straight line:
```
slot_j = start_xyz + j * spacing * direction_unit_vector
```

Default: start=(300, -200, 50), direction=(1,0,0), spacing=30mm.

---

## v1.0 — Original MATLAB Implementation (2004/2007)

**Platform**: MATLAB + Winwedge DDE + RS-232 serial

**Hardware**: Scorbot III, 5-DOF + gripper

**Kinematics**: Denavit-Hartenberg convention with the following parameters:

| Joint | alpha (rad) | d (mm) | a (mm) | theta |
|-------|-------------|--------|--------|-------|
| 1 (Base) | -pi/2 | 340 | 16 | theta1 |
| 2 (Shoulder) | 0 | 0 | 220 | theta2 |
| 3 (Elbow) | 0 | 0 | 220 | theta3 |
| 4 (Pitch) | -pi/2 | 0 | 0 | theta4 |
| 5 (Roll) | 0 | 151 | 0 | theta5 |

**Forward Kinematics**:
```
T_05 = A1 * A2 * A3 * A4 * A5
Position = [T(1,4), T(2,4), T(3,4)]
```

**Inverse Kinematics** (analytical, closed-form):
```
theta1 = atan2(qy, qx)
theta5 = asin(ux*sin(theta1) - uy*cos(theta1))
theta234 = atan2(-uz/cos(theta5), (ux*cos(theta1)+uy*sin(theta1))/cos(theta5))
theta3 = acos((k1^2 + k2^2 - a2^2 - a3^2) / (2*a2*a3))
theta2 = atan2(sin2, cos2)
theta4 = theta234 - theta2 - theta3
```

**Block arrangement**: Letters on a circular arc, character-to-index mapping via ASCII offset.

**Communication**: DDE protocol to Winwedge, serial byte commands `[motor_id, 'M', direction, d4, d3, d2, d1, CR]`.
