"""
Cursive writing mode using cubic Bezier curves.

Generates connected letterforms where the pen does not lift between
letters within a word. Each letter is defined by a sequence of
cubic Bezier control points. The end point of each letter connects
to the start of the next via a ligature curve.

Cubic Bezier: B(t) = (1-t)^3*P0 + 3*(1-t)^2*t*P1 + 3*(1-t)*t^2*P2 + t^3*P3
"""
import numpy as np
from typing import List, Tuple, Optional

# Cursive letter definitions: each letter is a list of Bezier segments
# Each segment: (P0, P1, P2, P3) as normalized coordinates in [0,1]^2
# P0 = start, P3 = end, P1/P2 = control points

CURSIVE_ALPHABET = {
    'a': [
        ((0.8, 0.5), (0.8, 1.0), (0.2, 1.0), (0.2, 0.5)),
        ((0.2, 0.5), (0.2, 0.0), (0.8, 0.0), (0.8, 0.5)),
        ((0.8, 0.5), (0.8, 0.0), (1.0, 0.0), (1.0, 0.0)),
    ],
    'b': [
        ((0.0, 0.0), (0.0, 0.5), (0.0, 1.0), (0.2, 1.0)),
        ((0.2, 1.0), (0.2, 0.5), (0.2, 0.5), (0.2, 0.5)),
        ((0.2, 0.5), (0.8, 0.5), (0.8, 1.0), (0.5, 1.0)),
        ((0.5, 1.0), (0.2, 1.0), (0.2, 0.5), (1.0, 0.0)),
    ],
    'c': [
        ((0.8, 0.8), (0.8, 1.0), (0.2, 1.0), (0.2, 0.5)),
        ((0.2, 0.5), (0.2, 0.0), (0.8, 0.0), (0.8, 0.2)),
    ],
    # ... more letters
}


# Simplified: generate basic shapes for all 26 letters
def _generate_default_alphabet():
    """Generate simple cursive forms for all lowercase letters."""
    alpha = {}
    for i, ch in enumerate('abcdefghijklmnopqrstuvwxyz'):
        if ch in CURSIVE_ALPHABET:
            continue
        # Default: a simple loop
        phase = i * 0.1
        alpha[ch] = [
            ((0.0, 0.0), (0.0, 0.8 + phase), (0.5, 1.0), (0.5, 0.5)),
            ((0.5, 0.5), (0.5, 0.0), (1.0, 0.0 - phase * 0.5), (1.0, 0.0)),
        ]
    CURSIVE_ALPHABET.update(alpha)


_generate_default_alphabet()


def cubic_bezier(p0, p1, p2, p3, n_points=20):
    """Evaluate cubic Bezier curve at n_points.

    B(t) = (1-t)^3*P0 + 3*(1-t)^2*t*P1 + 3*(1-t)*t^2*P2 + t^3*P3

    Args:
        p0: Start point (x, y).
        p1: First control point.
        p2: Second control point.
        p3: End point.
        n_points: Number of points to evaluate.

    Returns:
        Array of shape (n_points, 2) with evaluated points.
    """
    t = np.linspace(0, 1, n_points)
    p0, p1, p2, p3 = np.array(p0), np.array(p1), np.array(p2), np.array(p3)
    points = ((1 - t) ** 3)[:, None] * p0 + \
             (3 * (1 - t) ** 2 * t)[:, None] * p1 + \
             (3 * (1 - t) * t ** 2)[:, None] * p2 + \
             (t ** 3)[:, None] * p3
    return points


def generate_cursive_path(text: str, letter_width: float = 15.0,
                           letter_height: float = 20.0,
                           spacing: float = 2.0,
                           points_per_segment: int = 15) -> list:
    """Generate a continuous 2D path for cursive text.

    Args:
        text: String to write (lowercase).
        letter_width: Width of each letter in mm.
        letter_height: Height of each letter in mm.
        spacing: Extra spacing between letters in mm.
        points_per_segment: Points per Bezier segment.

    Returns:
        List of (x, y) tuples forming the continuous path.
        Pen-up events indicated by None entries.
    """
    text = text.lower()
    path: list = []
    x_offset = 0.0

    for i, ch in enumerate(text):
        if ch == ' ':
            x_offset += letter_width * 0.5
            path.append(None)  # pen up
            continue

        if ch not in CURSIVE_ALPHABET:
            x_offset += letter_width + spacing
            continue

        segments = CURSIVE_ALPHABET[ch]
        for seg in segments:
            p0 = (seg[0][0] * letter_width + x_offset, seg[0][1] * letter_height)
            p1 = (seg[1][0] * letter_width + x_offset, seg[1][1] * letter_height)
            p2 = (seg[2][0] * letter_width + x_offset, seg[2][1] * letter_height)
            p3 = (seg[3][0] * letter_width + x_offset, seg[3][1] * letter_height)

            points = cubic_bezier(p0, p1, p2, p3, points_per_segment)
            for pt in points:
                path.append((float(pt[0]), float(pt[1])))

        x_offset += letter_width + spacing

    return path
