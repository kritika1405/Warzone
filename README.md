# Warzone
Two player game based on Dameo

Types of Pieces: 2

Pawn: Can move forward or diagonal, Jump one piece in an orthogonal
manner(up, down, left, right)

King: Can move in 8 directions, step any direction, jump one piece in an
orthogonal manner(up, down, left, right)

A pawn can become a king when it reaches the opposite end of the board. A king has
more moves than a pawn

Obstacles: 1

Rock: Cannot move. Will be randomly placed from 2-6 in numbers. They just act as an obstacle and players may use it as cover.
Pawns or kings cannot occupy these spots but can jump over them.  


The User will move first and then the computer moves.

Movement

Pawns can only move forward, either straight ahead or diagonally.

Pawn can jump over other one or more other subsequent Pawn of the same
color if the square ahead of the line is free.

When a Pawn reaches the opposite end of the board, it is promoted to a king. 

The king can move in 8 directions to any available number
of cells.

Capturing 

In these types of moves, user jumps over enemy piece removing them from the board.
Capture can occur in orthogonal direction only. 

A Pawn may capture forwards, backwards and sideways by a short leap two squares beyond to an unoccupied square
opposite the captured piece. 

A king may capture by a long leap to any unoccupied square opposite the captured
piece, so long as there is no other piece obstructing the path of the king.

A jumped piece will be removed from the board at the end of the turn. 


Results

A player will lose if one of the following happens
-> He has no pieces left on board.
-> He has no valid moves remaining. This occurs if all the player's pieces are obstructed from moving by opponent pieces.

A game is a draw if neither player can win the game.

A game is also considered a draw when the same position repeats three times by the
same player (not necessarily consecutively).


Gameplay Directions

How to play the game?

Run the Warzone.py file using python compiler or command line.

Enter the size of the board you want to play on.

You will have a view of the board (2D and 3D).

You need to select the coordinates of one of your pieces that you want to move in the x,y format. 2D view can help you in that.

You will then have a list of all the available moves that piece you selected can take.

You need to select the index of the move you want to play. The indexing is zero based. i.e. 
if you want to play the 5th move, enter 4.

Your piece will move to the desired location.

Repeat the same directions for the second player.

Enjoy.
