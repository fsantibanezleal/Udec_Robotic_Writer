# Kinematics — Mathematical Foundation

## 1. Denavit-Hartenberg Convention

The Scorbot III robot arm is modeled using the standard **Denavit-Hartenberg (DH)** convention for serial manipulators. Each joint-link pair is described by four parameters:

| Parameter | Symbol | Description |
|-----------|--------|-------------|
| Link twist | α_i | Angle between z_{i-1} and z_i about x_i |
| Link offset | d_i | Distance along z_{i-1} from origin to x_i intersection |
| Link length | a_i | Distance along x_i between z_{i-1} and z_i |
| Joint angle | θ_i | Rotation about z_{i-1} (variable for revolute joints) |

### DH Parameter Table for Scorbot III

| Joint | α (rad) | d (mm) | a (mm) | θ |
|-------|---------|--------|--------|---|
| 1 (Base) | -π/2 | 340 | 16 | θ₁ |
| 2 (Shoulder) | 0 | 0 | 220 | θ₂ |
| 3 (Elbow) | 0 | 0 | 220 | θ₃ |
| 4 (Pitch) | -π/2 | 0 | 0 | θ₄ |
| 5 (Roll) | 0 | 151 | 0 | θ₅ |

## 2. Forward Kinematics

### Homogeneous Transformation Matrix

For each joint i, the transformation from frame i-1 to frame i is:

```
        ┌ cos(θᵢ)   -cos(αᵢ)sin(θᵢ)    sin(αᵢ)sin(θᵢ)    aᵢcos(θᵢ) ┐
A_i =   │ sin(θᵢ)    cos(αᵢ)cos(θᵢ)   -sin(αᵢ)cos(θᵢ)    aᵢsin(θᵢ) │
        │ 0           sin(αᵢ)            cos(αᵢ)            dᵢ         │
        └ 0           0                   0                   1          ┘
```

### End-Effector Pose

The total transformation from base to end-effector:

```
T₀₅ = A₁ · A₂ · A₃ · A₄ · A₅
```

The position vector is extracted from the last column:

```
p = [T₀₅(1,4), T₀₅(2,4), T₀₅(3,4)]ᵀ = [x, y, z]ᵀ
```

The orientation is the upper-left 3×3 rotation matrix:

```
R = T₀₅(1:3, 1:3)
```

## 3. Inverse Kinematics

Given a desired end-effector position **q** = [qx, qy, qz] and orientation matrix with approach vector **u** = [ux, uy, uz]:

### Step 1: Base Angle θ₁

```
θ₁ = atan2(qy, qx)
```

### Step 2: Wrist Roll θ₅

```
θ₅ = arcsin(ux·sin(θ₁) - uy·cos(θ₁))
```

The argument is clamped to [-1, 1] for numerical stability.

### Step 3: Combined Pitch Angle θ₂₃₄

```
θ₂₃₄ = atan2(-uz/cos(θ₅), (ux·cos(θ₁) + uy·sin(θ₁))/cos(θ₅))
```

### Step 4: Planar 2-Link Problem

Intermediate variables for the shoulder-elbow planar problem:

```
k₁ = qx·cos(θ₁) + qy·sin(θ₁) - a₁ + d₅·sin(θ₂₃₄)
k₂ = -qz + d₁ - d₅·cos(θ₂₃₄)
```

### Step 5: Elbow Angle θ₃ (Cosine Law)

```
cos(θ₃) = (k₁² + k₂² - a₂² - a₃²) / (2·a₂·a₃)
θ₃ = arccos(cos(θ₃))
```

If |cos(θ₃)| > 1, the target is unreachable.

### Step 6: Shoulder Angle θ₂

```
cos(θ₂) = [k₁(a₂ + a₃cos(θ₃)) + k₂·a₃·sin(θ₃)] / D
sin(θ₂) = [-k₁·a₃·sin(θ₃) + k₂(a₂ + a₃cos(θ₃))] / D
θ₂ = atan2(sin(θ₂), cos(θ₂))
```

where D = a₂² + a₃² + 2·a₂·a₃·cos(θ₃)

### Step 7: Pitch Angle θ₄

