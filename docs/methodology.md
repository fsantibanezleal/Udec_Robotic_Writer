# Methodology — Robotic Writer System

## 1. Problem Statement

Given:
- A **5-DOF Scorbot III robotic arm** fixed at the center of a workspace.
- **26 cubic letter blocks** (A–Z), each placed on a circular arc at a known radius from the robot base.
- A **writing line** (straight segment) where blocks are to be placed in sequence.

Task: Given an input text string, the robot must autonomously **pick each letter block** from the circle and **place it in order** on the writing line, forming the written word.

## 2. Approach

### 2.1 Character Mapping

Each character in the input string is mapped to a physical block position on the circular arc:

1. Convert character to uppercase.
2. Look up the block index (A=0, B=1, ..., Z=25).
3. Compute the block's angular position: `θ_block = θ_start + index × Δθ`.
4. Convert to Cartesian coordinates using the circle geometry.

Spaces are handled by leaving an empty slot on the writing line (no pick operation).

### 2.2 Pick-and-Place Cycle

For each character, the robot executes a 9-step sequence:

| Step | Action | Description |
|------|--------|-------------|
| 1 | Open gripper | Prepare to grasp |
| 2 | Move above block | Navigate to safe height above target block |
| 3 | Lower to block | Descend vertically to block position |
| 4 | Close gripper | Grasp the block |
| 5 | Lift | Raise to safe height with block |
| 6 | Move above slot | Navigate to safe height above writing position |
| 7 | Lower to slot | Descend to writing line height |
| 8 | Open gripper | Release the block |
| 9 | Lift | Raise to safe height, ready for next cycle |

### 2.3 Trajectory Planning

- **Joint-space interpolation**: Smooth cubic ease-in/ease-out between configurations.
- **Inverse kinematics**: Each target position is converted to joint angles.
- **Safe height**: All horizontal traversals occur at a configurable safe height (default 150 mm) to avoid collisions.
- **Approach angle**: The gripper approaches blocks vertically from above (-90°).

### 2.4 Motion Safety

- Joint limits are validated before executing any motion.
- Unreachable positions raise errors rather than attempting impossible configurations.
- Emergency stop capability is available through all hardware adapters.

## 3. Hardware Abstraction

The system supports multiple hardware backends through a common `HardwareAdapter` interface:

| Backend | Protocol | Use Case |
|---------|----------|----------|
| **MATLAB Engine** | MATLAB API | Legacy Scorbot III with existing MATLAB scripts |
| **Arduino Serial** | ASCII over USB | Custom stepper motor setup |
| **Direct Serial** | Scorbot byte protocol | Direct RS-232 connection to Scorbot controller |

All backends implement the same interface: `connect()`, `send_command()`, `disconnect()`, `emergency_stop()`.

## 4. Simulation Architecture

The simulation mode (no hardware required) executes the complete writing sequence in memory:

1. **Core engine** computes kinematics and generates trajectories.
2. **Writer logic** orchestrates the pick-and-place sequence.
3. **Trajectory data** (joint angles, positions, timestamps) is recorded.
4. **Frontend** renders the 3D animation from the recorded data.

This allows development, testing, and demonstration without physical hardware.

## 5. Coordinate Frames

| Frame | Origin | Description |
|-------|--------|-------------|
| World | Robot base on table | Fixed reference |
| Base (Frame 0) | Robot mounting point | Coincident with world |
| Frame 1 | Joint 1 axis | After base rotation |
| Frame 2 | Joint 2 axis | After shoulder rotation |
| Frame 3 | Joint 3 axis | After elbow rotation |
| Frame 4 | Joint 4 axis | After pitch rotation |
| Frame 5 (EE) | Gripper tip | End-effector frame |

## 6. Block Circle Geometry

N letter blocks (A-Z, N=26) are arranged on a circular arc of radius R centered at the robot base. The position of block k is:

```
x_k = R * cos(theta_0 + k * delta_theta)
y_k = R * sin(theta_0 + k * delta_theta)
z_k = h_table (constant surface height)
```

where:
- `theta_0 = -(N-1) * delta_theta / 2` centers the arc symmetrically about the forward direction
- `delta_theta = 8 degrees` is the angular separation between adjacent blocks
- The total arc spans from `theta_min = theta_0` to `theta_max = theta_0 + (N-1) * delta_theta`
- Total angular span: `(N-1) * delta_theta = 25 * 8 = 200 degrees`

The circular arrangement guarantees that every block is at the same radial distance from the robot base, ensuring uniform reachability and consistent approach geometry for the gripper.

## 7. Writing Line Geometry

Letters are placed sequentially along a writing arc (or line) at fixed spacing. For the arc-based layout (current implementation), the position of letter j in the word is:

```
x_j = R_write * cos(theta_center + j * angular_spacing)
y_j = R_write * sin(theta_center + j * angular_spacing)
z_j = z_surface
```

where:
- `R_write = R_block + offset` (default offset = 60 mm)
- `theta_center` is the angular center of the writing zone (default -25 degrees)
- `angular_spacing = 4 degrees` between adjacent letter slots

For the simplified linear layout:
```
x_j = x_start + j * spacing
y_j = y_line
z_j = z_surface
```

where `spacing = 30 mm` between block centers. The linear layout is simpler but can extend beyond the workspace for long words, which is why the arc-based layout was adopted in v2.2.

## 8. Ouija Mode

In Ouija mode, the robot acts as a "spirit board" spelling out answers to user questions. The decision flow is:

1. **Question input**: User types a question into the interface
2. **Classification**: The question is classified by its first word into categories (Yes/No, Who, When, Where, What, How, Greeting, or Mysterious)
3. **Response generation**: A response is randomly selected from a curated pool matching the question category. There is a 20% chance of overriding any category with a "mysterious" response (e.g., "BEWARE", "WAKE UP")
4. **Letter sequence**: The response string is converted to a sequence of letter indices
5. **Trajectory planning**: For each letter, the inverse kinematics and pick-and-place trajectory are computed
6. **Execution**: The robot picks each letter block from the circle and places it on the writing arc, spelling out the response

The Ouija mode reuses the same pick-and-place infrastructure as Tutorial mode. The key difference is that the text comes from the response generator rather than direct user input. With `infinite_replacement` enabled (default), the same letter block can be reused for repeated characters in the response.
