"""
Control operation of perceptivo, set audiogram params
"""

from PySide6 import QtWidgets
from PySide6.QtCore import Signal, Slot

from perceptivo.data import types
from perceptivo.gui.widgets.components import Range_Setter
from perceptivo.gui import params

class Control_Panel(QtWidgets.QGroupBox):

    valueChanged = Signal(types.GUI_Param)
    scaleChanged = Signal(types.GUI_Param)

    def __init__(self):
        super(Control_Panel, self).__init__('Control Panel')

        self._init_ui()

    def _init_ui(self):

        freq_params = params.CONTROL_PANEL['frequencies']
        amps_params = params.CONTROL_PANEL['amplitudes']

        self.freqs = Range_Setter(freq_params.key, freq_params.name, **freq_params.kwargs)
        self.amps = Range_Setter(amps_params.key, amps_params.name, **amps_params.kwargs)

        self.freqs.valueChanged.connect(self._valueChanged)
        self.amps.valueChanged.connect(self._valueChanged)
        self.freqs.scaleChanged.connect(self._scaleChanged)
        self.amps.scaleChanged.connect(self._scaleChanged)

        self.layout = QtWidgets.QVBoxLayout()

        self.layout.addWidget(self.freqs)
        self.layout.addWidget(self.amps)
        self.layout.addStretch(1)

        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)

    def _scaleChanged(self, value):
        sender = self.sender().key
        if sender == params.CONTROL_PANEL['frequencies'].key:
            key = 'log_x'
        elif sender == params.CONTROL_PANEL['amplitudes'].key:
            key = 'log_y'
        else:
            raise ValueError(f'Not sure who send the scale value, dont know how to parameterize it!')

        set_to = False
        if value == 'log':
            set_to = True

        self.scaleChanged.emit(types.GUI_Param(key, set_to))

    def _gridChanged(self):
        pass

    def _valueChanged(self, value: types.GUI_Param):
        self.valueChanged.emit(value)

    @Slot(types.GUI_Param)
    def setValue(self, value:types.GUI_Param):
        pass

