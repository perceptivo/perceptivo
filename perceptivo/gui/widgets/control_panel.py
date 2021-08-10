"""
Control operation of perceptivo, set audiogram params
"""

from PySide6 import QtWidgets

class Control_Panel(QtWidgets.QGroupBox):
    def __init__(self):
        super(Control_Panel, self).__init__('Control Panel')