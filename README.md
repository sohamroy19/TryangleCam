# COMDERS
Real-time Image Stitching, by [Soham Roy](https://github.com/sohamroy19), [Saurav Kale](https://github.com/siriusBl4ck), [Krishna Somasundaram](https://github.com/krishna122356) & [Varun M](https://github.com/I-am-VarunM).

<br>

## Requirements

#### Python:
- `pip install numpy imutils opencv-python`

#### CPP:
- GTK, OpenCV4 & any C++ compiler

<br>

## Execution

#### Python:
- Read the comments at lines 15-25 of [`TriangleCam.py`](Python/TryangleCam.py) to set camera sources before executing
  ```
  python Python/TryangleCam.py
  ```

#### CPP:
- ```
  g++ CPP/TryangleCam.cpp `pkg-config --cflags --libs opencv4 gtk+-3.0`
  ./a.out 
  ```
