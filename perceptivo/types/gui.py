import typing
from pydantic import Field

from perceptivo.types.root import PerceptivoType

GUI_PARAM_KEY = typing.Literal[
    'frequencies',
    'amplitudes',
    'log_x',
    'log_y',
    'extra_amplitude',
    'amplitude_step',
    'amplitude_range',
    'max_amplitude',
    'frequency_step',
    'frequency_range'
]
"""
Possible keys for GUI parameters. 

* ``frequencies`` - a tuple of frequencies to test
* ``amplitudes`` - a tuple of amplitudes to test
* ``log_x`` - boolean indicating whether an x-axis should be log scaled (True) or linearly scaled
* ``log_y`` - boolean indicating whether a y-axis should be log scaled (True) or linearly scaled
* ``extra_amplitude`` - boolean indicating whether an additional, suprathreshold amplitude should be tested as a confirmation
* ``amplitude_step`` - Step size of amplitudes to test in dB
"""

GUI_WIDGET_TYPE = typing.Literal['int', 'float', 'range', 'tuple', 'bool']
"""
Widget types that correspond to particular Qt Widgets

* ``int``, ``float`` - :class:`PySide.QtWidgets.QSpinBox` and :class:`PySide.QtWidgets.QDoubleSpinBox`
* ``range`` - :class:`.widgets.components.Range_Setter`
* ``tuple`` - :class:`PySide.QtWidgets.QLineEdit` evaluated by ``ast.literal_eval``
* ``bool`` - :class:`PySide.QtWidgets.QCheckBox`
"""


class GUI_Control(PerceptivoType):
    """Container for GUI_Params in transit"""
    key: GUI_PARAM_KEY
    value: typing.Union[str, float, tuple]

class GUI_Range(PerceptivoType):
    """
    Range for :class:`.widgets.components.Range_Setter`
    """
    min:float
    max:float
    n:int


class GUI_Param(PerceptivoType):
    """
    Parameterization for a GUI Parameter itself. ie. How a particular parameter should be represented.

    Params:
        key (GUI_PARAMS): the key used for the parameter
        name (str): A human readable name for the parameter
        widget_type (GUI_WIDGETS): A string that indicates the type of widget that should be used.
            Different ``widget_type`` s may use different widgets, combinations of widgets, and
            validators, and are thus not strictly isomorphic to a single widget type.
        default (any): the default value to be set, must correspond to widget type
        args (list): args to pass to the widget
        kwargs (dict): kwargs to pass to the widget
    """
    key: GUI_PARAM_KEY
    name: str
    widget_type: GUI_WIDGET_TYPE
    default: typing.Optional[typing.Union[float, int, GUI_Range, tuple]] = Field(default=None)
    args: list = Field(default_factory=list)
    kwargs: dict = Field(default_factory=dict)

# --------------------------------------------------
# Defaults and parameters for control panel widgets
# --------------------------------------------------

class Control_Panel_Params(PerceptivoType):
    """
    Defaults and parameters for :class:`perceptivo.gui.widgets.Control_Panel`

    """
    # amplitude_step = GUI_Param(
    #     key='amplitude_step',
    #     name='Amplitude Step Size (dBSPL)',
    #     widget_type='int',
    #     default=5,
    #     kwargs={'step':5, 'limits':(5,10)}
    # )
    amplitude_range = GUI_Param(
        key='amplitude_range',
        name='Amplitude Range (dBSPL)',
        widget_type='range',
        default=GUI_Range(min=0, max=80, n=8),
        kwargs={'limits': (0, 100)}
    )
    # frequency_step = GUI_Param(
    #     key='frequency_step',
    #     name='Frequency Step Size (Hz)',
    #     widget_type='int',
    #     default=1000,
    #     kwargs={'step': 500, 'limits':(100,5000)}
    # )
    frequency_range = GUI_Param(
        key='frequency_range',
        name='Frequency Range (Hz)',
        widget_type='range',
        default=GUI_Range(min=0,max=8000,n=17),
        kwargs={'limits':(0,20000)}
    )


class GUI_Params(PerceptivoType):
    """
    Container for all parameters to be given to the GUI on init
    """
    control_panel: Control_Panel_Params = Control_Panel_Params()




# CONTROL_PANEL = odict({
#     # 'frequencies': Param('frequencies', 'Frequencies', 'range', kwargs={'limits':(0,20000)}),
#     # 'amplitudes': Param('amplitudes', 'Amplitudes', 'range', kwargs={'limits':(0,1), 'round':3}),
#     #'extra_amplitude': Param('extra_amplitude', 'Extra Amplitude', 'bool'),
#     # 'max_amplitude': Param('max_amplitude', 'Max Amplitude (dBSPL)', 'int', 80, )
# })
