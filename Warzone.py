from math import inf
import numpy as np
import re
import time

# Constants
ROCK = "Rock"
KING = "King"
PAWN = "Pawn"
AI_PAWN = "AIPawn"
JUMP = "Jump"
MOVE = "Move"
DEPTH = [3,3,3,3,3,3]
OBSTACLES = [0,2,4,6,8,10]

class Piece:
    status = None
    moves = None
    user = None
    jumps = [[-2,0],[0,2],[2,0],[0,-2]]
    
    def __init__(self, status, moves, jumps, user):
        self.moves = moves
        self.user = user
        self.jumps = jumps

class Rock(Piece):
    status = ROCK
    def __init__(self):
        Piece.__init__(self, self.status,None,None,None)
        
class Pawn(Piece):
    status = PAWN
    moves = [[-1,0],[-1,-1],[-1,1]]
    jumps = [[-2,0],[0,2],[0,-2]]
    def __init__(self, user):
        Piece.__init__(self, self.status, self.moves, self.jumps, user)

class AIPawn(Piece):
    status = AI_PAWN
    moves = [[1,0],[1,-1],[1,1]]
    jumps = [[0,2],[2,0],[0,-2]]
    def __init__(self, user):
        Piece.__init__(self, self.status, self.moves, self.jumps, user)

class King(Piece):
    status = KING
    moves = [[1,0],[0,1],[-1,0],[0,-1],[1,1],[1,-1],[-1,-1],[-1,1]]
    jumps = [[-1,0],[0,1],[1,0],[0,-1]]
    def __init__(self, user):
        Piece.__init__(self, self.status, self.moves, self.jumps, user)

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

    if (n>8 or n<3 ):
        print("Please enter a valid board size(3-8): ")
        return
    
    #     Setup rocks
    rock_indices_x,rock_indices_y = np.random.randint(1,N-1,OBSTACLES[N-3]),np.random.randint(1,N-1,OBSTACLES[N-3])
    
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
    
def viewBoard(board):
    view = np.full((N+1,N+1),"_")
    for i in range(1,N+1):
        for j in range(1,N+1):
            if board[i-1][j-1]!=None:
                if board[i-1][j-1].piece.status==KING:
                    view[i][j]=str(board[i-1][j-1].piece.user).upper()
                elif board[i-1][j-1].piece.status==ROCK:
                    view[i][j]="o"
                else:
                    view[i][j]=str(board[i-1][j-1].piece.user)
    view[0]=np.arange(-1,N)
    for i in range(-1,N):
        view[i+1][0]=i
    view[0][0]="#"
    print(view)
    # print("3D-view")
    # updateCnnBoard()
    # print(cnn_board)
    
def resetBoard():
    return setupBoard(USER[0],USER[1],N),[]


#ALL action functions
def getMoves(board,location):
    x,y = location
    allmoves = []
    if (not validSpot(x,y) or emptySpot(board,x,y) or isRock(board,x,y)):
    #   print("Invalid location")
        return []
    currPiece = board[x][y].piece 
    if(board[x][y]!=None):
    #   print("Default ",moves," for ",piece)
        moves = currPiece.moves
        if currPiece.status=="King":
            for m in moves:
                i,j=x+m[0],y+m[1]
                while emptySpot(board,i,j):
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
                    if emptySpot(board,i,j):
                        allmoves.append((i,j))                
    movelist = []
    for j in allmoves:
        move = Move(location,j,"Move",currPiece.user)
        movelist.append(move)
    return movelist


def getJumps(board,location):
    x,y = location
    jumps = []
    if (not validSpot(x,y) or emptySpot(board,x,y) or isRock(board,x,y)):
    #         print("Invalid location")
        return []

    currPiece = board[x][y].piece 

    if currPiece.status=="King":
        for m in board[x][y].piece.jumps:
            i,j=x+m[0],y+m[1]
            while emptySpot(board,i,j):
                i,j=i+m[0],j+m[1]
            if validSpot(i,j) and board[i][j].piece.user!=currPiece.user:
                i,j=i+m[0],j+m[1]
                if emptySpot(board,i,j):
                    jumps.append((i,j))

    else:    
        for m in board[x][y].piece.jumps:
            i,j=x+m[0],y+m[1]
            if emptySpot(board,i,j):
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


def movePiece(board, move):
    # recentMoves.insert(0,move)
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
                if ( isRock(board,x,y) ):
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
                if ( isRock(board,x,y) ):
                    continue
                else:
                    board[x][y]=None
    if currPiece.status!="King":
        checkPromotion(board, move)

        
# helper functions
def emptySpot(board,i,j):
    if validSpot(i,j) and board[i][j]==None:
        return True
    return False

def nonEmptySpot(board,i,j):
    if validSpot(i,j) and board[i][j]!=None:
        return True
    return False

def isRock(board,i,j):
    if nonEmptySpot(board,i,j) and board[i][j].piece.status==ROCK:
        return True
    return False

def validSpot(i,j):
    if i>=0 and i<N and j>=0 and j<N:
        return True
    return False

def getValidMoves(board,location):
    allmoves = getMoves(board,location)
    jps = getJumps(board,location)
    allmoves.extend(jps)
    return allmoves

def viewValidMoves(board,location,curUser):
    allmoves = getValidMoves(board,location)
    if(allmoves!=[] and board[location[0],location[1]].piece.user!=curUser):
        return []
    temp = []
    for i in allmoves:
        if(isinstance(i,Move)):
            temp.append(i.toloc)
    print(temp)
    return allmoves

