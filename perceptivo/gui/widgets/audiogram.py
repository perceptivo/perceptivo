"""
Plot displaying audiogram options, current estimate of audiogram

"""

from PySide6 import QtWidgets, QtCore
import pyqtgraph as pg

import numpy as np
from perceptivo.data.logging import init_logger

from perceptivo.data.types import GUI_Param

class Audiogram(QtWidgets.QGroupBox):
    def __init__(self):
        super(Audiogram, self).__init__('Audiogram')
        self.logger = init_logger(self)

        self.log = (False, False)

        self.frequencies = tuple()
        self.amplitudes = tuple()

        self.plot = pg.PlotWidget(self)
        self.plot.plotItem.getAxis('bottom').setLabel('Frequency (Hz)')
        self.plot.plotItem.getAxis('left').setLabel('Amplitude (0-1 AU)')

        self.points = pg.ScatterPlotItem()
        self.plot.addItem(self.points)

        self.layout = QtWidgets.QGridLayout()
        self.layout.addWidget(self.plot)
        self.setLayout(self.layout)


    @QtCore.Slot(GUI_Param)
    def gridChanged(self, value: GUI_Param):
        if value.key not in ('frequencies', 'amplitudes'):
            return
        self.logger.debug(f'Grid Changed: {GUI_Param}')
        if value.key == 'frequencies':
            self.frequencies = value.value
        elif value.key == 'amplitudes':
            self.amplitudes = value.value
        else:
            raise ValueError(f'Need a GUI_Param with key == frequencies or amplitudes, got {value}')

        self._drawGrid()

    @QtCore.Slot(str)
    def scaleChanged(self, value: GUI_Param):
        if value.key == 'log_x':
            self.log = (value.value, self.log[1])
        elif value.key == 'log_y':
            self.log = (self.log[0], value.value)

        self.plot.plotItem.setLogMode(*self.log)

    def _drawGrid(self):
        if not all((self.frequencies, self.amplitudes)):
            return

        points = np.array(np.meshgrid(self.frequencies, self.amplitudes)).T.reshape(-1,2)
        self.logger.debug(f'Drawing Points: {points}')

        self.points.setData(pos=points)








