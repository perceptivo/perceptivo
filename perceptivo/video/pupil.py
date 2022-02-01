"""
Process and extract pupil
"""

from abc import abstractmethod

from perceptivo.root import Perceptivo_Object
from perceptivo.types.video import Frame
from perceptivo.types.pupil import Pupil


class PupilExtractor(Perceptivo_Object):
    """
    Base class for pupil extraction strategies.
    """

    def __init__(self, **kwargs):
        super(PupilExtractor, self).__init__(**kwargs)

    @abstractmethod
    def process(self, Frame) -> Pupil:
        """
        Given a frame, extract a pupil estimate

        Args:
            Frame ():

        Returns:

        """
