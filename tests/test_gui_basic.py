from perceptivo.prefs import Clinician_Prefs
from perceptivo.gui.main import Perceptivo_Clinician

from pytestqt import qt_compat
from pytestqt.qt_compat import qt_api


def test_gui_launch(qtbot):

    prefs = Clinician_Prefs()
    gui = Perceptivo_Clinician(
        prefs=prefs,
        networking=prefs.networking
    )
    qtbot.addWidget(gui)

    qtbot.waitUntil(lambda: gui.isVisible(), timeout=10000)


