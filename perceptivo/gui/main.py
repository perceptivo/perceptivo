"""
Main Gui container for Perceptivo Clinician interface


"""
from typing import Optional
from PySide6 import QtWidgets
from importlib.metadata import version
from perceptivo.gui import widgets

class Perceptivo_Clinician(QtWidgets.QMainWindow):
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
        self.audiogram = None # type: Optional[widgets.Audiogram]

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

    def update_grid(self, value):
        pass




    @property
    def settings(self):
        """Load and return :class:`PySide6.QtCore.QSettings`"""
        # TODO
        return self._settings


