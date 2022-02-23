"""
Main Gui container for Perceptivo Clinician interface


"""
from typing import Optional
from PySide6 import QtWidgets
from PySide6.QtCore import Signal, Slot, QThread
from importlib.metadata import version
import threading

from perceptivo.gui import widgets
from perceptivo.root import Perceptivo_Object
from perceptivo.prefs import Clinician_Prefs
from perceptivo.networking.node import Node
from perceptivo.data.logging import init_logger

from perceptivo.types.networking import Clinician_Networking, Socket
from perceptivo.types.video import Frame

class Perceptivo_Clinician(QtWidgets.QMainWindow):
    """
    GUI container for the Perceptivo clinician interface
    """

    def __init__(self,
                 prefs: Clinician_Prefs,
                 networking: Clinician_Networking):
        super(Perceptivo_Clinician, self).__init__()
        self.prefs = prefs
        self.networking = networking
        self.logger = init_logger(self)

        self._settings = None

        self.layout = QtWidgets.QGridLayout() # type: QtWidgets.QGridLayout
        self.widget = QtWidgets.QWidget() # type: QtWidgets.QWidget

        self.control_panel = None # type: Optional[widgets.Control_Panel]
        self.pupil_ts = None # type: Optional[widgets.Pupil]
        self.vid_pupil = None # type: Optional[widgets.Video]
        self.vid_patient = None # type: Optional[widgets.Video]
        self.audiogram = None # type: Optional[widgets.Audiogram]

        self.frame_receiver = None # type: Optional[Perceptivo_Clinician.Frame_Receiver]

        self.state = {
            'frequencies': tuple(),
            'amplitudes': tuple()
        }

        self._init_ui()
        self._init_networking()
        self._init_signals()


        self.show()



    def _init_ui(self):

        self.setCentralWidget(self.widget)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0,0,0,0)
        self.widget.setLayout(self.layout)

        self.setWindowTitle(f'Perceptivo - v{version("perceptivo")}')

        # add widgets!
        self.control_panel = widgets.Control_Panel()
        self.audiogram = widgets.Audiogram()
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
        self.frame_receiver = self.Frame_Receiver(self, self.networking.eyecam)
        self.frame_receiver.start()

    def _init_signals(self):
        self.control_panel.valueChanged.connect(self.audiogram.gridChanged)
        self.control_panel.scaleChanged.connect(self.audiogram.scaleChanged)

        self.control_panel.startToggled.connect(self.setStarted)

        self.frame_receiver.frame.connect(self.drawFrame)

    def update_grid(self, value):
        pass


    @Slot(bool)
    def setStarted(self, value:bool):
        self.logger.debug(f"Setting start value to {value}")

    @property
    def settings(self):
        """Load and return :class:`PySide6.QtCore.QSettings`"""
        # TODO
        return self._settings

    @Slot(Frame)
    def drawFrame(self, frame:Frame):
        self.vid_pupil.setImage(frame.frame)
        self.logger.debug(f'got frame {frame}')


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
            self.quitting = threading.Event()
            self.logger = init_logger(self)

        def run(self):
            self.socket = Node(
                socket=self.socket_prefs,
                poll_mode=Node.Poll_Mode.NONE,
            )
            try:
                while not self.quitting.is_set():
                    try:
                        frame = self.socket.socket.recv()
                        self.frame.emit(frame)
                    except Exception as e:
                        self.logger.debug(f'Exception getting frame, {e}')

            finally:
                self.socket.release()

        @Slot()
        def quit(self):
            self.quitting.set()





