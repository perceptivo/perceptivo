from dataclasses import dataclass
from datetime import datetime

import numpy as np


@dataclass
class Frame:
    """
    Single video frame container

    Attributes:
        frame (:class:`numpy.ndarray`): Frame!
        timestamp (:class:`datetime.datetime`): Time of acquisition
        color (bool): If ``False`` , grayscale (frame should be 2 dimensional or 3rd axis should be len  == 1 ).
            if ``True``, RGB Color.
    """
    frame: np.ndarray
    timestamp: datetime
    color: bool = False


@dataclass
class Picamera_Params:
    """
    Configuration for a :class:`perceptivo.video.cameras.PiCamera`
    """

@dataclass
class Camera_Calibration:
    """
    Parameters that define the conditions of use for a camera

    Args:
        picam (:class:`.Picamera_Params`): Parameterization of the PiCamera
        distance (float): distance from camera to subject in mm
        mm_per_px (float): approximate number of mm per pixel at a given distance
    """
    picam: Picamera_Params
    distance: float
    mm_per_px: float