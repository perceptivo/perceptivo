from dataclasses import field
from enum import Enum
from pydantic.dataclasses import dataclass
from pydantic import BaseModel, Field
from datetime import datetime
import typing

import numpy as np
import cv2



class Frame(BaseModel):
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
    color: bool = True
    cropped: typing.Optional['Frame'] = None


    def __post_init__(self):
        self._color = None
        self._gray = None
        self._norm = None
        self.dtype = self.frame.dtype
        if self.color:
            self._color = self.frame
        else:
            self._gray = self.frame


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


class Color_Mode(Enum):
    rgb = 'rgb'
    grayscale = 'grayscale'


class Picamera_Params(BaseModel):
    """
    Configuration for a :class:`perceptivo.video.cameras.PiCamera`
    """
    sensor_mode: int = 0
    resolution: typing.Tuple[int, int] = (1280, 720)
    fps: int = 30
    format: Color_Mode = 'grayscale'




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