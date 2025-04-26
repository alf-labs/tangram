# Tangram Puzzle Image Analyzer

This analyzer attempts to parse pictures of a
[Tangram Puzzle](https://amzn.to/4cOuWxd).


## Usage

1. Place all source pictures in `data/originals`.
2. Create the destination directory:
```
$ mkdir data/output
```
3. Run the generator:
```
python main.py -d data/originals/
```
4. Open the generate index: \
[data/output/index.html](data/output/index.html)


To run the generator on a different source and destination directories:
```
python main.py --input-dir path/to/sources/ --output-dir path/to/output/dir
python main.py          -d path/to/sources/           -o path/to/output/dir
```
The command above scans the input directory _recursively_ for all files matching `*.jpg`.
Once all the files have been processed, an `index.html` is generated listing all the results.

Each parameter has a long and a short form (e.g. `-d` and `--input-dir`).

The default output directory, if not provided, is `data/output`.

It's also possible to process a single image at a time:
```
python main.py --input-image path/to/image.jpg --output-dir path/to/output/dir
python main.py            -i path/to/image.jpg           -o path/to/output/dir
```

Inputs are only processed once. To force inputs to be processed again, use the `-y`
or `--overwrite` argument:

```
python main.py -d data/originals/ --overwrite
python main.py -d data/originals/  -y
```



## Build Requirements

This requires Python 3 with the
[OpenCV-Python library](https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html).


Windows using Python for Windows (standalone or via Git Bash):
```
$ python -m venv .venv
$ source .venv/Scripts/active
$ python -m pip install --upgrade pip
$ pip install -v opencv-python
```

The method above is the official way to install OpenCV-Python on Windows.
The methods explain below can be... tedious, at best.


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
