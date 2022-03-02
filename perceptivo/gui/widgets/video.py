"""
https://stackoverflow.com/a/35316662/13113166
"""

import PySide6
import pyqtgraph as pg
from pyqtgraph.widgets.RawImageWidget import RawImageGLWidget



class Video(pg.ImageView):
# class Video(RawImageGLWidget):
    def __init__(self, *args, **kwargs):
        super(Video, self).__init__(*args, **kwargs)


# class GLVideo(RawImageGLWidget):
