"""
Plot displaying audiogram options, current estimate of audiogram

"""
import typing
from typing import Optional, Tuple

from PySide6 import QtWidgets, QtCore
import pyqtgraph as pg

import numpy as np
from perceptivo.data.logging import init_logger

from perceptivo.types.gui import GUI_Control


class Audiogram(QtWidgets.QGroupBox):
    def __init__(self,
                 default_amplitudes:Tuple[float]=tuple(),
                 default_frequencies:Tuple[float]=tuple()):
        super(Audiogram, self).__init__('Audiogram')
        self.logger = init_logger(self)

        self.log = (False, False)

        self.frequencies = default_frequencies
        self.amplitudes = default_amplitudes

        self.plot = pg.PlotWidget(self)
        self.plot.plotItem.getAxis('bottom').setLabel('Frequency (Hz)')
        self.plot.plotItem.getAxis('left').setLabel('Amplitude (0-1 AU)')

        self.points = pg.ScatterPlotItem()
        self.plot.addItem(self.points)

        self.layout = QtWidgets.QGridLayout()
        self.layout.addWidget(self.plot)
        self.setLayout(self.layout)

        self._drawGrid()


    @QtCore.Slot(GUI_Control)
    def gridChanged(self, value: GUI_Control):
        if value.key not in ('frequencies', 'amplitudes', 'frequency_range', 'amplitude_range'):
            self.logger.warning(f'Invalid control value: {GUI_Control}')
            return
        self.logger.debug(f'Grid Changed: {GUI_Control}')
        if value.key in ('frequencies', 'frequency_range'):
            self.frequencies = value.value
        elif value.key in ('amplitudes', 'amplitude_range'):
            self.amplitudes = value.value
        else:
            raise ValueError(f'Need a GUI_Control with key == frequencies or amplitudes, got {value}')

        self._drawGrid()

    @QtCore.Slot(str)
    def scaleChanged(self, value: GUI_Control):
        if value.key == 'log_x':
            self.log = (value.value, self.log[1])
        elif value.key == 'log_y':
            self.log = (self.log[0], value.value)

        self.plot.plotItem.setLogMode(*self.log)

    def _drawGrid(self):
        if not all((self.frequencies, self.amplitudes)):
            return

        points = np.array(np.meshgrid(self.frequencies, self.amplitudes)).T.reshape(-1,2)
        self.logger.debug(f'Redrawing Audiogram grid points')

        self.points.setData(pos=points)








