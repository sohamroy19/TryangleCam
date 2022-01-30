# import the necessary packages
import numpy as np
import imutils
import cv2


class Stitcher:
    def __init__(self):
        # determine if we are using OpenCV v3.X and initialize the
        # cached homography matrix
        self.isv3 = imutils.is_cv3()
        self.cachedH = None
        self.cachedResult = None

    def stitch(self, images, ratio=0.75, reprojThresh=4.0, flushCache=False):
        # unpack the images
        (imageB, imageA) = images

        # if the cached homography matrix is None, then we need to
        # apply keypoint matching to construct it
        if flushCache or (self.cachedH is None):
            # detect keypoints and extract
            (kpsA, featuresA) = self.detectAndDescribe(imageA)
            (kpsB, featuresB) = self.detectAndDescribe(imageB)

            try:
                # match features between the two images
                M = self.matchKeypoints(
                    kpsA, kpsB, featuresA, featuresB, ratio, reprojThresh
                )

                # if the match is None, then there aren't enough matched
                # keypoints to create a panorama
                if M is None or M[1] is None:
                    print("[WARN] not enough keypoints- using cached homography")
                else:
                    # cache the homography matrix
                    self.cachedH = M[1]
            except:
                print("[WARN] matchKeypoints failed- using cached homography")

        # apply a perspective transform to stitch the images together
        # using the cached homography matrix
        try:
            result = cv2.warpPerspective(
                imageA,
                self.cachedH,
                (imageA.shape[1] + imageB.shape[1], imageA.shape[0] + imageB.shape[0]),
            )

            if result is None:
                print("[WARN] warpPerspective returned None- using cached result")
            else:
                result[0 : imageB.shape[0], 0 : imageB.shape[1]] = imageB
                self.cachedResult = result
        except:
            print("[WARN] warpPerspective failed- using cached result")

        return self.cachedResult

    def detectAndDescribe(self, image):
        # convert the image to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # check to see if we are using OpenCV 3.X
        if self.isv3:
            # detect and extract features from the image
            descriptor = cv2.xfeatures2d.SIFT_create()
            (kps, features) = descriptor.detectAndCompute(image, None)

        # otherwise, we are using OpenCV 4.X
        else:
            sift = cv2.SIFT_create()
            (kps, features) = sift.detectAndCompute(gray, None)

        # convert the keypoints from KeyPoint objects to NumPy arrays
        kps = np.float32([kp.pt for kp in kps])

        # return a tuple of keypoints and features
        return (kps, features)

    def matchKeypoints(self, kpsA, kpsB, featuresA, featuresB, ratio, reprojThresh):
        # compute the raw matches and initialize the list of actual matches
        matcher = cv2.DescriptorMatcher_create("BruteForce")
        rawMatches = matcher.knnMatch(featuresA, featuresB, 2)
        matches = []

        # loop over the raw matches
        for m in rawMatches:
            # ensure the distance is within a certain ratio of each
            # other (i.e. Lowe's ratio test)
            if len(m) == 2 and m[0].distance < m[1].distance * ratio:
                matches.append((m[0].trainIdx, m[0].queryIdx))

        # computing a homography requires at least 4 matches
        if len(matches) > 4:
            # construct the two sets of points
            ptsA = np.float32([kpsA[i] for (_, i) in matches])
            ptsB = np.float32([kpsB[i] for (i, _) in matches])

            # compute the homography between the two sets of points
            (H, status) = cv2.findHomography(ptsA, ptsB, cv2.RANSAC, reprojThresh)

            # return the matches along with the homograpy matrix
            # and status of each matched point
            return (matches, H, status)

        # otherwise, no homograpy could be computed
        return None

    def drawMatches(self, imageA, imageB, kpsA, kpsB, matches, status):
        # initialize the output visualization image
        (hA, wA) = imageA.shape[:2]
        (hB, wB) = imageB.shape[:2]
        vis = np.zeros((max(hA, hB), wA + wB, 3), dtype="uint8")
        vis[0:hA, 0:wA] = imageA
        vis[0:hB, wA:] = imageB

        # loop over the matches
        for ((trainIdx, queryIdx), s) in zip(matches, status):
            # only process the match if the keypoint was successfully matched
            if s == 1:
                # draw the match
                ptA = (int(kpsA[queryIdx][0]), int(kpsA[queryIdx][1]))
                ptB = (int(kpsB[trainIdx][0]) + wA, int(kpsB[trainIdx][1]))
                cv2.line(vis, ptA, ptB, (0, 255, 0), 1)

        # return the visualization
        return vis
