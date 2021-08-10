"""
Timeseries of pupil diameter, audio/stimulus presentation info
"""

from PySide6 import QtWidgets

class Pupil(QtWidgets.QGroupBox):
    def __init__(self):
        super(Pupil, self).__init__('Pupil Diameter')
