"""Tests for the cursive Bezier writing module."""

import numpy as np
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from src.core.cursive import (
    cubic_bezier,
    generate_cursive_path,
    CURSIVE_ALPHABET,
)
from src.api.main import app


# ── Unit tests for cursive module ─────────────────────────────────────────


class TestCubicBezier:
    """Tests for the cubic_bezier function."""

    def test_endpoints(self):
        """Bezier curve should start at P0 and end at P3."""
        p0, p1, p2, p3 = (0.0, 0.0), (1.0, 2.0), (3.0, 2.0), (4.0, 0.0)
        pts = cubic_bezier(p0, p1, p2, p3, n_points=50)
        assert pts.shape == (50, 2)
        np.testing.assert_allclose(pts[0], p0, atol=1e-10)
        np.testing.assert_allclose(pts[-1], p3, atol=1e-10)

    def test_straight_line(self):
        """Collinear control points should give a straight line."""
        p0, p3 = (0.0, 0.0), (10.0, 0.0)
        p1 = (3.33, 0.0)
        p2 = (6.67, 0.0)
        pts = cubic_bezier(p0, p1, p2, p3, n_points=20)
        # All y values should be zero
        np.testing.assert_allclose(pts[:, 1], 0.0, atol=1e-10)
        # x values should be monotonically increasing
        assert np.all(np.diff(pts[:, 0]) >= -1e-10)

    def test_output_shape(self):
        """Output shape should match n_points."""
        pts = cubic_bezier((0, 0), (1, 1), (2, 1), (3, 0), n_points=7)
        assert pts.shape == (7, 2)

    def test_single_point(self):
        """n_points=1 should return the start point."""
        pts = cubic_bezier((0, 0), (1, 1), (2, 1), (3, 0), n_points=1)
        assert pts.shape == (1, 2)
        np.testing.assert_allclose(pts[0], (0, 0), atol=1e-10)


class TestCursiveAlphabet:
    """Tests for the cursive alphabet definition."""

    def test_all_lowercase_present(self):
        """All 26 lowercase letters should have entries."""
        for ch in 'abcdefghijklmnopqrstuvwxyz':
            assert ch in CURSIVE_ALPHABET, f"Missing letter: {ch}"

    def test_segments_structure(self):
        """Each letter should have at least one segment with 4 control points."""
        for ch, segments in CURSIVE_ALPHABET.items():
            assert len(segments) > 0, f"Letter '{ch}' has no segments"
            for i, seg in enumerate(segments):
                assert len(seg) == 4, (
                    f"Letter '{ch}' segment {i} should have 4 control points, "
                    f"got {len(seg)}"
                )
                for j, pt in enumerate(seg):
                    assert len(pt) == 2, (
                        f"Letter '{ch}' segment {i} point {j} should be 2D"
                    )


class TestGenerateCursivePath:
    """Tests for the generate_cursive_path function."""

    def test_single_letter(self):
        """Single letter should produce a non-empty path."""
        path = generate_cursive_path("a")
        points = [p for p in path if p is not None]
        assert len(points) > 0

    def test_word(self):
        """A word should produce points for each letter."""
        path = generate_cursive_path("hello")
        points = [p for p in path if p is not None]
        assert len(points) > 10

    def test_space_produces_pen_up(self):
        """Spaces should insert None (pen-up) markers."""
        path = generate_cursive_path("a b")
        assert None in path

    def test_uppercase_lowered(self):
        """Uppercase input should be lowered automatically."""
        path_upper = generate_cursive_path("HELLO")
        path_lower = generate_cursive_path("hello")
        # Same letter sequence, same path
        assert len(path_upper) == len(path_lower)

    def test_points_are_tuples(self):
        """Non-None points should be (x, y) tuples of floats."""
        path = generate_cursive_path("abc")
        for pt in path:
            if pt is not None:
                assert len(pt) == 2
                assert isinstance(pt[0], float)
                assert isinstance(pt[1], float)

    def test_x_increases(self):
        """Overall x coordinate should increase across letters."""
        path = generate_cursive_path("abc")
        points = [p for p in path if p is not None]
        # First point of 'a' should be left of last point of 'c'
        assert points[-1][0] > points[0][0]

    def test_custom_dimensions(self):
        """Custom letter dimensions should scale the output."""
        path_small = generate_cursive_path("a", letter_width=10, letter_height=10)
        path_large = generate_cursive_path("a", letter_width=30, letter_height=30)
        pts_small = [p for p in path_small if p is not None]
        pts_large = [p for p in path_large if p is not None]
        # Max extent of large should be bigger than small
        max_x_small = max(p[0] for p in pts_small)
        max_x_large = max(p[0] for p in pts_large)
        assert max_x_large > max_x_small

    def test_empty_after_unknown_char(self):
        """Unknown characters (digits, symbols) should be skipped gracefully."""
        path = generate_cursive_path("a1b")
        # Should not crash, should still have points for 'a' and 'b'
        points = [p for p in path if p is not None]
        assert len(points) > 0


# ── API endpoint tests ────────────────────────────────────────────────────


@pytest.fixture
def transport():
    return ASGITransport(app=app)


@pytest_asyncio.fixture
async def client(transport):
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_cursive_path_endpoint(client):
    """GET /api/cursive-path should return a valid path."""
    response = await client.get("/api/cursive-path", params={"text": "hello"})
    assert response.status_code == 200
    data = response.json()
    assert data["text"] == "hello"
    assert data["total_points"] > 0
    assert data["num_segments"] >= 1
    assert len(data["segments"]) == data["num_segments"]
    # Each segment should have points with x, y
    for seg in data["segments"]:
        assert len(seg) > 0
        assert "x" in seg[0]
        assert "y" in seg[0]


@pytest.mark.asyncio
async def test_cursive_path_with_spaces(client):
    """Text with spaces should produce multiple segments."""
    response = await client.get("/api/cursive-path", params={"text": "hi there"})
    assert response.status_code == 200
    data = response.json()
    assert data["num_segments"] >= 2


@pytest.mark.asyncio
async def test_cursive_path_empty_text(client):
    """Empty text should return 400."""
    response = await client.get("/api/cursive-path", params={"text": ""})
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_cursive_path_custom_params(client):
    """Custom dimensions should be accepted."""
    response = await client.get(
        "/api/cursive-path",
        params={"text": "ab", "letter_width": 20, "letter_height": 30, "spacing": 5},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_points"] > 0
