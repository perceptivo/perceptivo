"""
Dataclasses for intra-program data exchange
"""
import typing
from enum import Enum, auto
from dataclasses import dataclass, field

from PySide6.QtWidgets import QWidget


GUI_PARAM_KEY = typing.Literal['frequencies', 'amplitudes', 'log_x', 'log_y', 'extra_amplitude',]
"""
Possible keys for GUI parameters. 

* ``frequencies`` - a tuple of frequencies to test
* ``amplitudes`` - a tuple of amplitudes to test
* ``log_x`` - boolean indicating whether an x-axis should be log scaled (True) or linearly scaled
* ``log_y`` - boolean indicating whether a y-axis should be log scaled (True) or linearly scaled
* ``extra_amplitude`` - boolean indicating whether an additional, suprathreshold amplitude should be tested as a confirmation
"""

GUI_WIDGET_TYPE = typing.Literal['int', 'float', 'range', 'tuple', 'bool']
"""
Widget types that correspond to particular Qt Widgets

* ``int``, ``float`` - :class:`PySide.QtWidgets.QSpinBox` and :class:`PySide.QtWidgets.QDoubleSpinBox`
* ``range`` - :class:`.widgets.components.Range_Setter`
* ``tuple`` - :class:`PySide.QtWidgets.QLineEdit` evaluated by ``ast.literal_eval``
* ``bool`` - :class:`PySide.QtWidgets.QCheckBox`
"""

@dataclass
class GUI_Param_Type:
    """
    Parameterization for a GUI Parameter itself. ie. How a particular parameter should be represented.

    Params:
        key (GUI_PARAMS): the key used for the parameter
        name (str): A human readable name for the parameter
        widget_type (GUI_WIDGETS): A string that indicates the type of widget that should be used.
            Different ``widget_type``s may use different widgets, combinations of widgets, and
            validators, and are thus not strictly isomorphic to a single widget type.
        default (any): the default value to be set, must correspond to widget type
        args (list): args to pass to the widget
        kwargs (dict): kwargs to pass to the widget
    """
    key: GUI_PARAM_KEY
    name: str
    widget_type: GUI_WIDGET_TYPE
    default: typing.Any
    args: list = field(default_factory=list)
    kwargs: dict = field(default_factory=dict)


@dataclass
class GUI_Param:
    """Container for GUI_Params in transit"""
    key: GUI_PARAM_KEY
    value: typing.Union[str, float, tuple]

