"""
Dataclasses for intra-program data exchange
"""
import typing
from enum import Enum, auto
from dataclasses import dataclass, field

from PySide6.QtWidgets import QWidget


GUI_PARAM_KEY = typing.Literal['frequencies', 'amplitudes', 'log_x', 'log_y']
GUI_WIDGET_TYPE = typing.Literal['int', 'float', 'range', 'tuple']

@dataclass
class GUI_Param_Type:
    """
    Parameterization for a GUI Parameter itself. ie. How a particular parameter should be represented.

    Args:
        key (GUI_PARAMS): the key used for the parameter
        name (str): A human readable name for the parameter
        widget_type (GUI_WIDGETS): A string that indicates the type of widget that should be used.
            Different ``widget_type``s may use different widgets, combinations of widgets, and
            validators, and are thus not strictly isomorphic to a single widget type.
        args (list): args to pass to the widget
        kwargs (dict): kwargs to pass to the widget
    """
    key: GUI_PARAM_KEY
    name: str
    widget_type: GUI_WIDGET_TYPE
    args: list = field(default_factory=list)
    kwargs: dict = field(default_factory=dict)


@dataclass
class GUI_Param:
    """Container for GUI_Params in transit"""
    key: GUI_PARAM_KEY
    value: typing.Union[str, float, tuple]

