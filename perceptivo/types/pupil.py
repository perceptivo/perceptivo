"""
Types specifically for carrying and manipulating pupil measurements
"""
import typing
# from dataclasses import dataclass
from datetime import datetime

from pydantic.dataclasses import dataclass
from pydantic import BaseModel

import numpy as np

from perceptivo.types.sound import Sound
from perceptivo.types.units import Ellipse
from perceptivo.types.video import Frame


@dataclass
class Pupil:
    """
    A single-frame measurement of a pupil

    Attributes:
        ellipse (:class:`.Ellipse`): Fit ellipse given frame
        params (:class:`.Pupil_Params`): Pupil parameterization!
    """
    ellipse: Ellipse
    frame: Frame


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
    A timeseries of pupil diameters and timestamps corresponding to a pupil dilation event

    Attributes:
        ellipses (typing.List[Pupil]): List of ellipses from a pupil measurement
        timestamps (typing.List[datetime.datetime]): List of timestamps of equal length to ``ellipses``
        sound (:class:`.types.sound.Sound`): Sound that was presented for this pupil response

    Properties:
        max_diameter (float): maximum diameter reached during a given sample
        diameters (typing.List[float]): List of diameters in pixels of equal length to ``timestamps``
        response (bool): True/False whether the sound was heard, calculated by dividing
            the maximum measured pupil dilation in pixels / maximum possible dilation in pixels
            and comparing to the detection threshold. Aka
            ( :attr:`.Dilation.max_diameter` / :attr:`.Pupil_Params.max_diameter` ) >
            :attr:`.Pupil_Params.threshold`
    """

    params: Pupil_Params
    sound: Sound
    pupils: typing.List[Pupil]
    timestamps: typing.List[datetime]

    @property
    def diameters(self) -> typing.List[float]:
        """
        Extract major axes from ellipses

        Returns:
            typing.List[float]: List of major axes in pixels
        """
        return [pupil.ellipse.a for pupil in self.pupils]

    @property
    def max_diameter(self) -> float:
        return np.max(self.diameters)

    @property
    def response(self) -> bool:
        return (self.max_diameter / self.params.max_diameter) > self.params.threshold

