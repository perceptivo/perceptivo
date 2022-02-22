"""
Picamera capture. Easy enough with Autopilot
"""
import typing
from typing import Optional
from queue import Empty, Full
from autopilot.hardware.cameras import PiCamera
import multiprocessing as mp
from perceptivo.types.video import Picamera_Params, Frame
from perceptivo.root import Perceptivo_Object
from datetime import datetime

class Picamera_Process(mp.Process, Perceptivo_Object):
    """
    Separate process for the picamera
    """

    def __init__(self,
                 params:Picamera_Params = Picamera_Params(),
                 queue_size:int = 1024,
                 **kwargs):
        super(Picamera_Process, self).__init__(**kwargs)
        self.params = params

        self.queue_size = queue_size

        self.q = mp.Queue(maxsize=queue_size)
        """
        Queue for the parent runtime to grab frames from the
        picamera.
        """

        self.collecting = mp.Event()
        """
        Event set when collecting a sample. when set, 
        dump frames into :attr:`.Picamera_Process.q`
        """

        self._closing = mp.Event()

        self.cam = None # type: typing.Optional[PiCamera]

    def run(self):

        self.cam = PiCamera(**self.params.dict())
        self.cam.queue(self.queue_size)
        self.cam.queueing.clear()
        self.cam.capture()

        if self.params.format == "grayscale":
            color = False
        else:
            color = True

        try:
            while not self._closing.is_set():
                if self.collecting.is_set():
                    self.cam.queueing.set()
                    try:
                        timestamp, frame = self.cam.q.get_nowait()
                    except Empty:
                        self.logger.debug('Queue was empty!')
                        continue

                    frame = Frame(
                        frame=frame,
                        timestamp=datetime.fromisoformat(timestamp),
                        color = color
                    )
                    try:
                        self.q.put_nowait(frame)
                    except Full:
                        self.logger.exception(f'Couldnt put frame in queue because it was full')

                else:
                    self.cam.queueing.clear()

        finally:
            # deinitialize camera
            self.cam.stopping.set()


    def release(self):
        """
        Stop running and release picamera resources
        """
        self._closing.set()



