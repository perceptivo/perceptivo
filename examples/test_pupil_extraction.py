import pdb
import sys
from datetime import datetime
import pdb
from matplotlib import pyplot as plt
import typing

plt.ion()
import cv2
import numpy as np


from perceptivo.util import download
from perceptivo.prefs import Directories
from perceptivo.video.pupil import EnsembleExtractor
from perceptivo.types.video import Frame

def download_sample():
    url = 'https://archive.org/download/pupil_dilation_sample/pupils.mp4'
    filename = Directories.user_dir / 'pupil_sample.mp4'
    if not filename.exists():
        download(url, filename)
    return filename

def draw(fig:plt.Figure, ax:typing.List[plt.Axes], frame:Frame, extractor:EnsembleExtractor):
    inframe = frame
    frame = cv2.cvtColor(frame.frame.copy(), cv2.COLOR_BGR2RGB)
    if len(extractor._num_detections) == 0:
        max_neighbors = -1
    else:
        max_neighbors = np.argmax(extractor._num_detections)

    for i, (x2, y2, w2, h2) in enumerate(extractor._eyes):
        eye_center = (x2 + w2 // 2, y2 + h2 // 2)
        radius = int(round((w2 + h2) * 0.25))
        if i == max_neighbors:
            color = (0,0,255)
        else:
            color = (255,0,0)
        frame = cv2.circle(frame, eye_center, radius, color, 4)

    # draw cropped frame in top right corner
    cropped = extractor._cropped.frame

    # draw darkest circle on edges
    edges = extractor._canny_edges.copy().astype(float)
    edges *= 0.5
    for circ in extractor._circles:
        print(circ)
        edges = cv2.circle(
            edges, (circ[0], circ[1]), circ[2],
            0.75, 1
        )
    edges = cv2.circle(edges,
                       (extractor._filtered_circle[0], extractor._filtered_circle[1]),
                       extractor._filtered_circle[2],
                       1,4)



    # cv2.imshow('pupil', frame)
    ax[0,0].clear()
    ax[0,1].clear()
    ax[1,0].clear()
    ax[1,1].clear()

    ax[0,0].imshow(frame)
    ax[0,1].hist(np.ravel(cropped))
    ax[1,0].imshow(cropped)
    ax[1,1].imshow(edges)

    plt.pause(0.0001)

def test_pupil_extraction():
    fig, ax = plt.subplots(2, 2, figsize=(12,9))
    video_file = download_sample()

    extractor = EnsembleExtractor(
        canny_kwargs={'low_thresh':0.4, 'high_thresh':0.7},
        sigmoid=(0.2, 4),
        hough_kwargs={'radii': (40, 60)}
    )

    # Open video to a random point
    vid = cv2.VideoCapture(str(video_file))
    n_frames = vid.get(cv2.CAP_PROP_FRAME_COUNT)
    start_frame = np.random.randint(0, np.round(n_frames*0.8))
    vid.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    frames_got = 0

    try:
        while True:
            ret, _frame = vid.read()
            frames_got += 1
            if not ret:
                raise RuntimeError('Couldnt get frames!')
            if frames_got % 5 != 0:
                continue

            frame = Frame(
                timestamp=datetime.now(),
                frame=_frame
            )
            _ = extractor.process(frame)
            # pdb.set_trace()
            draw(fig, ax, frame, extractor)

    except KeyboardInterrupt:
        pass
    finally:
        vid.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    test_pupil_extraction()