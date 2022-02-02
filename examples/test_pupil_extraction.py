from perceptivo.util import download
from perceptivo.prefs import Directories

url = 'https://archive.org/download/pupil_dilation_sample/pupils.mp4'
filename = Directories.user_dir / 'pupil_sample.mp4'
if not filename.exists():
    download(url, filename)

