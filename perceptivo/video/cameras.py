"""
Picamera capture. Easy enough with Autopilot
"""
import typing
from typing import Optional
from queue import Empty, Full

import cv2
from autopilot.hardware.cameras import PiCamera
import multiprocessing as mp
from perceptivo.types.video import Picamera_Params, Frame
from perceptivo.types.networking import Socket
from perceptivo.root import Perceptivo_Object
from perceptivo.networking.node import Node
from perceptivo.networking.messages import Message
from perceptivo.data.logging import init_logger
from datetime import datetime

class Picamera_Process(mp.Process, Perceptivo_Object):
    """
    Separate process for the picamera
    """

    def __init__(self,
                 params:Picamera_Params = Picamera_Params(),
                 networking: Optional[Socket] = None,
                 queue_size:int = 1024,
                 **kwargs):
        super(Picamera_Process, self).__init__(daemon=True,**kwargs)
        self.params = params
        self.networking = networking

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

        self.node = None # type: Optional[Node]

    def run(self):
        # reinint logger
        self._logger = init_logger(self)

        if self.networking is not None:
            self.node = Node(
                self.networking,
                poll_mode=Node.Poll_Mode.NONE,
            )

        self.cam = PiCamera(**self.params.dict())
        self.cam.queue(self.queue_size)
        self.cam.queueing.clear()

        if self.params.output_file is not None:
            if self.params.output_file.exists():
                self.logger.debug('Prior output file exists, deleting...')
                self.params.output_file.unlink()
                self.cam.write(str(self.params.output_file))
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
                        timestamp, frame = self.cam.q.get(timeout=1/self.params.fps)
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

                    # passively clear q so when we start capturing again we're not processing stale frames
                    try:
                        _ = self.cam.q.get_nowait()
                    except Empty:
                        pass

                    # just make a frame to stream if we can
                    try:
                        timestamp, frame = self.cam.frame
                    except TypeError:
                        continue
                    frame = Frame(
                        frame = frame,
                        timestamp = datetime.fromisoformat(timestamp),
                        color=color
                    )

                if self.node is not None:
                    _, jpg_buf = cv2.imencode('.jpg', frame.frame)
                    self.node.socket.send(jpg_buf)

        finally:
            # deinitialize camera
            self.cam.stopping.set()


    def release(self):
        """
        Stop running and release picamera resources
        """
        self._closing.set()



