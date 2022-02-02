"""
Process and extract pupil

Sketch of default strategy:

* Track to find approximate position of eyes with :class:`.processors.Haar_Tracker`
* Mask image around both eyes, split processing in parallel L/R (if present)
* Use white of eyes to mask cornea and pupil
* Sigmoid filter images to separate cornea and pupil
* Blob detection to find center mass of pupil
* Compare blob vs. edge detection of pupil.
* Use Kalman filter on :class:`perceptivo.types.units.Ellipse` properties to avoid
  jumps and all that

"""
import typing
from abc import abstractmethod
from typing import Union, Optional, List, Dict

from perceptivo.root import Perceptivo_Object

if typing.TYPE_CHECKING:
    from perceptivo.types.video import Frame
    from perceptivo.video.processors import Processor
    from perceptivo.types.pupil import Pupil


class PupilExtractor(Perceptivo_Object):
    """
    Base class for pupil extraction strategies.
    """

    def __init__(self, processors:List[Processor],  **kwargs):
        super(PupilExtractor, self).__init__(**kwargs)



    @abstractmethod
    def process(self, frame:Frame) -> Pupil:
        """
        Given a frame, extract a pupil estimate

        Args:
            Frame ():

        Returns:

        """

