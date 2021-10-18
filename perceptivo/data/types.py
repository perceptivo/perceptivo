"""
Dataclasses for intra-program data exchange
"""
import typing
from enum import Enum, auto
from dataclasses import dataclass, field
import shutil
from pathlib import Path

from PySide6.QtWidgets import QWidget



GUI_PARAM_KEY = typing.Literal['frequencies', 'amplitudes', 'log_x', 'log_y', 'extra_amplitude','amplitude_step', 'max_amplitude']
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

@dataclass
class GUI_Param_Type:
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
    default: typing.Any = field(default=None)
    args: list = field(default_factory=list)
    kwargs: dict = field(default_factory=dict)


@dataclass
class GUI_Param:
    """Container for GUI_Params in transit"""
    key: GUI_PARAM_KEY
    value: typing.Union[str, float, tuple]

# --------------------------------------------------
# Networking
# --------------------------------------------------

ZMQ_SOCKET = typing.Literal['REQ', 'REP', 'PUB', 'SUB', 'PAIR', 'DEALER', 'ROUTER', 'PULL', 'PUSH']
ZMQ_PROTOCOL = typing.Literal['tcp', 'ipc', 'inproc']
ZMQ_MODE = typing.Literal['connect', 'bind']


@dataclass
class Socket:
    id: str
    socket_type: ZMQ_SOCKET
    protocol: ZMQ_PROTOCOL
    mode: ZMQ_MODE
    port: int
    ip: str = field(default='*')



# --------------------------------------------------
# Sound
# --------------------------------------------------

@dataclass
class Jackd_Config:
    """
    Configure the jackd daemon used by the sound server, see https://linux.die.net/man/1/jackd

    Params:
        bin (:class:`pathlib.Path`): Path to the jackd binary
        priority (int): Priority to run the process (higher is better), default 75
        driver (str): Driver to use, default 'alsa'
        device_name (str): Device to use in alsa's parlance, default 'hw:sndrpihifiberry'
        fs (int): Sampling rate in Hz, default 44100
        nperiods (int): Number of periods per buffer cycle, default 3
        period (int): size of period, default 1024 samples.
        launch_str (str): launch string with arguments compiled from the other arguments
    """
    bin: Path = Path(shutil.which('jackd'))
    priority: int = 75
    driver: str = "alsa"
    device_name: str = "hw:sndrpihifiberry"
    fs: int = 44100
    nperiods: int = 3
    period: int = 1024
    launch_str: str = f'{bin} -P{priority} -R -d{driver} -d{device_name} -D -r{fs} -n{nperiods} -p{period} -s &'



