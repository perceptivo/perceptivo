import cv2
import matplotlib.pyplot as plt
from skimage.feature import blob_doh
from skimage import feature, morphology, filters, segmentation, measure, draw
from matplotlib.patches import Ellipse
import numpy as np
plt.ion()

def test_blobs(vid):

    fig, ax = plt.subplots()

    while True:
        ret, frame = vid.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        blobs = blob_doh(frame)

        ax.imshow(frame)
        for blob in blobs:
            y, x, r = blob
            c = plt.Circle((x, y), r, color='red', linewidth=2, fill=False)
            ax.add_patch(c)

        plt.pause(0.001)


def test_watershed(vid):
    fig, ax = plt.subplots(4,1, figsize=(8,10))

    while True:
        for axis in ax:
            axis.cla()

        ret, frame = vid.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        medfilt = filters.rank.median(frame, footprint=morphology.disk(5))

        # peaks = feature.peak_local_max(255-frame, footprint=morphology.disk(5), min_distance=20)
        edges = filters.scharr(medfilt)

        thresh = filters.threshold_otsu(edges)

        skeleton = morphology.skeletonize(edges>thresh)
        labeled = measure.label(skeleton)

        n_labels = len(np.unique(labeled))
        ells = []
        med_values = []
        masks = []
        for i in range(1,n_labels):
            pts = np.where(labeled==i)
            pts = np.column_stack((pts[1], pts[0]))
            ellipse_mod = measure.EllipseModel()
            ret = ellipse_mod.estimate(pts)
            if not ret:
                continue
            # compute median value inside ellipse
            rr, cc = draw.ellipse(ellipse_mod.params[1], ellipse_mod.params[0], ellipse_mod.params[2], ellipse_mod.params[3], rotation=ellipse_mod.params[4])
            rr = np.clip(rr, 0, frame.shape[0]-1)
            cc = np.clip(cc, 0, frame.shape[1]-1)
            med_values.append(np.median(np.ravel(medfilt[rr, cc])))
            ells.append(ellipse_mod)
            masks.append((rr, cc))

        # pick the ellipse with lowest median
        sort_meds = np.argsort(med_values)
        frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
        for i in sort_meds[0:2]:

            ellipse = ells[i]
            # mask_rr, mask_cc = masks[i]
            # print( (ellipse.params[0],  ellipse.params[1]),  (ellipse.params[2], ellipse.params[3]), ellipse.params[4])
            cv2.ellipse(frame, (round(ellipse.params[0]),  round(ellipse.params[1])),  (round(ellipse.params[2]), round(ellipse.params[3])), ellipse.params[4], 0, 360, (255,0,0))
            # ell_patch = Ellipse((ellipse.params[0],  ellipse.params[1]), ellipse.params[2], ellipse.params[3], ellipse.params[4],  color='red', linewidth=2, fill=False)
            # print(ellipse.params[2], ellip)
            # ax[0].add_patch(ell_patch)
            # labeled[labeled != which_ell+1] = 0
            # labeled[mask_rr, mask_cc] = i
            # frame[mask_rr, mask_cc] = 255

        # segmented = segmentation.watershed(edges, markers)



        ax[0].imshow(frame)
        # ax[0].add_patch(ell_patch)
        ax[1].imshow(medfilt)
        ax[2].imshow(edges)
        ax[3].imshow(labeled)

        plt.pause(0.001)


def get_frame():
    """
    Convenience function just to get frame from example video in grayscale
    Returns:

    """
    vid = cv2.VideoCapture('pupil_crop.mp4')
    ret, frame = vid.read()
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return frame




if __name__ == "__main__":
    vid = cv2.VideoCapture('pupil_crop.mp4')
    # test_blobs(vid)
    test_watershed(vid)