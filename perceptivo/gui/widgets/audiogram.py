"""
Plot displaying audiogram options, current estimate of audiogram

"""

from PySide6 import QtWidgets

class Audiogram(QtWidgets.QGroupBox):
    def __init__(self):
        super(Audiogram, self).__init__('Audiogram')
