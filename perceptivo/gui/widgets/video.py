"""
https://stackoverflow.com/a/35316662/13113166
"""

import PySide6
import pyqtgraph as pg

class Video(pg.ImageView):
    def __init__(self, *args, **kwargs):
        super(Video, self).__init__(*args, **kwargs)