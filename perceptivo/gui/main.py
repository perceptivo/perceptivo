"""
Main Gui container for Perceptivo Clinician interface


"""
import sys
from typing import Optional, Dict
import cv2

import numpy as np
from PySide6 import QtWidgets
from PySide6.QtCore import Signal, Slot, QThread, QTimer
from importlib.metadata import version
import threading
import zmq

from perceptivo.gui import widgets
from perceptivo.root import Perceptivo_Object
from perceptivo.prefs import Clinician_Prefs
from perceptivo.networking.node import Node
from perceptivo.networking.messages import Message
from perceptivo.data.logging import init_logger

from perceptivo.types.networking import Clinician_Networking, Socket
from perceptivo.types.video import Frame
from perceptivo.types.gui import GUI_Control
from perceptivo.types.psychophys import Samples
from perceptivo.types.exam import Exam_Params

class Perceptivo_Clinician(QtWidgets.QMainWindow):
    """
    GUI container for the Perceptivo clinician interface
    """
    quitting = Signal()
    launched = Signal()
    controlChanged = Signal(GUI_Control)

    def __init__(self,
                 prefs: Clinician_Prefs,
                 networking: Clinician_Networking,
                 update_period:Optional[float]=None):
        super(Perceptivo_Clinician, self).__init__()
        self.prefs = prefs
        self.networking = networking

        if update_period is not None:
            self.update_period = update_period
        else:
            self.update_period = self.prefs.update_period

        self.logger = init_logger(self)

        self._settings = None

        self.layout = QtWidgets.QGridLayout() # type: QtWidgets.QGridLayout
        self.widget = QtWidgets.QWidget() # type: QtWidgets.QWidget

        self.control_panel = None # type: Optional[widgets.Control_Panel]
        self.pupil_ts = None # type: Optional[widgets.Pupil]
        self.vid_pupil = None # type: Optional[widgets.Video]
        self.vid_patient = None # type: Optional[widgets.Video]
        self.audiogram = None # type: Optional[widgets.Audiogram]
        self.samples = None # type: Optional[Samples]
        self._started = False

        self.frame_receiver = None # type: Optional[Perceptivo_Clinician.Frame_Receiver]

        self.state = {
            'frequencies': tuple(),
            'amplitudes': tuple()
        }

        self.callbacks = {
            'CONNECT': self.cb_connect,
            'DATA': self.cb_data
        }

        self.senders = []

        self._init_ui()
        self._init_networking()
        self._init_signals()

        # make timer to check for messages
        self.msg_timer = QTimer()
        self.msg_timer.setSingleShot(True)
        self.msg_timer.timeout.connect(self.receive_messages)
        self.msg_timer.setInterval(self.update_period*1000)


        self.show()
        self.launched.emit()
        self.receive_messages()


    def _init_ui(self):

        self.setCentralWidget(self.widget)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0,0,0,0)
        self.widget.setLayout(self.layout)

        self.setWindowTitle(f'Perceptivo - v{version("perceptivo")}')

        # add widgets!
        self.control_panel = widgets.Control_Panel(self.prefs.gui.control_panel)
        self.audiogram = widgets.Audiogram(
            default_amplitudes=self.control_panel.widgets['amplitude_range'].value(),
            default_frequencies=self.control_panel.widgets['frequency_range'].value()
        )
        self.pupil_ts = widgets.Pupil()
        self.vid_pupil = widgets.Video()
        self.vid_patient = widgets.Video()

        # layout widgets!
        self.layout.addWidget(self.control_panel, 0, 0)
        self.layout.addWidget(self.audiogram, 0, 1)
        self.layout.addWidget(self.vid_patient, 0, 2)
        self.layout.addWidget(self.pupil_ts, 1, 0, 1, 2)
        self.layout.addWidget(self.vid_pupil, 1, 2)
        self.layout.setColumnStretch(0, 1)
        self.layout.setColumnStretch(1, 1)
        self.layout.setColumnStretch(2, 1)

    def _init_networking(self):
        if 'pytest' not in sys.modules:
            self.frame_receiver = self.Frame_Receiver(self, self.networking.eyecam)
            self.frame_receiver.start()

        self.node = Node(
            self.networking.control,
            poll_mode=Node.Poll_Mode.NONE
        )

    def _init_signals(self):
        # signals coming into the GUI
        self.control_panel.valueChanged.connect(self.audiogram.gridChanged)
        self.control_panel.scaleChanged.connect(self.audiogram.scaleChanged)

        self.control_panel.valueChanged.connect(self.changeControl)


        self.control_panel.startToggled.connect(self.setStarted)

        # Signals leaving the GUI

        if 'pytest' not in sys.modules:
            self.frame_receiver.frame.connect(self.drawFrame)
            self.quitting.connect(self.frame_receiver.quitting)

    @Slot(GUI_Control)
    def changeControl(self, value:GUI_Control):
        """
        Receive changed control settings from widgets, etc. and emit them to
        the patient.

        Also emits from the :attr:`.controlChanged` signal

        Args:
            value (:class:`.types.gui.GUI_Control`): Control value that changed
        """
        # create a message to send to patient
        msg = Message(control=value, key="CONTROL")
        self.node.send(
            to="patient:control",
            msg=msg
        )
        self.controlChanged.emit(value)


    @Slot(bool)
    def setStarted(self, value:bool):
        self.logger.debug(f"Setting start value to {value}")
        if value:
            # starting!
            if self._started:
                self.logger.exception("Already started exam")
                return
            self._start_exam()
            self._started = True
        else:
            # stopping!
            if not self._started:
                self.logger.exception("Exam not started, cant stop")
                return
            self._stop_exam()
            self._started = False

    @property
    def exam_params(self) -> Exam_Params:
        return Exam_Params(
            frequencies=self.control_panel.widgets['frequency_range'].value(),
            amplitudes=self.control_panel.widgets['amplitude_range'].value(),
            iti=self.control_panel.widgets['iti'].value(),
            iti_jitter=self.control_panel.widgets['iti'].value()
        )


    def _start_exam(self):
        msg = Message(key='START', params=self.exam_params)
        self.node.send(msg=msg, to='patient:control')


    def _stop_exam(self):
        self.node.send(Message(key='STOP'), to="patient:control")
        self.logger.debug('sent stop message to patient')

    @property
    def settings(self):
        """Load and return :class:`PySide6.QtCore.QSettings`"""
        # TODO
        return self._settings

    @Slot(Frame)
    def drawFrame(self, frame):
        frame = np.frombuffer(frame, dtype='uint8')
        self.vid_pupil.setImage(cv2.imdecode(frame, -1))
        # frame = Message.from_serialized(frame).value['frame']
        # self.vid_pupil.setImage(frame.frame)


    def receive_messages(self):

        try:

            msg = self.node.socket.recv_multipart(flags=zmq.NOBLOCK)
            msg = Message.from_serialized(msg[-1])

            self.logger.debug(f'Received message: {msg}')

            if msg.key in self.callbacks.keys():
                self.callbacks[msg.key](msg)
                self.logger.debug(f"Called callback for key {msg.key}")

        except zmq.ZMQError as e:
            if str(e) == 'Resource temporarily unavailable':
                pass
                # no messages to process
            else:
                raise e

        finally:
            self.msg_timer.start()

    def cb_connect(self, msg:Message):
        """

        Args:
            msg ():

        Returns:

        """
        self.senders.append(msg.value['id'])
        self.logger.info(f'Received connection from {msg.value["id"]}')

    def cb_data(self, msg:Message):
        """
        Receive data from the patient during an exam

        Message that contains a :class:`.types.psychophys.Sample`
        """
        sample = msg.value['sample']
        kernel = msg.value['kernel']



    def closeEvent(self, event):
        self.quitting.emit()
        self.frame_receiver.exit()
        self.frame_receiver.quitting_evt.set()
        self.msg_timer.stop()
        self.frame_receiver.wait(5)
        event.accept()


    class Frame_Receiver(QThread):
        """
        Thread to launch a networking node, receive threads, and emit new frames
        """
        frame = Signal(Frame)

        def __init__(self,
                     parent,
                     socket_prefs:Socket):
            super(Perceptivo_Clinician.Frame_Receiver, self).__init__(parent)
            self.socket_prefs = socket_prefs
            self.logger = init_logger(self)

            self.quitting_evt = threading.Event()

        def run(self):

            self.logger.debug('starting frame receiver thread')
            self.socket = Node(
                socket=self.socket_prefs,
                poll_mode=Node.Poll_Mode.NONE,
            )
            try:
                while not self.quitting_evt.is_set():
                    try:
                        frame = self.socket.socket.recv()
                        self.frame.emit(frame)
                    except Exception as e:
                        self.logger.debug(f'Exception getting frame, {e}')

            finally:
                self.logger.debug('releasing socket')
                self.socket.release()


        @Slot()
        def quitting(self):
            self.logger.debug('got quit signal')
            self.quitting_evt.set()





