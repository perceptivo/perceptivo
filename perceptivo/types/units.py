"""
Very basic units or unit-like things
"""
from dataclasses import dataclass


@dataclass
class Ellipse:
    """
    Parameterization of an ellipse corresponding to a Pupil

    Attrs:
        x (int): Ellipse center in pixels
        y (int): Ellipse center in pixels
        a (float): Major axis in pixels
        b (float): Minor axis in pixels
        t (float): Orientation in radians, clockwise from vertical
    """

    x: int
    y: int
    a: float
    b: float
    t: float