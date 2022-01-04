from abc import abstractmethod
from perceptivo.root import Perceptivo_Object

class Calibration(Perceptivo_Object):
    """
    Base class for calibration objects
    """

    @abstractmethod
    def calibrate(self, sound: 'perceptivo.types.sound.Sound') -> 'perceptivo.types.sound.Sound':
        """
        Take a 
        Args:
            sound ():

        Returns:

        """
