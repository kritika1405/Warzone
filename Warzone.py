import numpy as np
import torch as tr
import re


# Constants
ROCK = "Rock"
KING = "King"
PAWN = "Pawn"
AI_PAWN = "AIPawn"
JUMP = "Jump"
MOVE = "Move"


class Piece:
    status = None
    moves = None
    user = None
    jumps = [[-2,0],[0,2],[2,0],[0,-2]]
    def __init__(self, status, moves, user):
        self.moves = moves
        self.user = user

class Rock(Piece):
    status = ROCK
    def __init__(self):
        Piece.__init__(self, self.status,None,None)
        
class Pawn(Piece):
    status = PAWN
    moves = [[-1,0],[-1,-1],[-1,1]]
    def __init__(self, user):
        Piece.__init__(self, self.status, self.moves, user)

class AIPawn(Piece):
    status = AI_PAWN
    moves = [[1,0],[1,-1],[1,1]]
    def __init__(self, user):
        Piece.__init__(self, self.status, self.moves, user)

class King(Piece):
    status = KING
    moves = [[1,0],[0,1],[-1,0],[0,-1],[1,1],[1,-1],[-1,-1],[-1,1]]
    jumps = [[-1,0],[0,1],[1,0],[0,-1]]
    def __init__(self, user):
        Piece.__init__(self, self.status, self.moves, user)

class Gem:
    piece = None
    user = None
    def __init__(self,piece,user):
        if(piece==PAWN):
            self.piece = Pawn(user)
        elif(piece==AI_PAWN):
            self.piece = AIPawn(user)
        elif(piece==KING):
            self.piece = King(user)
        elif(piece==ROCK):
            self.piece = Rock()

class Move:
    fromloc = None
    toloc = None
    kind = JUMP or MOVE
    user = None
    def __init__(self,fromloc,toloc,kind,user):
        self.fromloc = fromloc
        self.toloc   = toloc
        self.kind    = kind
        self.user    = user


def setupBoard(a,b,n):
    board = np.full((n,n),None)
    cnn_board = np.full((n,n,4),0)
    game_over = False
    winner = None
    recentMoves = []

    if (n>8 or n<3 ):
        print("Please enter a valid board size(3-8): ")
        return
    
#     Setup rocks
    rock_indices_x,rock_indices_y = np.random.randint(1,N-1,2),np.random.randint(1,N-1,2)
    
    for i in range(len(rock_indices_x)):
        board[rock_indices_x[i]][rock_indices_y[i]] = Gem(ROCK,None)
#     print(rock_indices_x,rock_indices_y)

    
    board_setup = [[],[],[],[(0,n)],[(0,n)],[(0,n),(1,n-1)],[(0,n),(1,n-1)],[(0,n),(1,n-1),(2,n-2)],[(0,n),(1,n-1),(2,n-2)]]
#     setup AI piece
    for i in board_setup[n]:
        x,y=i
        for j in range(x,y):
            board[x][j] = Gem(AI_PAWN,a)
    
#     setup User piece
    for i in board_setup[n]:
        x,y=i
        for j in range(x,y):
            board[n-x-1][j] = Gem(PAWN,b)
    
    return board,cnn_board
    
def viewBoard():
    view = np.full((N+1,N+1),"_")
    for i in range(1,N+1):
        for j in range(1,N+1):
            if board[i-1][j-1]!=None:
                if board[i-1][j-1].piece.status==KING:
                    view[i][j]=str(board[i-1][j-1].piece.user).upper()
                elif board[i-1][j-1].piece.status==ROCK:
                    view[i][j]='o'
                else:
                    view[i][j]=str(board[i-1][j-1].piece.user)
    view[0]=np.arange(-1,N)
    for i in range(-1,N):
        view[i+1][0]=i
    view[0][0]='#'
    print(view)
    print()
    print("3D-view")
    updateCnnBoard()
    print(cnn_board)
    
def resetBoard():
    return setupBoard(USER[0],USER[1],N),[]


#ALL action functions
def getMoves(location):
    x,y = location
    allmoves = []
    if (not validSpot(x,y) or emptySpot(x,y) or isRock(x,y)):
#         print("Invalid location")
        return []
    currPiece = board[x][y].piece 
    if(board[x][y]!=None):
#       print("Default ",moves," for ",piece)
        moves = currPiece.moves
        if currPiece.status=="King":
            for m in moves:
                i,j=x+m[0],y+m[1]
                while emptySpot(i,j):
                    allmoves.append((i,j)) 
                    i,j=i+m[0],j+m[1]
        else:
            for m in moves:
                i,j=x+m[0],y+m[1]
                flag = False
