from dataclasses import dataclass
from datetime import datetime

import numpy as np


@dataclass
class Frame:
    """
    Single video frame container
    """
    frame: np.ndarray
    timestamp: datetime


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