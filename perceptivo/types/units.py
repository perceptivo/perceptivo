"""
Very basic units or unit-like things
"""
from dataclasses import dataclass
import typing
from skimage.draw import ellipse
import numpy as np


@dataclass
class Ellipse:
    """
    Parameterization of an ellipse corresponding to a Pupil

    .. todo:

        We should wrap :class:`skimage.measure.EllipseModel` here

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

    def mask(self, scale:float=1) -> typing.Tuple[np.ndarray, np.ndarray]:
        """
        Coordinates for a boolean mask, created with :func:`skimage.draw.ellipse`

        .. note::

            When calling ellipse, :attr:`.y` is used as the 0th dimension and :attr:`.x` as the 1st,
            since rows in a frame (y) are typically the 0th dimension.

        Args:
            scale (float): Scale the major and minor axes by this much!

        Returns:
            tuple of two ndarrays, coordinates in the 0th and 1st axis of the mask points
        """
        return ellipse(self.y, self.x, self.b*scale, self.a*scale, rotation=self.t)