#                 for empty block
                if validSpot(i,j):
                    if board[i][j]==None:
                        flag = True
                        allmoves.append((i,j))
#                 for filled block with user piece, then jump
                if flag==False:
                    while validSpot(i,j) and board[i][j]!=None and board[i][j].piece.user==currPiece.user :
                        i+=m[0]
                        j+=m[1]
                    if emptySpot(i,j):
                        allmoves.append((i,j))                
    movelist = []
    for j in allmoves:
        move = Move(location,j,"Move",currPiece.user)
        movelist.append(move)
    return movelist


def getJumps(location):
    x,y = location
    jumps = []
    if (not validSpot(x,y) or emptySpot(x,y) or isRock(x,y)):
#         print("Invalid location")
        return []

    currPiece = board[x][y].piece 
    
    if currPiece.status=="King":
        for m in board[x][y].piece.jumps:
            i,j=x+m[0],y+m[1]
            while emptySpot(i,j):
                i,j=i+m[0],j+m[1]
            if validSpot(i,j) and board[i][j].piece.user!=currPiece.user:
                i,j=i+m[0],j+m[1]
                if emptySpot(i,j):
                    jumps.append((i,j))
            
    else:    
        for m in board[x][y].piece.jumps:
            i,j=x+m[0],y+m[1]
            if emptySpot(i,j):
                if x==i and j>y and board[i][j-1]!=None and board[i][j-1].piece.user!=currPiece.user:
                    jumps.append((i,j))
                elif x==i and j<y and board[i][j+1]!=None and board[i][j+1].piece.user!=currPiece.user:
                    jumps.append((i,j))
                elif y==j and i>x and board[i-1][j]!=None and board[i-1][j].piece.user!=currPiece.user:
                    jumps.append((i,j))
                elif y==j and i<x and board[i+1][j]!=None and board[i+1][j].piece.user!=currPiece.user:
                    jumps.append((i,j))

    jumplist = []
    for j in jumps:
#         print(currPiece.user)
        jump = Move(location,j,JUMP,currPiece.user)
        jumplist.append(jump)
    return jumplist
       
    
def movePiece(move):
    recentMoves.insert(0,move)
    fromlocation, tolocation = move.fromloc,move.toloc
    currPiece = board[fromlocation[0]][fromlocation[1]].piece
    board[tolocation[0]][tolocation[1]] = board[fromlocation[0]][fromlocation[1]]
    board[fromlocation[0]][fromlocation[1]] = None
    if move.kind=="Jump":
        if fromlocation[0]==tolocation[0]:
            x=fromlocation[0]
            start,end=0,0
            if tolocation[1]<fromlocation[1]:
                start = tolocation[1]+1
                end = fromlocation[1]
            else:
                start = fromlocation[1]+1
                end = tolocation[1]
            for y in range(start,end):
                if ( isRock(x,y) ):
                    continue
                else:
                    board[x][y]=None
        if fromlocation[1]==tolocation[1]:
            y=fromlocation[1]
            start,end=0,0
            if tolocation[0]<fromlocation[0]:
                start = tolocation[0]+1
                end = fromlocation[0]
            else:
                start = fromlocation[0]+1
                end = tolocation[0]
            for x in range(start,end):
                if ( isRock(x,y) ):
                    continue
                else:
                    board[x][y]=None
    if currPiece.status!="King":
        checkPromotion(move)


# helper functions
def emptySpot(i,j):
    if validSpot(i,j) and board[i][j]==None:
        return True
    return False

def nonEmptySpot(i,j):
    if validSpot(i,j) and board[i][j]!=None:
        return True
    return False

def isRock(i,j):
    if nonEmptySpot(i,j) and board[i][j].piece.status==ROCK:
        return True
    return False

def validSpot(i,j):
    if i>=0 and i<N and j>=0 and j<N:
        return True
    return False

def getValidMoves(location):
    x,y = location
    allmoves = getMoves(location)
    jps = getJumps(location)
    allmoves.extend(jps)
    return allmoves

def viewValidMoves(location,curUser):
    allmoves = getValidMoves(location)
    if(allmoves!=[] and board[location[0],location[1]].piece.user!=curUser):
        return []
    temp = []
    for i in allmoves:
        if(isinstance(i,Move)):
            temp.append(i.toloc)
    print(temp)
    return allmoves

def checkPromotion(move):
    if (move.toloc[0]==0 and move.user!=USER[0]) or ( move.toloc[0]==N-1 and move.user!=USER[1]):
        print("Promotion move")
        promoteToKing(move)

