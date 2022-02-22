"""
Picamera capture. Easy enough with Autopilot
"""

from autopilot.hardware.cameras import PiCamera
import multiprocessing as mp
from perceptivo.types.video import Picamera_Params

class Picamera_Process(mp.Process):
    """
    Separate process to interact with picamera with a


    """


