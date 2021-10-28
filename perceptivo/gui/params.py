"""
Parameters presented to the clinician to control the operation of the device
"""

from perceptivo.types.gui import GUI_Param_Type as Param
from collections import OrderedDict as odict
from PySide6 import QtWidgets
from perceptivo.gui.widgets.components import Range_Setter

CONTROL_PANEL = odict({
    # 'frequencies': Param('frequencies', 'Frequencies', 'range', kwargs={'limits':(0,20000)}),
    # 'amplitudes': Param('amplitudes', 'Amplitudes', 'range', kwargs={'limits':(0,1), 'round':3}),
    'amplitude_step': Param('amplitude_step', 'Amplitude Step Size (dBSPL)', 'int', 5, kwargs={'step':5, 'limits':(5,10)}),
    'extra_amplitude': Param('extra_amplitude', 'Extra Amplitude', 'bool'),
    'max_amplitude': Param('max_amplitude', 'Max Amplitude (dBSPL)', 'int', 80, kwargs={'limits':(60, 80)})
})

WIDGET_MAP = {
    'int': QtWidgets.QSpinBox,
    'float': QtWidgets.QDoubleSpinBox,
    'range': Range_Setter,
    'tuple': QtWidgets.QLineEdit,
    'bool': QtWidgets.QCheckBox
}

