# import the necessary packages
from Stitcher import Stitcher
from MotionDetector import MotionDetector
from imutils.video import VideoStream
from datetime import datetime

import numpy as np
import imutils
import time
import cv2

# initialize the video streams and allow them to warmup
print("[INFO] starting cameras...")

###############################################################################
##  When standing behind the cameras, the leftStream should be the camera    ##
##  to your lefthand side and the rightStream should be the camera to your   ##
##  righthand side.                                                          ##
##                                                                           ##
##  VideoStream(src=0).start()            # for default camera (eg. webcam)  ##
##  VideoStream(usePiCamera=True).start()         # for Raspberry Pi camera  ##
##  VideoStream(src="http://10.42.164.131:8080/video").start() # for IP cam  ##
##  rightStream = leftStream                                # for mirroring  ##
###############################################################################
leftStream = VideoStream(2).start()
rightStream = VideoStream(4).start()

time.sleep(2.0)

# initialize the image stitcher, motion detector, and total number of frames read
stitcher = Stitcher()
motion = MotionDetector(minArea=500)
frames = 0

# loop over frames from the video streams
while True:
    # grab the frames from their respective video streams
    left = leftStream.read()
    right = rightStream.read()

    # resize the frames
    left = imutils.resize(left, height=480)
    right = imutils.resize(right, height=480)

    cv2.imshow("Left Frame", left)
    cv2.imshow("Right Frame", right)

    # wait for a keypress on first display
    if frames == 0:
        key = cv2.waitKey(0) & 0xFF
        motion_detection = key == ord("m")

    ###########################################################################
    ##  (frames % x) flushes the homography cache every x frames             ##
    ###########################################################################

    # start = datetime.now()  # PROFILING
    result = stitcher.stitch([left, right], flushCache=(frames % 100 == 0))
    # time_ms = (datetime.now() - start).total_seconds() * 1000  # PROFILING
    # print("[INFO] stitched frame #{} in {:.2f} ms".format(frames, time_ms)) # PROFILING

    # keep trying to compute homograpy if it didn't work the first time
    while result is None:
        print("[INFO] homography could not be computed: frame #{}".format(frames))

        result = stitcher.stitch([left, right], flushCache=(frames % 100))

    if motion_detection:
        # convert the panorama to grayscale, blur it slightly, update the motion detector
        gray = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        locs = motion.update(gray)

        # only process the panorama for motion if a nice average has been built up
        if frames > 32 and len(locs) > 0:
            # initialize the minimum and maximum (x, y)-coordinates, respectively
            (minX, minY) = (np.inf, np.inf)
            (maxX, maxY) = (-np.inf, -np.inf)

            # loop over the locations of motion and accumulate the
            # minimum and maximum locations of the bounding boxes
            for l in locs:
                (x, y, w, h) = cv2.boundingRect(l)
                (minX, maxX) = (min(minX, x), max(maxX, x + w))
                (minY, maxY) = (min(minY, y), max(maxY, y + h))

            # draw the bounding box
            cv2.rectangle(result, (minX, minY), (maxX, maxY), (0, 0, 255), 3)

    # increment the total number of frames
    frames += 1

    # show the output image
    cv2.imshow("Result", result)

    key = cv2.waitKey(1) & 0xFF

    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break

# do a bit of cleanup
print("[INFO] cleaning up...")
cv2.destroyAllWindows()
leftStream.stop()
rightStream.stop()
