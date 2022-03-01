"""
Control operation of perceptivo, set audiogram params
"""
import typing

from PySide6 import QtWidgets
from PySide6.QtCore import Signal, Slot

import perceptivo.gui.widgets
import perceptivo.types.gui
from perceptivo.types.gui import GUI_Param, Control_Panel_Params, GUI_Control
from perceptivo.gui.widgets.components import Range_Setter
from perceptivo.gui import styles
from perceptivo.root import Perceptivo_Object

class Control_Panel(QtWidgets.QGroupBox):

    valueChanged = Signal(GUI_Control)
    scaleChanged = Signal(GUI_Control)
    startToggled = Signal(GUI_Control)

    def __init__(self, params:Control_Panel_Params):
        super(Control_Panel, self).__init__('Control Panel')
        self.params = params

        self.widgets:typing.Dict[str,QtWidgets.QWidget] = {}
        self.buttons:typing.Dict[str,QtWidgets.QPushButton] = {}

        self._init_ui()
        self.show()

    def _init_ui(self):

        self.layout = QtWidgets.QGridLayout()

        self._init_buttons()
        self._init_params()

        self.layout.setRowStretch(self.layout.rowCount(),1)
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)

    def _init_buttons(self):

        self.buttons['start'] = QtWidgets.QPushButton('START')
        self.buttons['start'].setCheckable(True)
        self.buttons['start'].toggled.connect(self._startToggled)


        self.buttons['stop'] = QtWidgets.QPushButton('STOP')
        self.buttons['stop'].setVisible(False)


        for but in self.buttons.values():
            but.setFixedHeight(styles.CONTROL_PANEL['button_height'])

        self.layout.addWidget(self.buttons['start'], 0, 0, 1, 2)
        self.layout.addWidget(self.buttons['stop'], 0, 1, 1, 1)

    def _init_params(self):

        for i, (field, param) in enumerate(self.params):
            i += 1
            widget_class = perceptivo.gui.widgets.WIDGET_MAP[param.widget_type]
            if param.widget_type == "range":
                # handle custom range widget separately
                widget = widget_class(key=param.key, name=param.name,default=param.default,**param.kwargs)
            else:
                widget = widget_class(parent=self)

            widget.setObjectName(param.key)

            # store reference to widget
            if param.key in self.widgets.keys():
                self.logger.exception(f"Already have a widget for key {param.key}, overlapping gui param keys will cause unexpected behavior! check prefs.json and types/gui.py")
            self.widgets[param.key] = widget

            if param.widget_type == 'range':
                self.layout.addWidget(widget, i, 0, 1, 2)
                widget.valueChanged.connect(self._valueChanged)
                continue

            # --------------------------------------------------
            # apply kwargs
            # --------------------------------------------------
            if 'limits' in param.kwargs:
                widget.setMinimum(param.kwargs['limits'][0])
                widget.setMaximum(param.kwargs['limits'][1])

            if 'step' in param.kwargs:
                widget.setSingleStep(param.kwargs['step'])

            # --------------------------------------------------
            # apply default
            # --------------------------------------------------
            if param.default is not None:
                if param.widget_type in ('int', 'float'):
                    widget.setValue(param.default)
                elif param.widget_type in ('tuple',):
                    widget.setText(str(param.default))
                elif param.widget_type in ('bool',):
                    widget.setChecked(param.default)
                else:
                    self.logger.exception(f'Dont know how to apply default for widget_type {param["widget_type"]}')

            # --------------------------------------------------
            # add to layout
            # --------------------------------------------------

            label = QtWidgets.QLabel(param.name)
            self.layout.addWidget(label, i, 0, 1, 1)
            self.layout.addWidget(widget, i, 1, 1, 1)

            # connect to signals
            if isinstance(widget, (QtWidgets.QSpinBox, QtWidgets.QDoubleSpinBox)):
                widget.valueChanged.connect(self._valueChanged)
            elif isinstance(widget, QtWidgets.QLineEdit):
                widget.textChanged.connect(self._valueChanged)
            elif isinstance(widget, QtWidgets.QCheckBox):
                widget.toggled.connect(self._valueChanged)


    def _startToggled(self, value:bool):
        self.logger.debug(f'Start button toggled: {bool}')
        try:
            self.setUpdatesEnabled(False)
            if value:
                self.buttons['start'].setText('PAUSE')
                self.buttons['stop'].setVisible(True)
                self.layout.addWidget(self.buttons['start'], 0,0,1,1)
            else:
                self.buttons['stop'].setVisible(False)
                self.buttons['start'].setText('START')
                self.layout.addWidget(self.buttons['start'], 0, 0, 1, 2)

            self.startToggled.emit(value)
        finally:
            self.setUpdatesEnabled(True)



    def _valueChanged(self, value: GUI_Control):
        if not isinstance(value, GUI_Control):
            value = GUI_Control(key=self.sender().objectName(), value=value)

        self.logger.debug(f'emitting {value}')
        self.valueChanged.emit(value)

    def _scaleChanged(self, value):
        sender = self.sender().key
        if sender == perceptivo.types.gui.CONTROL_PANEL['frequencies'].key:
            key = 'log_x'
        elif sender == perceptivo.types.gui.CONTROL_PANEL['amplitudes'].key:
            key = 'log_y'
        else:
            raise ValueError(f'Not sure who send the scale value, dont know how to parameterize it!')

        set_to = False
        if value == 'log':
            set_to = True

        self.scaleChanged.emit(GUI_Control(key, set_to))

    def _gridChanged(self):
        pass

    @Slot(GUI_Control)
    def setValue(self, value: GUI_Control):
        pass

