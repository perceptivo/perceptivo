"""
Process and extract pupil
"""

from abc import abstractmethod, abstractproperty

from perceptivo.root import Perceptivo_Object

class PupilExtractor(Perceptivo_Object):
    """
    Base class for pupil extraction strategies.
    """

    def __init__(self, **kwargs):
        super(PupilExtractor, self).__init__(**kwargs)

