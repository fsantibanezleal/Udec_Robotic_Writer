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

## References

- Denavit, J. & Hartenberg, R.S. (1955). "A kinematic notation for lower-pair mechanisms based on matrices." *ASME J. of Applied Mechanics*.
- Craig, J.J. (2005). *Introduction to Robotics: Mechanics and Control*. 3rd ed. Pearson.
- Scorbot-ER III Technical Manual, Eshed Robotec.
