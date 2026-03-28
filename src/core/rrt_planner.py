"""
RRT (Rapidly-exploring Random Tree) path planner for the Scorbot III.

Plans collision-free paths in joint space by growing a tree from the
start configuration toward the goal, avoiding joint limit violations
and workspace obstacles.

For the Scorbot III, "obstacles" are joint limit boundaries and
optional rectangular exclusion zones in Cartesian workspace.
"""
import numpy as np
from typing import List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class Obstacle:
    """Rectangular exclusion zone in workspace (x_min, x_max, y_min, y_max, z_min, z_max)."""
    bounds: np.ndarray  # (6,) [xmin, xmax, ymin, ymax, zmin, zmax]


class RRTPlanner:
    """RRT path planner in joint space."""

    def __init__(self, joint_limits: np.ndarray, step_size: float = 5.0,
                 max_iterations: int = 1000, goal_threshold: float = 3.0):
        """
        Args:
            joint_limits: (N_joints, 2) array of [min, max] per joint (degrees).
            step_size: Maximum step size per iteration (degrees).
            max_iterations: Maximum tree growth iterations.
            goal_threshold: Distance to goal for success (degrees).
        """
        self.joint_limits = joint_limits
        self.step_size = step_size
        self.max_iterations = max_iterations
        self.goal_threshold = goal_threshold
        self.obstacles: List[Obstacle] = []

    def add_obstacle(self, bounds: np.ndarray):
        """Add a workspace obstacle."""
        self.obstacles.append(Obstacle(bounds=np.asarray(bounds)))

    def plan(self, start: np.ndarray, goal: np.ndarray,
             forward_kinematics_fn=None, seed=None) -> Optional[List[np.ndarray]]:
        """Plan a path from start to goal in joint space.

        Args:
            start: Start joint configuration (degrees).
            goal: Goal joint configuration (degrees).
            forward_kinematics_fn: Optional function(joints) -> (x,y,z)
                for workspace obstacle checking.
            seed: Random seed.

        Returns:
            List of joint configurations forming the path, or None if failed.
        """
        rng = np.random.default_rng(seed)

        # Trivial case: start is already at goal
        if np.linalg.norm(start - goal) < self.goal_threshold:
            return [start.copy(), goal.copy()]

        # Tree: list of (config, parent_index)
        tree = [(start.copy(), -1)]

        for _ in range(self.max_iterations):
            # Sample random configuration (biased toward goal 10% of time)
            if rng.random() < 0.1:
                q_rand = goal.copy()
            else:
                q_rand = np.array([
                    rng.uniform(lo, hi) for lo, hi in self.joint_limits
                ])

            # Find nearest node in tree
            dists = [np.linalg.norm(node[0] - q_rand) for node in tree]
            nearest_idx = int(np.argmin(dists))
            q_nearest = tree[nearest_idx][0]

            # Steer toward random sample
            direction = q_rand - q_nearest
            dist = np.linalg.norm(direction)
            if dist < 1e-6:
                continue
            q_new = q_nearest + direction / dist * min(self.step_size, dist)

            # Check joint limits
            if not self._within_limits(q_new):
                continue

            # Check workspace obstacles
            if forward_kinematics_fn and self.obstacles:
                pos = forward_kinematics_fn(q_new)
                if self._collides(pos):
                    continue

            # Add to tree
            tree.append((q_new.copy(), nearest_idx))

            # Check if goal reached
            if np.linalg.norm(q_new - goal) < self.goal_threshold:
                # Extract path
                path = [q_new]
                idx = len(tree) - 1
                while tree[idx][1] >= 0:
                    idx = tree[idx][1]
                    path.append(tree[idx][0])
                path.reverse()
                path.append(goal)
                return path

        return None  # Failed to find path

    def _within_limits(self, q: np.ndarray) -> bool:
        for i, (lo, hi) in enumerate(self.joint_limits):
            if q[i] < lo or q[i] > hi:
                return False
        return True

    def _collides(self, pos: np.ndarray) -> bool:
        for obs in self.obstacles:
            b = obs.bounds
            if (b[0] <= pos[0] <= b[1] and
                b[2] <= pos[1] <= b[3] and
                b[4] <= pos[2] <= b[5]):
                return True
        return False

    def smooth_path(self, path: List[np.ndarray],
                    forward_kinematics_fn=None, iterations: int = 50,
                    seed=None) -> List[np.ndarray]:
        """Smooth path by random shortcutting."""
        rng = np.random.default_rng(seed)
        path = [p.copy() for p in path]

        for _ in range(iterations):
            if len(path) < 3:
                break
            i = rng.integers(0, len(path) - 2)
            j = rng.integers(i + 2, len(path))

            # Check if shortcut is valid
            shortcut = path[i] + np.linspace(0, 1, 5)[:, None] * (path[j] - path[i])
            valid = True
            for q in shortcut:
                if not self._within_limits(q):
                    valid = False
                    break
                if forward_kinematics_fn and self.obstacles:
                    if self._collides(forward_kinematics_fn(q)):
                        valid = False
                        break

            if valid:
                path = path[:i+1] + [path[j]] + path[j+1:]

        return path
