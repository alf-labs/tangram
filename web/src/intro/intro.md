[Analysis of the Puzzle](#/#analysis-of-the-puzzle)
|
[Generator](#/#tangram-puzzle-generator)
|
[Heatmap](#/#pieces-heatmap)
|
[Image Analyzer](#/#tangram-puzzle-image-analyzer)

---
A [Tangram](https://en.wikipedia.org/wiki/Tangram) is a "dissection puzzle"
composed of a number of flat wooden pieces which are assembled to form a specific
shape.

<img width="128" src="https://raw.githubusercontent.com/alf-labs/tangram/refs/heads/main/analyzer/data/originals/sample/sample.jpg#left" alt="Tangram Puzzle Sample"> This
project deals with a variant called **12 pieces hexagon tangram jigsaw**.  
Whereas a traditional tangram has only 7 pieces, this variant of the puzzle,
as the name indicates, uses 12 pieces which fit in an enclosing hexagon.  
There are actually 8 shapes of pieces, and 5 different colors.

Solving the puzzle is rather simple -- just place the pieces till they fit.

The complexity amount is fairly low. As a simple brain-teaser, or mental fidget,
most solutions can often be found in a few seconds, although some initial pieces
placements are dead ends which are not necessarily obvious at first and can result
in several minutes of attempts at solving the puzzle via trial and error.
In other words, it's a lot of fun.


---
### Analysis of the Puzzle

The puzzle shape is an hexagon, with a dimension of 6 "lines" in any given direction.
Each line is composed of equilateral triangle cells.
Lines have respectively 7, 9, 11, 11, 9, and 7 cells each.
There are 54 cells total on the board.

The most basic puzzle piece is a trapezoid composed of 3 cells.
All the more complex pieces are composed of two of these trapezoids and have 6 cells. 

The pieces have different colors:
  * 1 white piece,
  * 2 black pieces,
  * 2 orange pieces,
  * 3 red pieces,
  * 3 "wood brown" pieces.

Some of the pieces have _chirality_, meaning that their mirror image is different.
Such pieces can be "turned over" on the board and occupy a different space.

As the pieces are placed on an hexagon board, they can be rotated by increments of 60°.
However, some pieces have radial symmetry, and has such only a subset of their
rotation matters.

Here is the list of pieces as handled by the generator below:

|           Piece            | Name           | Colors                                                | Cells | Chiral | Rotations |
|:--------------------------:|----------------|-------------------------------------------------------|-------|--------|-----------|
| ![Piece TW](piece_tw.png)  | Tx - Trapezoid | 1x White = TW <br> 1x Orange = TO <br> 2x Yellow = TY | 3     | No     | 0°        |
| ![Piece HR](piece_hr.png)  | HW - Hexagon   | 1x Red                                                | 6     | No     | 0°        |
| ![Piece J1](piece_j1.png)  | J1 - J         | 1x Orange                                             | 6     | Yes    | 0°..360°  |
| ![Piece J2](piece_j2.png)  | J2 - J         | 1x Orange                                             | 6     | Yes    | 0°..360°  |
| ![Piece i1](piece_i1.png)  | i1 - I Beam    | 1x Red                                                | 6     | Yes    | 0°..180°  |
| ![Piece i2](piece_i2.png)  | i2 - I Beam    | 1x Red                                                | 6     | Yes    | 0°..180°  |
| ![Piece L1](piece_l1.png)  | L1 - L         | 1x Yellow                                             | 6     | Yes    | 0°..360°  |
| ![Piece L2](piece_l2.png)  | L2 - L         | 1x Yellow                                             | 6     | Yes    | 0°..360°  |
| ![Piece P1](piece_p1.png)  | &#929;1 - Rho  | 1x Red                                                | 6     | Yes    | 0°..360°  |
| ![Piece P2](piece_p2.png)  | &#929;2 - Rho  | 1x Red                                                | 6     | Yes    | 0°..360°  |
| ![Piece VB](piece_vb.png)  | VB - V         | 1x Black                                              | 6     | No     | 0°..360°  |
| ![Piece W1](piece_w1.png)  | W1 - W         | 1x Black                                              | 6     | Yes    | 0°..360°  |
| ![Piece W2](piece_w2.png)  | W2 - W         | 1x Black                                              | 6     | Yes    | 0°..360°  |

Notes:
  * Color "Yellow" is really a wood brown color. I use the code name "Yellow" as 
    it allows each color to have a different starting letter. This is used in the
    generator and the analyzer to encode the board as a string with one letter per
    cell color.
  * The letter "&#929;" is really an upper case Greek rho.
  * The "I beam" is encoded using the lower case "i" to easily differentiate it from "L".


---
### Tangram Puzzle Generator

One of the early questions we had about this puzzle is how many possible solutions
there are.
We do not know of a way to mathematically compute the number of valid solutions.
This prompted the idea of writing a generator that would compute all the possible moves
to find the number of possible board solutions.


#### Board Orientation

As we're dealing with an hexagonal board, there are always 6 possible ways to
rotate the same board. To be able to compare different boards, we need a consistent
way to orient any given board.

The choice was made to rely on the white trapezoid piece, and always represent it
with its largest side horizontal and at the bottom:

![Piece TW](piece_tw.png#center)

That piece was chosen because it's easily distinguishable and unique on any given board.

Thus for any given board, we rotate the hexagonal board in such a way that this unique piece
is always in the same direction, no matter where it is on the board.  
This gives us an easy way to orient any given board, allowing us to compare them more
easily.


#### Permutations

We define the concept of a "permutation". A permutation is an arrangement of
all the 12 puzzle pieces in a specific chirality and rotation. This basically tells
us _how_ we are going to arrange the pieces on the board, but not _where_.

Here's an example of a "permutation" -- it describes each piece with its desired
mirror image (e.g. "J1" instead of "J2" here) and each piece rotation angle:
```
HR@0   i1@60 W1@60  P2@240 VB@300 J1@120
L1@300 TW@0  TO@240 TY@240 TY@120
```

That's useful because the number of permutations is actually fairly easy to compute.

For example the TW is always represented in the same orientation and thus has no
visible permutation. Same goes for the HR piece -- since it is an hexagon, it always
looks the same when rotated and thus has essentially no visible rotational permutation.
On the other hand, a piece like the W can be oriented in 6 different ways, and as
such has 6 possible permutations for the W1 shape, and 6 more possible permutations for
its W2 counterpart once mirrored.

The number of total permutations is simply the factor of all 12 pieces potential
permutations:

| Piece | Permutation per piece | Permutations total |
|:-----:|----------------------:|-------------------:|
| TW    |                    1	 |                  1 |
| HR    |                    1	 |                  1 |         
| TO	  |                    6	 |                  6 |
| TY 1  |                    6	 |                 36 |
| TY 2  |                    6	 |                216 |
| i	    |                    6	 |              1,296 |
| L	    |                   12	 |            186,624 |
| P	    |                   12	 |          2,239,488 |
| VB	  |                    6	 |         13,436,928 |  
| W	    |                   12	 |        161,243,136 |


Thus, we have a total number of 161,243,136 permutations to try.


#### Solutions

The generator iterates through all the permutations.
For each permutation, it tries to fill the board with that set of pieces in their
specific order.

A solution is found when all 12 pieces can be placed on the board side by side,
with no overlap and no gaps.

Here's an example of a "solution":
```
HR@0:1x1x0   i1@60:5x5x1  W1@60:3x4x1
P2@240:3x1x1 VB@300:0x0x1 J1@120:4x1x1
L1@300:0x2x1 TW@0:5x3x0   TO@240:3x3x0
TY@240:0x0x0 TY@120:5x5x0
```

The numbers indicate the location of each's piece _first cell_ on the board using the
_YRG Coordinate System_:

![YRG Coordinate System](abs_yrg.png#center)

The results of the generator can be seen in the [Generator tab](#/gn).

Result: **The [generator](#/gn) has found 84,696 unique solutions in 161,242,856 permutations.**

There are 2 versions of the generator in this project:
* [analyzer/gen.py](https://github.com/alf-labs/tangram/blob/main/analyzer/gen.py) is the
  original version written in Python. It initially computed permutations at the speed of
  one every 10 seconds, and was further optimized using various heuristics to compute
  10 permutations per second.
* [rgen](https://github.com/alf-labs/tangram/tree/main/rgen) is a rewrite of the generator
  in Rust. It uses the same heuristics. This one computes about 500 permutations per second
  per thread on the laptop. Running it on 4 threads, it covered the 160 million permutations in
  about 24 hours.


#### Pieces Heatmap

Due to their shapes, pieces are more likely to be located in specific places of the board.

The analyzer/generator uses all the solutions found above and counts the number of times
each cell is used by a given piece accross all solutions. The result is a
"piece heatmap" which can be seen in the [Pieces tab](#/pc).


---
### Tangram Puzzle Image Analyzer

The analyzer was built to determine whether our puzzle solutions were unique
or contained duplicates.

The analyzer is a command-line Python program that processes
images of the real puzzle board using
[OpenCV-Python](https://docs.opencv.org/4.x/index.html),
and then outputs a table that lists all the pictures of the boards and their
identified cells colors, listing duplicates when found.

The image analyzer is experimental and has a few shortcomings.

More information about the Python analyzer is available in the github
[analyzer](https://github.com/alf-labs/tangram/tree/main/analyzer) directory.

The results of the analyzer can be seen in the [Analyzer tab](#/an).


---
### Code and License

All the code is available at https://github.com/alf-labs/tangram
under a [MIT license](https://github.com/alf-labs/tangram/blob/main/LICENSE).

~~