```
θ₄ = θ₂₃₄ - θ₂ - θ₃
```

## 4. Block Circle Geometry

Letter blocks are arranged on a circular arc of radius R centered at the robot base:

```
Block_i position:
  x_i = R · cos(θ_start + i · Δθ)
  y_i = R · sin(θ_start + i · Δθ)
  z_i = h_table (constant height)

where:
  θ_start = -(N-1)·Δθ / 2  (centered symmetric arc)
  Δθ = minimum angular separation (default 8°)
  N = number of blocks (26 for A-Z)
```

Total angular span: `(N-1) · Δθ = 25 × 8° = 200°`

## 5. Writing Line Geometry

Blocks are placed sequentially along a line:

```
Slot_j position:
  p_j = p_start + j · s · d̂

where:
  p_start = starting point of the writing line
  s = spacing between block centers (default 30 mm)
  d̂ = unit direction vector (default [1, 0, 0])
```

## 6. Joint Limits

| Joint | Min (°) | Max (°) |
|-------|---------|---------|
| θ₁ (Base) | -126.5 | +126.5 |
| θ₂ (Shoulder) | -120.0 | +63.0 |
| θ₃ (Elbow) | -90.0 | +90.0 |
| θ₄ (Pitch) | -250.0 | +40.0 |
| θ₅ (Roll) | -180.0 | +180.0 |
| Gripper | 0 mm | 59 mm |

## 7. Motor Step Resolution

| Motor | Joint | Resolution |
|-------|-------|-----------|
| 1 | Base | 0.094°/step |
| 2 | Shoulder | 0.1175°/step |
| 3 | Elbow | 0.1175°/step |
| 4 | Pitch | 0.458°/step |
| 5 | Roll | 0.458°/step |
| 8 | Gripper | 6.7797 steps/mm |

## 8. Denavit-Hartenberg Convention Detail

For each joint i, the homogeneous transformation is composed of four elementary transformations applied in sequence:

```
A_i = Rz(theta_i) * Tz(d_i) * Tx(a_i) * Rx(alpha_i)
```

This product expands to the standard 4x4 DH matrix:

```
        [cos(theta)  -sin(theta)cos(alpha)   sin(theta)sin(alpha)  a*cos(theta)]
A_i =   [sin(theta)   cos(theta)cos(alpha)  -cos(theta)sin(alpha)  a*sin(theta)]
        [0            sin(alpha)              cos(alpha)             d           ]
        [0            0                       0                      1           ]
```

Each elementary transformation has a geometric interpretation:
- **Rz(theta_i)**: Rotate about z_{i-1} by the joint angle (the variable for revolute joints)
- **Tz(d_i)**: Translate along z_{i-1} by the link offset
- **Tx(a_i)**: Translate along x_i by the link length
- **Rx(alpha_i)**: Rotate about x_i by the link twist

The key advantage of the DH convention is that any rigid body transformation between consecutive joint axes can be described by exactly four parameters, reducing the 6-DOF problem to 4 parameters by careful choice of coordinate frame placement.

## 9. Workspace Analysis

The **reachable workspace** is the set of all points (x, y, z) achievable by the end-effector for at least one orientation. For the Scorbot III with 5 revolute joints:

### Workspace Boundaries

The workspace is bounded by:
- **Outer radius**: R_max = a_2 + a_3 + d_5 = 220 + 220 + 151 = 591 mm (arm fully extended)
- **Inner radius**: R_min = |a_2 - a_3 - d_5| (arm folded back, limited by joint limits)
- **Height range**: Determined by joint limits on theta_2, theta_3, theta_4 combined with link lengths

### Workspace Volume for a 5R Robot

For a general 5R serial manipulator, the reachable workspace volume is approximated by the volume of the partial spherical shell minus self-collision zones:

```
V_workspace = (4/3) * pi * (R_max^3 - R_min^3) * (theta_1_range / 2*pi) * K_collision
```

where:
- `theta_1_range = 253 deg = 4.415 rad` (from -126.5 to +126.5 degrees)
- `K_collision` is the collision-free fraction (typically 0.6-0.8 for the Scorbot III)

