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
