import typing
from dataclasses import dataclass, field
from datetime import datetime

import numpy as np

from perceptivo.types.sound import Sound


@dataclass
class Pupil_Params:
    """
    Parameters to use with :class:`.video.pupil.PupilExtractor` classes to
    parameterize

    Attributes:
        threshold (float): Diameter threshold as a fraction of maximum diameter to consider
            a positive response to a stimulus
        max_diameter (float): Maximum diameter of pupil in pixels
    """
    threshold: float
    max_diameter: float

@dataclass
class Dilation:
    """
    A timeseries of pupil diameters and timestamps corresponding to a pupil dilation

    Attributes:
        diameters (typing.List[float]): List of diameters in pixels of equal length to ``timestamps``
        timestamps (typing.List[datetime.datetime]): List of timestamps of equal length to ``diameters``

    Properties:
        max_diameter (float): maximum diameter reached during a given sample
    """
    diameters: typing.List[float]
    timestamps: typing.List[datetime]

    @property
    def max_diameter(self) -> float:
        return np.max(self.diameters)


@dataclass
class Pupil:
    """
    A measurement of a single pupil dilation event

    Attributes:
        sound (:class:`.types.sound.Sound`): Sound that was presented for this pupil response

    """
    sound: Sound
    dilation: Dilation
    params: Pupil_Params

    @property
    def response(self) -> bool:
        return (self.dilation.max_diameter / self.params.max_diameter) > self.params.threshold

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