def promoteToKing(move):
    #print(" promoting to king ")
    king = Gem("King",move.user) 
    board[move.toloc[0]][move.toloc[1]]=king
    
def viewRecentMoves():
    for i in recentMoves:
        print("User: ",i.user," From: ",i.fromloc," To: ",i.toloc)
        
def evaluate():
    game_over,winner = False,None
    x,y,X,Y=0,0,0,0
    for i in range(N):
        for j in range(N):
            if(nonEmptySpot(i,j) and board[i][j].piece.status!=ROCK ):
                if(board[i][j].piece.user==USER[0]):
                    if PAWN in board[i][j].piece.status:
                        x+=1 
                    else:
                        X+=1
                else:
                    if PAWN in board[i][j].piece.status:
                        y+=1 
                    else:
                        Y+=1
#     print("User 1 has ",x+X,"pieces left.","\nUser 2 has ",y+Y,"pieces left.")
    
    if (x+X)==0:
        game_over=True
        winner = USER[1]
        print(USER[1]," has won the game.")    
        return game_over,winner
    
    if (y+Y)==0 :
        game_over=True
        winner = USER[0]
        print(USER[0]," has won the game.")
        return game_over,winner
        
    a,b = evaluateIfUserHasMoves(USER[0]),evaluateIfUserHasMoves(USER[1])
    if not a and not b:
        game_over=True
        winner = "Draw"
        print("The game has ended in draw.")
    elif not a:
        game_over=True
        winner = USER[1]
        print(USER[1]," has won the game.")
    elif not b:
        game_over=True
        winner = USER[0]
        print(USER[0]," has won the game.")
    
    return game_over,winner

def evaluateIfUserHasMoves(user):
    flag = False
    for i in range(N):
        for j in range(N):
            if(nonEmptySpot(i,j) and board[i][j].piece.user==user ):
                if getValidMoves((i,j))!=[]:
                    flag = True
                    break
    return flag

#Encoding for CNN
space = [1,0,0,0]
x_pawn = [0,1,0,0]
y_pawn = [0,0,1,0]
obstacle = [0,0,0,1]
x_king = [0,2,0,0]
y_king = [0,0,2,0]

def updateCnnBoard():
    for i in range(N):
        for j in range(N):
            if board[i][j]!=None:
                if board[i][j].piece.status==KING:
                    if board[i][j].piece.user==USER[0]:
                        cnn_board[i][j]=x_king
                    else:
                        cnn_board[i][j]=y_king
                elif board[i][j].piece.status==ROCK:
                    cnn_board[i][j]= obstacle
                elif board[i][j].piece.status==PAWN:
                    cnn_board[i][j]= y_pawn
                elif board[i][j].piece.status==AI_PAWN:
                    cnn_board[i][j]= x_pawn
            else:
                cnn_board[i][j]= space


turn = 0
USER = ["x","y"] # AI : 1, User: 2
recentMoves = []
game_over = False
winner = None


#Game Play

if __name__ == "__main__":

    print("Welcome to Warzone")
    n = input("Please enter board size (3-8): ")

    while True:
        if n not in ["3","4","5","6","7","8"]:
            n = input("Please enter a valid board size: ")
        else:
            N = int(n)
            break
    board,cnn_board = setupBoard(USER[0],USER[1],N)

    while True:
        curUser = USER[1] if turn%2 == 0 else USER[0]
        print("Turn of ",curUser)
        turn+=1
        viewBoard()
        vm,ind = [],-1
        ch2 = input("Enter piece to get Moves: (in x,y coordinate format): ")
        while True:
            if re.match("[0-9],[0-9]",ch2):
                txt = ch2.split(",")
                m = []
                for i in txt:
                    m.append(int(i))
                vm = viewValidMoves(m,curUser)
                if vm!=[]:
                    break
                else:
                    ch2 =input("Please choose a valid piece: ")
            else:
                ch2 =input("Please choose a valid piece: ")
        ch3 = input("Enter Move: (index of move you want, use 0th-indexing) ")
        while True:
            if re.match("[0-9]+",ch3):
                ind = int(ch3)
                if (ind>=0 and ind<len(vm)):
                    break
                else:
                    ch3 =input("Please choose a valid move: ")
            else:
                ch3 =input("Please choose a valid move: ")
        movePiece(vm[ind])
        print()
        print("Recent Moves Played ")
        viewRecentMoves()
        game_over, winner = evaluate()
        
        if game_over:
            print("Game Over !!!")
            break
        print("\n")
        