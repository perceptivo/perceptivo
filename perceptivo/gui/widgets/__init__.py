from PySide6 import QtWidgets

from perceptivo.gui.widgets.components import Range_Setter
from perceptivo.gui.widgets.video import Video
from perceptivo.gui.widgets.audiogram import Audiogram
from perceptivo.gui.widgets.control_panel import Control_Panel
from perceptivo.gui.widgets.pupil import Pupil

WIDGET_MAP = {
    'int': QtWidgets.QSpinBox,
    'float': QtWidgets.QDoubleSpinBox,
    'range': Range_Setter,
    'tuple': QtWidgets.QLineEdit,
    'bool': QtWidgets.QCheckBox
}