def checkPromotion(board, move):
    if (move.toloc[0]==0 and move.user!=USER[0]) or ( move.toloc[0]==N-1 and move.user!=USER[1]):
        king = Gem("King",move.user) 
        board[move.toloc[0]][move.toloc[1]]=king
    
def viewRecentMoves():
    for i in recentMoves:
        print("User: ",i.user," From: ",i.fromloc," To: ",i.toloc)
        
def game_result(board):
    game_status,winner = game_over(board)
    if (game_status):
        if (winner==""):
            print("The game has ended in draw.")
        elif (winner == USER[1]):
            print(USER[1]," has won the game.")
        elif  (winner == USER[0]):
            print(USER[0]," has won the game.")

        print("Game Over !!!")
        return game_status

def checkIfUserHasMoves(board,user):
    flag = False
    m = np.where(board!=None)
    for i,j in zip(m[0],m[1]):
        if(board[i][j].piece.user==user):
            if getValidMoves(board,(i,j))!=[]:
                flag = True
                break
    return flag

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
                
# AI baseline

def baselineMoveMaker(user,board):
    pieces = getAllPiecesOfUser(board, user)
    moves = getAllMovesFromPieces(board,pieces)
    x = int (np.random.randint(0,len(moves)))
    m = moves[x]
    movePiece(board, m)

def getAllPiecesOfUser(board,user):
    pieces = []
    m = np.where(board!=None)
    for i,j in zip(m[0],m[1]):
        if(board[i][j].piece.user==user):
            pieces.append((i,j))
    return pieces
    
def getAllMovesFromPieces(board, pieces):
    comb = []
    for i in pieces:
        moves=getValidMoves(board,i)
        comb.extend(moves)
    return comb
    

def callMinimax(board, treeNodesChecked, N):
    board_copy = np.array(board,copy = True)
    move = minimax(board_copy, DEPTH[N-3], +1, treeNodesChecked)
    movePiece(board,move[0])
    return move[3]


def minimax(board, depth, player, treeNodesChecked):
    if player == 1:
        best = [None, -inf, False, treeNodesChecked]
        user = USER[0]
    else:
        best = [None, +inf, False, treeNodesChecked]
        user = USER[1]
    
    if game_over(board)[0]:
        score = evaluateWinScore(board)
        return [None, score, True, treeNodesChecked]
    elif depth==0:
        score = evaluateCurrentScoreBasedOnPieces(board)
        return [None, score, False, treeNodesChecked]
    
    allPieces = getAllPiecesOfUser(board, user)
    allMoves = getAllMovesFromPieces(board, allPieces)
    
    for i in allMoves:
        treeNodesChecked+=1
        board_copy = np.array(board,copy=True)
        movePiece(board_copy,i)
        score = minimax(board_copy, depth-1, -player, treeNodesChecked)
        score[0] = i

        if player == +1:
            if score[1] > best[1]:
                best = score  # max value
        else:
            if score[1] < best[1]:
                best = score  # min value
        
    best[3]+= treeNodesChecked
    return best

def evaluateWinScore(board):
    result,winner = game_over(board)

    if(result):
        if (winner==USER[0]):
           return +100 
        elif (winner==USER[1]):
            return -100
        else:
            return 0
    else:
        return 0

def evaluateCurrentScoreBasedOnPieces(board):
    x,y,X,Y=0,0,0,0
    m = np.where(board!=None)
    for i,j in zip(m[0],m[1]):
        if(board[i][j].piece.status!=ROCK ):
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
    return (x + (3 * X)) - (y + (3 * Y))

def game_over(board):
    a,b = checkIfUserHasMoves(board,USER[0]),checkIfUserHasMoves(board,USER[1])
    if not a and not b:
        return True, ""
    elif not a:
        return True, USER[1]
    elif not b:
        return True, USER[0]
    
    return False,""

def playHuman(curUser):
    print("Your Turn ")
    viewBoard(board)
    vm,ind = [],-1
    ch2 = input("Enter piece to get Moves: (in x,y coordinate format): ")
    while True:
        if re.match("[0-9],[0-9]",ch2):
            txt = ch2.split(",")
            m = []
            for i in txt:
                m.append(int(i))
            vm = viewValidMoves(board,m,curUser)
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
    movePiece(board, vm[ind])

def main(ai):
    turn = 0
    while not game_result(board):
        curUser = USER[1] if turn%2 == 0 else USER[0]
        if(curUser==USER[0]):
            if (ai=="1"):
                baselineMoveMaker(USER[0],board)
            else:
                treeNodesChecked = 0
                treeNodesChecked = callMinimax(board, treeNodesChecked, N)
                print(" Tree nodes traversed by AI: ",treeNodesChecked)
        else:
            playHuman(curUser)
            viewBoard(board)
        turn+=1

        print("\n")

if __name__ == "__main__":
    USER = ["x","y"] # AI : 1, User: 2
    recentMoves = []
    game_status = False
    winner = None
    print("---------------------------------------------")
    print("        ***   Welcome to Warzone   ***       ")
    print("---------------------------------------------")
    print()
    n = input("Please enter board size (3-7): ")

    while n not in ["3","4","5","6","7","8"]:
        n = input("Please enter a valid board size: ")
    N = int(n)

    print("1. Baseline AI (Easy and fun)")
    print("2. Tree-Based AI (if you are looking for a challenge)")
    print()
    ai=input("Please enter the AI you want to play against(1,2)")
    while ai not in ["1","2"]:
        ai = input("Please enter a valid AI choice: ")
    
    board,cnn_board = setupBoard(USER[0],USER[1],N)
    treeNodesChecked = 0

    main(ai) 
    
    print("---------------------------------------------")
    print("       ***   Thank you for playing   ***     ")
    print("---------------------------------------------")
    

