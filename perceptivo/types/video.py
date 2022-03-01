from dataclasses import field
from enum import Enum
from pydantic.dataclasses import dataclass
from pydantic import BaseModel, Field, PrivateAttr
from datetime import datetime
import typing
from pathlib import Path


import numpy as np
import cv2

from perceptivo.types.root import PerceptivoType

class Frame(PerceptivoType):
    """
    Single video frame container

    Attributes:
        frame (:class:`numpy.ndarray`): Frame!
        timestamp (:class:`datetime.datetime`): Time of acquisition
        color (bool): If ``False`` , grayscale (frame should be 2 dimensional or 3rd axis should be len  == 1 ).
            if ``True``, RGB Color.
    """
    frame: np.ndarray
    timestamp: datetime = Field(default_factory=datetime.now)
    color: typing.Optional[bool] = None
    cropped: typing.Optional['Frame'] = None
    _color: typing.Optional[np.ndarray] = None
    _gray: typing.Optional[np.ndarray] = None
    _norm: typing.Optional[np.ndarray] = None
    dtype: typing.Optional[np.dtype] = None

    def __init__(self, **data):
        super().__init__(**data)

        self._color = None
        self._gray = None
        self._norm = None
        self.dtype = self.frame.dtype
        # try to infer if it wasn't passed specifically
        if self.color is None:
            if len(self.frame.shape) == 3 and self.frame.shape[2] == 3:
                self.color = True
            else:
                self.color = False

        if self.color:
            self._color = self.frame
            self._gray = None
        else:
            self._gray = self.frame
            self._color = None


    def set_color(self, color):
        if color and not self.color:
            raise ValueError('Cant colorize grayscale images!')
        elif not color and self.color:
            self._color = self.frame.copy()
            gray = self.gray
            self.frame = gray
            self.color = color

    def norm(self):
        """make frame 0-1"""
        if self._norm is None:
            if self.frame.dtype == 'uint8':
                self._norm = self.frame.astype(float) / 255
                self.frame = self._norm
                self.dtype = 'float'

    @property
    def gray(self) -> np.ndarray:
        """
        Grayscale version of the frame, if color
        """
        if self._gray is None:
            if self.color:
                self._gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
            else:
                self._gray = self.frame
        return self._gray

    def crop(self, bbox:typing.List[int]):
        """
        Crop with a bounding box (top, bottom, left, right),
        assign to self.cropped

        Args:
            bbox ():

        Returns:
            new Frame image with cropped image as its frame
        """

        self.cropped = Frame(
            frame=self.frame[bbox[0]:bbox[1], bbox[2]:bbox[3]],
            timestamp=self.timestamp,
            color=self.color)

        return self.cropped

    class Config:
        arbitrary_types_allowed:bool = True


Color_Mode = typing.Literal['rgb', 'grayscale']


class Picamera_Params(BaseModel):
    """
    Configuration for a :class:`perceptivo.video.cameras.PiCamera`
    """
    sensor_mode: int = 0
    resolution: typing.Tuple[int, int] = (1280, 720)
    fps: int = 30
    format: Color_Mode = 'grayscale'
    output_file: typing.Optional[Path] = None




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