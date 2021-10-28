"""
Main Gui container for Perceptivo Clinician interface


"""
from typing import Optional
from PySide6 import QtWidgets
from PySide6.QtCore import Signal, Slot
from importlib.metadata import version
from perceptivo.gui import widgets
from perceptivo.root import Perceptivo_Object

class Perceptivo_Clinician(QtWidgets.QMainWindow, Perceptivo_Object):
    """
    GUI container for the Perceptivo clinician interface
    """

    def __init__(self):
        super(Perceptivo_Clinician, self).__init__()

        self._settings = None

        self.layout = QtWidgets.QGridLayout() # type: QtWidgets.QGridLayout
        self.widget = QtWidgets.QWidget() # type: QtWidgets.QWidget

        self.control_panel = None # type: Optional[widgets.Control_Panel]
        self.pupil_ts = None # type: Optional[widgets.Pupil]
        self.vid_pupil = None # type: Optional[widgets.Video]
        self.vid_patient = None # type: Optional[widgets.Video]
        self.audiogram = None # type: import perceptivo.types.sound
Optional[perceptivo.types.sound.Audiogram]

        self.state = {
            'frequencies': tuple(),
            'amplitudes': tuple()
        }

        self._init_ui()
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

    def _init_signals(self):
        self.control_panel.valueChanged.connect(self.audiogram.gridChanged)
        self.control_panel.scaleChanged.connect(self.audiogram.scaleChanged)

        self.control_panel.startToggled.connect(self.setStarted)

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