For the Scorbot III specifically:
```
R_max = 591 mm
R_min ~ 50 mm (estimated from joint limit constraints)
V_workspace ~ (4/3) * pi * (591^3 - 50^3) * (253/360) * 0.7
           ~ 0.43 m^3
```

The actual reachable workspace is a partial sphere (not a full sphere) because:
1. Joint 1 (base) only rotates 253 degrees, not 360
2. Joints 2 and 3 have asymmetric limits, creating a non-uniform cross-section
3. Self-collision between links eliminates part of the interior volume

![Workspace Diagram](diagrams/workspace.svg)

## 10. Jacobian Matrix

The Jacobian matrix relates joint velocities to end-effector velocities:

```
v = J(q) * q_dot
```

where v = [v_x, v_y, v_z, omega_x, omega_y, omega_z]^T is the 6D end-effector velocity (linear + angular) and q_dot = [theta_1_dot, ..., theta_5_dot]^T is the vector of joint velocities.

For the Scorbot III (5 DOF), the Jacobian is a 6x5 matrix:

```
J = [J_v]   = [z_0 x p_0n,  z_1 x p_1n,  ...,  z_4 x p_4n]
    [J_w]     [z_0,          z_1,          ...,  z_4        ]
```

where:
- `z_i` = unit vector along joint i axis (third column of T_{0i})
- `p_in` = vector from joint i origin to end-effector (last column of T_{0n} minus last column of T_{0i})
- `x` denotes the cross product

### Singularities

Singularities occur when rank(J) < min(6, 5) = 5, meaning the arm loses one or more degrees of freedom in Cartesian space. For the Scorbot III, singular configurations include:

1. **Arm fully extended**: theta_3 = 0, the elbow is straight. The arm cannot move radially.
2. **Arm fully folded**: theta_3 = +/-180 degrees (if reachable). Same loss of radial DOF.
3. **Wrist aligned with base axis**: theta_5 singularity when the wrist roll axis aligns with the base rotation axis.

At or near singularities, the inverse kinematics solution becomes numerically unstable (condition number of J diverges), and joint velocities required for small Cartesian motions become very large.

## 11. Trajectory Planning

The pick-and-place trajectory uses **cubic polynomial interpolation** for smooth motion between waypoints. For each joint, the trajectory segment from time 0 to T is:

```
theta(t) = a_0 + a_1*t + a_2*t^2 + a_3*t^3
```

With boundary conditions for zero velocity at start and end (rest-to-rest motion):

```
theta(0) = theta_start     =>  a_0 = theta_start
theta(T) = theta_end       =>  a_0 + a_1*T + a_2*T^2 + a_3*T^3 = theta_end
theta_dot(0) = 0            =>  a_1 = 0
theta_dot(T) = 0            =>  a_1 + 2*a_2*T + 3*a_3*T^2 = 0
```

Solving for the coefficients:

```
a_0 = theta_start
a_1 = 0
a_2 = 3*(theta_end - theta_start) / T^2
a_3 = -2*(theta_end - theta_start) / T^3
```

This yields a smooth **S-curve** velocity profile:

```
theta_dot(t) = 6*(theta_end - theta_start)/T^2 * t * (1 - t/T)
```

The acceleration profile is:

```
theta_ddot(t) = 6*(theta_end - theta_start)/T^2 * (1 - 2*t/T)
```

The maximum velocity occurs at t = T/2 and equals `1.5 * (theta_end - theta_start) / T`. The maximum acceleration occurs at the endpoints and equals `6 * (theta_end - theta_start) / T^2`.

For multi-segment trajectories (e.g., the full pick-and-place cycle), via-point constraints ensure continuity of position and velocity at segment junctions, producing globally smooth motion.

![Trajectory Profile](diagrams/trajectory.svg)

## References

- Denavit, J. & Hartenberg, R.S. (1955). "A kinematic notation for lower-pair mechanisms based on matrices." *ASME J. of Applied Mechanics*.
- Craig, J.J. (2005). *Introduction to Robotics: Mechanics and Control*. 3rd ed. Pearson.
- Scorbot-ER III Technical Manual, Eshed Robotec.
