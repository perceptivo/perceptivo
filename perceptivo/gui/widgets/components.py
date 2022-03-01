"""
Subcomponents for larger GUI widgets
"""

import typing

from PySide6 import QtWidgets, QtGui, QtCore
from PySide6.QtCore import Signal, Slot

import numpy as np

from perceptivo.types.gui import GUI_Param, GUI_Range, GUI_Control, GUI_PARAM_KEY
from perceptivo.data.logging import init_logger

class Range_Setter(QtWidgets.QWidget):
    """
    Buttons and text fields to parameterize a linearly or logarithmically spaced array of values
    """

    valueChanged = Signal(GUI_Control)
    buttonClicked = Signal(GUI_Control)
    scaleChanged = Signal(str)

    def __init__(self,
                 key: GUI_PARAM_KEY,
                 name: str,
                 round:int=0,
                 limits:typing.Tuple[int, int]=(0, 100),
                 default:GUI_Range=GUI_Range(min=0, max=100, n=10),
                 *args, **kwargs):
        """
        Args:
            key (str): key of value that is set by this widget, likely one of :data:`.types.GUI_PARAM_KEY`
            name (str): human-readable name of parameter
            round (int): Digits to round generated values to (default ``0``)
            limits (tuple): Absolute allowable maximum and minimum
            step (float): Step size of the spinboxes
            *args, **kwargs: passed to :class:`PySide6.QtWidgets.QWidget`
        """
        super(Range_Setter, self).__init__(*args, **kwargs)
        self.logger = init_logger(self)

        self.key = key # type: GUI_PARAM_KEY
        self.name = str(name)
        self.round = int(round)
        self.limits = limits
        self.default = default

        self._init_ui()

        self._init_signals()

        # set defaults
        self.minbox.setValue(self.default.min)
        self.maxbox.setValue(self.default.max)
        self.nbox.setValue(self.default.n)



    def _init_ui(self):

        self.layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.layout)

        self.label = QtWidgets.QLabel(self.name)

        self.mingroup = QtWidgets.QGroupBox('Min')
        self.maxgroup = QtWidgets.QGroupBox('Max')
        self.ngroup = QtWidgets.QGroupBox('#')

        self.minlayout, self.maxlayout, self.nlayout = QtWidgets.QHBoxLayout(), QtWidgets.QHBoxLayout(), QtWidgets.QHBoxLayout()

        self.minbox = QtWidgets.QDoubleSpinBox()
        self.maxbox = QtWidgets.QDoubleSpinBox()
        self.nbox = QtWidgets.QSpinBox()

        self.minbox.setMinimum(self.limits[0]); self.maxbox.setMinimum(self.limits[0])
        self.minbox.setMaximum(self.limits[1]); self.maxbox.setMaximum(self.limits[1])
        self.nbox.setMinimum(1)


        self.minlayout.addWidget(self.minbox)
        self.maxlayout.addWidget(self.maxbox)
        self.nlayout.addWidget(self.nbox)
        self.minlayout.setContentsMargins(0,0,0,0)
        self.maxlayout.setContentsMargins(0,0,0,0)

        self.mingroup.setLayout(self.minlayout)
        self.maxgroup.setLayout(self.maxlayout)
        self.ngroup.setLayout(self.nlayout)

        self.logcheck = QtWidgets.QCheckBox('Log')
        self.button = QtWidgets.QPushButton('X')

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.mingroup)
        self.layout.addWidget(self.maxgroup)
        self.layout.addWidget(self.ngroup)
        self.layout.addWidget(self.logcheck)
        self.layout.addWidget(self.button)

        # --------------------------------------------------

        horz_policy = QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Expanding,
                QtWidgets.QSizePolicy.Preferred
            )

        self.setSizePolicy(horz_policy)
        self.mingroup.setSizePolicy(horz_policy)
        self.maxgroup.setSizePolicy(horz_policy)
        self.ngroup.setSizePolicy(horz_policy)

    def _init_signals(self):
        self.minbox.valueChanged.connect(self._valueChanged)
        self.maxbox.valueChanged.connect(self._valueChanged)
        self.nbox.valueChanged.connect(self._valueChanged)

        self.logcheck.stateChanged.connect(self._scaleChanged)

        self.button.clicked.connect(self._buttonClicked)


    def _valueChanged(self):
        param = GUI_Control(key=self.key, value=self.value())
        self.valueChanged.emit(param)
        self.logger.debug(f'Value Changed: {param}')

    def _buttonClicked(self):
        param = GUI_Control(key=self.key, value=self.value())
        self.buttonClicked.emit(param)
        self.logger.debug(f'Value Changed: {param}')

    def _scaleChanged(self):
        if self.logcheck.isChecked():
            change_to = 'log'
        else:
            change_to = 'linear'

        self.scaleChanged.emit(change_to)
        self.logger.debug(f"Scale changed to {change_to}")

        self._valueChanged()

    def value(self) -> typing.Tuple[float]:
        min, max, n = self.minbox.value(), self.maxbox.value(), self.nbox.value()
        if self.logcheck.isChecked():
            if min == 0:
                min = 0.00001
            seq = np.geomspace(min, max, n)
        else:
            seq = np.linspace(min, max, n)

        return tuple(seq.tolist())

    def setMaximum(self, value:float):
        pass

    def setMinimum(self, value:float):
        pass


