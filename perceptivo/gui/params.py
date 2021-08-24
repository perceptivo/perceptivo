"""
Parameters presented to the clinician to control the operation of the device
"""

from perceptivo.data.types import GUI_Param_Type as Param

CONTROL_PANEL = {
    'frequencies': Param('frequencies', 'Frequencies', 'range', kwargs={'limits':(0,20000)}),
    'amplitudes': Param('amplitudes', 'Amplitudes', 'range', kwargs={'limits':(0,1), 'round':3})
}