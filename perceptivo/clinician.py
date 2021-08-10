"""
entrypoint for clinician interface
"""

import sys
from PySide6.QtWidgets import QApplication
from perceptivo.gui.main import Perceptivo_Clinician

def main():
    app = QApplication(sys.argv)
    gui = Perceptivo_Clinician()
    sys.exit(app.exec_())