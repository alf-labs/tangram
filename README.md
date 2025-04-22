# Tangram Puzzle Image Analyzer

TDB


## Build Requirements

Windows using Python for Windows (standalone or via Git Bash):
```
$ python -m venv .venv
$ source .venv/Scripts/active
$ python -m pip install --upgrade pip
$ pip install -v opencv-python
```

Windows with Cygwin or MSYS have their own packages which may or may not build easily:
```
Cygwin Setup: requires make, cmake, gcc, python3-pkgconfig, python3-cv2, python3-devel
$ pip install --verbose opencv-python

MSYS:
$ pacman -S cmake gcc mingw-w64-x86_64-python-opencv
```

Linux:
```
$ apt install python3-opencv
```


## License

MIT. See [LICENSE](/LICENSE).

~~
