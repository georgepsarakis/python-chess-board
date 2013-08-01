Python Chess Board
==================

Small Python script that sets up a chess board and allows 2 players to play with each other on a terminal.

Features:

1.  Timer for each player
2.  Minimal move validation and appropriate messages


## Getting Started ##

__Dependencies__

There is only one dependency the `argparse` Python package, for command line arguments processing:

`easy_install argparse`

__Get The Code & Run!__

Just open a terminal in a Linux box and run:

`git clone https://github.com/georgepsarakis/python-chess-board.git`

`cd python-chess-board`

`./chessboard.py --help`

to get a list of the command line arguments (basically the usernames) or just:

`./chessboard.py`

to start a game!


## How to Play ##

Apart from basic understanding of the [chess moves](https://en.wikipedia.org/wiki/Chess#Movement), the interface follows these steps:

1. You are presented with the initial board setup
2. The timer starts for White
3. Once you thought of your move, just press `Enter` to stop the clock
4. Enter your move according to the pattern: `PIECE SQUARE->TARGET SQUARE` . Example: `b2 -> B3` will move the white pawn in *B2* one position forward. You can use uppercase or lowercase letters, and add whitespace between the *->* separator and the square notation, it doesn't matter.
5. The move is checked and the user is either prompted with an error message, explaining why the move was rejected or if accepted the timer for the other user starts counting
6. Process is repeated

## Notes ##

* The move validation is pretty basic so far and you cannot perform complex moves such as [castling](https://en.wikipedia.org/wiki/Chess#Castling) or [promotion](https://en.wikipedia.org/wiki/Chess#Promotion). You are not even allowed to move the pawns 2 positions forward when they are in their initial positions, as adding many exceptions would complicate the design at this moment.
* It should be able to detect, verify and report check & checkmate events (maybe the first steps towards an engine?).

----
This is intended as a fun & learning project and has no actual real-life value except for learning purposes. 

Please open an issue in order to ask questions and express (constructive) criticism!
