# Tangram Puzzle

A [Tangram](https://en.wikipedia.org/wiki/Tangram) is a "dissection puzzle"
composed of a number of flat wooden pieces which are assembled to form a specific
shape.

<img width="128" src="https://raw.githubusercontent.com/alf-labs/tangram/refs/heads/main/analyzer/data/originals/sample/sample.jpg#left" alt="Tangram Puzzle Sample"> This
project deals with a variant called **12 pieces hexagon tangram jigsaw**.  
Whereas a traditional tangram seems to have only 7 pieces,  
as the name indicates, this puzzle uses 12 pieces which fit in an enclosing hexagon.  
There are actually 8 shapes of pieces, and 5 different colors.

Solving the puzzle is rather simple -- just place the pieces till they fit.

The complexity amount is fairly low. As a simple brain-teaser, or mental fidget,
most solutions can often be found in a few seconds, although some initial pieces
placements are dead ends which are not necessarily obvious at first and can result
in a several minutes of attempts at solving the puzzle via trial and error.
In other words, it's a lot of fun.


### Analysis of the Puzzle

The puzzle shape is an hexagon, with a dimension of 6 "lines" in any given direction.
Each line is composed of equilateral triangles "cells". Lines have respectively
7, 9, 11, 11, 9, and 7 cells each. There are 54 cells total on the board.

The most basic puzzle piece is a trapezoid composed of 3 cells.
All the more complex are composed of two of these trapezoids and thus have 6 cells. 

The pieces have different colors:
  * 1 white piece,
  * 2 black pieces,
  * 2 orange pieces,
  * 3 red pieces,
  * 3 "wood brown" pieces.

Some of the pieces have _chirality_, meaning that their mirror image is different.
Such pieces can be "turned over" on the board and occupy a different space.

As the pieces are placed on an hexagon board, they can be rotated by increments 60°.
However, some pieces have radial symmetry, and has such only a subset of their
rotation matters.

Here is the list of pieces has handled by the generator below:

| Piece                      | Name           | Colors                                                | Cells | Chiral | Rotations |
|:--------------------------:|----------------|-------------------------------------------------------|-------|--------|-----------|
| ![Piece TW](/piece_tw.png) | Tx - Trapezoid | 1x White = TW <br> 1x Orange = TO <br> 2x Yellow = TY | 3     | No     | 0°        |
| ![Piece HR](/piece_hr.png) | HW - Hexagon   | 1x Red                                                | 6     | No     | 0°        |
| ![Piece J1](/piece_j1.png) | J1 - J         | 1x Orange                                             | 6     | Yes    | 0°..360°  |
| ![Piece J2](/piece_j2.png) | J2 - J         | 1x Orange                                             | 6     | Yes    | 0°..360°  |
| ![Piece i1](/piece_i1.png) | i1 - I Beam    | 1x Red                                                | 6     | Yes    | 0°..180°  |
| ![Piece i2](/piece_i2.png) | i2 - I Beam    | 1x Red                                                | 6     | Yes    | 0°..180°  |
| ![Piece L1](/piece_l1.png) | L1 - L         | 1x Yellow                                             | 6     | Yes    | 0°..360°  |
| ![Piece L2](/piece_l2.png) | L2 - L         | 1x Yellow                                             | 6     | Yes    | 0°..360°  |
| ![Piece P1](/piece_p1.png) | &#929;1 - Rho  | 1x Red                                                | 6     | Yes    | 0°..360°  |
| ![Piece P2](/piece_p2.png) | &#929;2 - Rho  | 1x Red                                                | 6     | Yes    | 0°..360°  |
| ![Piece VB](/piece_vb.png) | VB - V         | 1x Black                                              | 6     | No     | 0°..360°  |
| ![Piece W1](/piece_w1.png) | W1 - W         | 1x Black                                              | 6     | Yes    | 0°..360°  |
| ![Piece W2](/piece_w2.png) | W2 - W         | 1x Black                                              | 6     | Yes    | 0°..360°  |

Notes:
  * Color "Yellow" is really a wood brown color. I use the code name "Yellow" as 
    it allows each color to have a different starting letter. This is used in the
    generator and the analyzer to encode the board as a string with one letter per
    cell color.
  * The letter "&#929;" is really an upper case Greek rho.
  * The "I beam" is encoded using the lower case "i" to easily differentiate it from "L".


### Tangram Puzzle Generator

One of the early question I had about this puzzle is how many possible solution
there are. 


#### Board Orientation

As we're dealing with an hexagonal board, there are always 6 possible ways to
rotate the same board. To be able to compare different boards, we need a consistent
way to orient any given board.

The choice was made to rely on the white trapezoid piece, and always represent it
with its largest side horizontal and at the bottom:

![Piece TW](/piece_tw.png)

That piece was chosen because it's easily distinguishable and unique on any given board.
This gives us an easy way to orient any given board, allowing us to compare them more
easily.


#### Permutations

We define the concept of a "permutation". A permutation is an arrangement of
all the 12 puzzle pieces in a specific chirality and rotation. This basically tells
us _how_ we are going to arrange the pieces on the board, but not _where_.

Here's an example of a "permutation" -- it describes each piece with its desired
mirror image (e.g. "J1" instead of "J2" here) and each piece rotation angle:
```
HR@0 i1@60 W1@0 P1@120 VB@240 J1@300 L2@0 TO@60 TW@0 TY@0 TY@300
```

That's useful because the number of permutations is actually fairly easy to compute.

For example the TW is always represented in the same orientation and thus has no
visible permutation. Same goes for the HR piece -- since it is an hexagon, it always
looks the same when rotated and thus has essentially no visible rotational permutation.
On the other hand, a piece like the W can be oriented in 6 different ways, and as
such as 6 possible permutations for the W1 shape, and 6 more possible permutations for
its W2 counterpart once mirrored.

The number of total permutations is simply the factor of all 12 pieces potential
permutations:

| Piece | Permutation per piece | Permutations total |
|:-----:|----------------------:|-------------------:|
| TW    |                    1	 |                  1 |
| HR    |                    1	 |                  1 |         
| TO	 |                    6	 |                  6 |
| TY 1	 |                    6	 |                 36 |
| TY 2	 |                    6	 |                216 |
| i	 |                    6	 |              1,296 |
| L	 |                   12	 |            186,624 |
| P	 |                   12	 |          2,239,488 |
| VB	 |                    6	 |         13,436,928 |  
| W	 |                   12	 |        161,243,136 |


Thus we have a total number of 161,243,136 permutations to try.


#### Solutions

The generator iterates through all the permutations.
For each permutation, it tries to fill the board with that set of pieces in their
specific order.

A solution is found when all 12 pieces can be placed 

Here's an example of a "solution":
```
HR@0:4x2x0 i1@60:5x5x1 W1@0:1x1x0 P1@120:2x3x1 VB@240:0x3x0
J1@300:2x3x0 L2@0:4x1x1 TO@60:3x0x1 TW@0:2x1x0 TY@0:5x4x0 TY@300:1x1x1
```

The numbers indicate the location of each's piece _first cell_ on the board.

**The generator has found 84,696 unique solutions found in 161,242,856 permutations.**


### Tangram Puzzle Image Analyzer

This analyzer attempts to parse pictures of a
[Tangram Puzzle](data/originals/sample/sample.jpg).

<p align=center><img width="384" src="analyzer/data/originals/sample/sample.jpg" alt="Tangram Puzzle Sample"></p>




### Code and License

All the code is available at https://github.com/alf-labs/tangram
under a [MIT license](https://github.com/alf-labs/tangram/blob/main/LICENSE).

~~
