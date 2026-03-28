"""Tests for the RRT path planner."""

import numpy as np
import pytest

from src.core.rrt_planner import RRTPlanner, Obstacle


# Joint limits for a 5-DOF arm (simplified for testing)
SIMPLE_LIMITS = np.array([
    [-180, 180],
    [-180, 180],
    [-180, 180],
    [-180, 180],
    [-180, 180],
], dtype=float)


@pytest.fixture
def planner():
    return RRTPlanner(
        joint_limits=SIMPLE_LIMITS,
        step_size=10.0,
        max_iterations=2000,
        goal_threshold=5.0,
    )


class TestBasicPlanning:
    """Test basic RRT path planning without obstacles."""

    def test_plan_simple_path(self, planner):
        """RRT should find a path between two valid configurations."""
        start = np.array([0.0, 0.0, 0.0, 0.0, 0.0])
        goal = np.array([50.0, 30.0, -20.0, 10.0, 0.0])

        path = planner.plan(start, goal, seed=42)

        assert path is not None, "RRT should find a path"
        assert len(path) >= 2, "Path should have at least start and goal"
        np.testing.assert_array_almost_equal(path[0], start)
        np.testing.assert_array_almost_equal(path[-1], goal)

    def test_plan_same_start_goal(self, planner):
        """RRT should quickly find a trivial path when start == goal."""
        config = np.array([10.0, 20.0, 30.0, 40.0, 50.0])

        path = planner.plan(config, config.copy(), seed=42)

        # With goal bias of 10%, it should find this quickly
        assert path is not None

    def test_plan_respects_joint_limits(self, planner):
        """All waypoints in the path should be within joint limits."""
        start = np.array([0.0, 0.0, 0.0, 0.0, 0.0])
        goal = np.array([100.0, -100.0, 50.0, -50.0, 80.0])

        path = planner.plan(start, goal, seed=42)
        assert path is not None

        for waypoint in path:
            for i, (lo, hi) in enumerate(SIMPLE_LIMITS):
                assert lo <= waypoint[i] <= hi, \
                    f"Joint {i} value {waypoint[i]} out of limits [{lo}, {hi}]"

    def test_plan_fails_for_unreachable_goal(self):
        """RRT should return None when goal is outside joint limits."""
        tight_limits = np.array([[-10, 10]] * 5, dtype=float)
        planner = RRTPlanner(
            joint_limits=tight_limits,
            step_size=2.0,
            max_iterations=100,
            goal_threshold=1.0,
        )

        start = np.array([0.0] * 5)
        # Goal is outside limits -- planner can't reach it
        goal = np.array([50.0] * 5)

        path = planner.plan(start, goal, seed=42)
        assert path is None, "Should fail for unreachable goal"


class TestObstacleAvoidance:
    """Test RRT with workspace obstacles."""

    def test_plan_avoids_obstacle(self):
        """Path should avoid a workspace obstacle when FK is provided."""
        limits = np.array([[-180, 180]] * 5, dtype=float)
        planner = RRTPlanner(
            joint_limits=limits,
            step_size=10.0,
            max_iterations=3000,
            goal_threshold=5.0,
        )

        # Add an obstacle in the workspace
        planner.add_obstacle(np.array([-50, 50, -50, 50, -50, 50]))

        # Simple FK: just use first 3 joints as x, y, z
        def fake_fk(joints):
            return joints[:3].copy()

        start = np.array([0.0, 0.0, -100.0, 0.0, 0.0])
        goal = np.array([0.0, 0.0, 100.0, 0.0, 0.0])

        path = planner.plan(start, goal, forward_kinematics_fn=fake_fk, seed=42)

        if path is not None:
            # Verify no waypoint collides with obstacle
            for wp in path:
                pos = fake_fk(wp)
                assert not planner._collides(pos), \
                    f"Waypoint at position {pos} collides with obstacle"

    def test_add_obstacle(self, planner):
        """Adding obstacles should increase the obstacle list."""
        assert len(planner.obstacles) == 0
        planner.add_obstacle(np.array([0, 10, 0, 10, 0, 10]))
        assert len(planner.obstacles) == 1
        planner.add_obstacle(np.array([20, 30, 20, 30, 20, 30]))
        assert len(planner.obstacles) == 2

    def test_collides_inside(self, planner):
        """A point inside an obstacle should be detected as collision."""
        planner.add_obstacle(np.array([0, 10, 0, 10, 0, 10]))
        assert planner._collides(np.array([5, 5, 5])) is True

    def test_collides_outside(self, planner):
        """A point outside all obstacles should not collide."""
        planner.add_obstacle(np.array([0, 10, 0, 10, 0, 10]))
        assert planner._collides(np.array([20, 20, 20])) is False


class TestPathSmoothing:
    """Test path smoothing via random shortcutting."""

    def test_smooth_reduces_waypoints(self, planner):
        """Smoothing should reduce or maintain the number of waypoints."""
        start = np.array([0.0, 0.0, 0.0, 0.0, 0.0])
        goal = np.array([80.0, -60.0, 40.0, -30.0, 20.0])

        path = planner.plan(start, goal, seed=42)
        assert path is not None

        original_len = len(path)
        smoothed = planner.smooth_path(path, seed=42, iterations=100)

        assert len(smoothed) <= original_len, \
            "Smoothed path should have fewer or equal waypoints"
        # First and last should be preserved
        np.testing.assert_array_almost_equal(smoothed[0], path[0])
        np.testing.assert_array_almost_equal(smoothed[-1], path[-1])

    def test_smooth_respects_limits(self, planner):
        """Smoothed path should still respect joint limits."""
        start = np.array([0.0, 0.0, 0.0, 0.0, 0.0])
        goal = np.array([50.0, 30.0, -20.0, 10.0, 0.0])

        path = planner.plan(start, goal, seed=42)
        assert path is not None

        smoothed = planner.smooth_path(path, seed=42)
        for wp in smoothed:
            assert planner._within_limits(wp), \
                f"Smoothed waypoint {wp} violates joint limits"

    def test_smooth_short_path(self, planner):
        """Smoothing a 2-point path should return it unchanged."""
        path = [np.array([0.0] * 5), np.array([10.0] * 5)]
        smoothed = planner.smooth_path(path, seed=42)
        assert len(smoothed) == 2


class TestWithinLimits:
    """Test the joint limit checking utility."""

    def test_within_limits_valid(self, planner):
        assert planner._within_limits(np.array([0.0] * 5)) is True

    def test_within_limits_at_boundary(self, planner):
        assert planner._within_limits(np.array([180.0] * 5)) is True
        assert planner._within_limits(np.array([-180.0] * 5)) is True

    def test_within_limits_exceeded(self, planner):
        assert planner._within_limits(np.array([181.0, 0, 0, 0, 0])) is False
        assert planner._within_limits(np.array([0, 0, 0, 0, -181.0])) is False
