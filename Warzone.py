from math import inf
import numpy as np
import re
import time
import torch as tr
import itertools as it
import matplotlib.pyplot as pt
import pickle as pk
from torch.nn import Sequential, Conv2d, Flatten,Linear

# Constants
USER = ["x","y"] # AI : 1, User: 2
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
    
#     Setup rocks
    rock_indices_x,rock_indices_y = np.random.randint(1,n-1,OBSTACLES[n-3]),np.random.randint(1,n-1,OBSTACLES[n-3])
    
    for i in range(len(rock_indices_x)):
        board[rock_indices_x[i]][rock_indices_y[i]] = Gem(ROCK,None)

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
    
    return board
    
def viewBoard(board):
    N = len(board)
    view = np.full((N+1,N+1),"_")
    for i in range(1,N+1):
        for j in range(1,N+1):
            if board[i-1][j-1] is not None:
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

#ALL action functions
def getMoves(board,location):
    x,y = location
    N = len(board)
    allmoves = []
    if (not validSpot(x,y,N) or emptySpot(board,x,y) or isRock(board,x,y)):
        return []
    currPiece = board[x][y].piece 
    if(board[x][y]!=None):
    #   print("Default ",moves," for ",piece)
        moves = currPiece.moves
        if currPiece.status==KING:
            for m in moves:
                i,j=x+m[0],y+m[1]
                while emptySpot(board,i,j):
                    N = len(board)
                    allmoves.append((i,j)) 
                    i,j=i+m[0],j+m[1]
        else:
            for m in moves:
                i,j=x+m[0],y+m[1]
                flag = False
    #                 for empty block
                if validSpot(i,j,N):
            
                    if board[i][j]==None:
                        flag = True
                        allmoves.append((i,j))
    #                 for filled block with user piece, then jump
                if flag==False:
                    while validSpot(i,j,N) and board[i][j]!=None and board[i][j].piece.user==currPiece.user :
                        i+=m[0]
                        j+=m[1]
                    if emptySpot(board,i,j):
                        N = len(board)
                        allmoves.append((i,j))                
    movelist = []
    for j in allmoves:
        move = Move(location,j,"Move",currPiece.user)
        movelist.append(move)
    return movelist


def getJumps(board,location):
    N = len(board)
    x,y = location
    jumps = []
    if (not validSpot(x,y,N) or emptySpot(board,x,y) or isRock(board,x,y)):
        return []

    currPiece = board[x][y].piece 

    if currPiece.status=="King":
        for m in board[x][y].piece.jumps:
            i,j=x+m[0],y+m[1]
            while emptySpot(board,i,j):
                N = len(board)
                i,j=i+m[0],j+m[1]
            if validSpot(i,j,N) and board[i][j].piece.user!=currPiece.user:
                i,j=i+m[0],j+m[1]
                if emptySpot(board,i,j):
                    N = len(board)
                    jumps.append((i,j))

    else:    
        for m in board[x][y].piece.jumps:
            i,j=x+m[0],y+m[1]
            if emptySpot(board,i,j):
                N = len(board)
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
        jump = Move(location,j,JUMP,currPiece.user)
        jumplist.append(jump)
    return jumplist


def movePiece(board, move):
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
    N = len(board)
    if validSpot(i,j,N) and board[i][j]==None:
        return True
    return False

def nonEmptySpot(board,i,j):
    N = len(board)
    if validSpot(i,j,N) and board[i][j]!=None:
        return True
    return False

def isRock(board,i,j):
    if nonEmptySpot(board,i,j) and board[i][j].piece.status==ROCK:
        return True
    return False

def validSpot(i,j,N):
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
    N = len(board)
    if (move.toloc[0]==0 and move.user!=USER[0]) or ( move.toloc[0]==N-1 and move.user!=USER[1]):
        king = Gem("King",move.user) 
        board[move.toloc[0]][move.toloc[1]]=king
            
def game_result(state):
    game_status,winner = game_over(state.board, state.turn)
    if (game_status and winner==""):
        print("The game has ended in draw.")
    elif (winner == USER[1]):
        print(USER[1]," has won the game.")
    elif  (winner == USER[0]):
        print(USER[0]," has won the game.")

    print("Game Over !!!")
    return game_status,winner

def checkIfUserHasMoves(board,user):
    flag = False
    m = np.where(board!=None)
    for i,j in zip(m[0],m[1]):
        if(board[i][j].piece.user==user):
            if getValidMoves(board,(i,j))!=[]:
                flag = True
                break
    return flag
           
# AI baseline

def baseline_AI(state):
    pieces = getAllPiecesOfUser(state.board, state.get_user())
    moves = getAllMovesFromPieces(state.board,pieces)
    x = int (np.random.randint(0,len(moves)))
    m = moves[x]
    return state.perform(m)


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
    

def minimax_AI(state):
    treeNodesChecked = 0
    N = len(state.board)
    player = 1 if state.turn %2==1 else -1
    board_copy = np.array(state.board,copy = True)
    move = minimax(board_copy, DEPTH[N-3], player, treeNodesChecked)
    return state.perform(move[0])


def minimax(board, depth, player, treeNodesChecked):
    turn = 1 if player==1 else 0
    if player == 1:
        best = [None, -inf, False, treeNodesChecked]
        user = USER[0]
    else:
        best = [None, +inf, False, treeNodesChecked]
        user = USER[1]
    
    status, winner = game_over(board,turn)
    if status:
        score = evaluateWinScore(winner)
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

def evaluateWinScore(winner):
    if (winner==USER[0]):
        return +100 
    elif (winner==USER[1]):
        return -100
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

def game_over(board,turn):
    a,b = checkIfUserHasMoves(board,USER[0]),checkIfUserHasMoves(board,USER[1])
    if turn%2==1 and not a:
        return True, USER[1]
    elif turn%2==0 and not b:
        return True, USER[0]
    
    return False,""

def playHuman(state):
    curUser = state.get_user()
    vm,ind = [],-1
    ch2 = input("Enter piece to get Moves: (in x,y coordinate format): ")
    while True:
        if re.match("[0-9],[0-9]",ch2):
            txt = ch2.split(",")
            m = []
            for i in txt:
                m.append(int(i))
            vm = viewValidMoves(state.board,m,curUser)
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

    return state.perform(vm[ind])

def encode(board):
    n = len(board)
    board_state = np.full((n,n),0.)
    for i in range(n):
        for j in range(n):
            if(board[i][j]!=None):
                if(board[i][j].piece.status==ROCK):
                    board_state[i][j]=3
                if(board[i][j].piece.status==KING):
                    if(board[i][j].piece.user==USER[0]):
                        board_state[i][j]=4
                    else:
                        board_state[i][j]=5
                if(board[i][j].piece.status==PAWN):
                    board_state[i][j]=2   
                if(board[i][j].piece.status==AI_PAWN):
                    board_state[i][j]=1       
    onehot = tr.zeros(6,n,n)
    for mv in range(6):
        x,y = tr.where(tr.tensor(board_state)==mv)
        for i,j in zip(x,y):
            onehot[mv][i][j]=1
    return onehot 

def decode(cnn_board):
    piece = [None,Gem(AI_PAWN,USER[0]),Gem(PAWN,USER[1]),Gem(ROCK,None),Gem(KING,USER[0]),Gem(KING,USER[1])]
    n = len(cnn_board[0])
    new_board = np.full((n,n),None)
    for mv in range(0,6):
        coordinates = tr.nonzero(cnn_board[mv])
        for pt in coordinates:
            new_board[pt[0]][pt[1]]=piece[mv]
    return new_board

def uniform(node):
    c = np.random.choice(len(node.children()))
    return node.children()[c]

def puct(node):
    c = np.random.choice(len(node.children()), p=puct_probs(node))
    return node.children()[c]

def puct_probs(node):
    probs = []
    node_visits = np.sum(node.get_visit_counts())
    for c in node.child_list:
        n_c = np.sum(c.visit_count)
        q_c = 0 if n_c==0 else np.sum(c.score_total)/n_c
        if(node.state.is_max_players_turn() == False and q_c!=0):
            q_c= -q_c
        u_c = q_c + (np.log(node_visits + 1)/ (n_c + 1))**0.5
        probs.append(u_c)
    
    return tr.softmax(tr.tensor(probs),dim=0)
    

class Node(object):
    def __init__(self, state, depth = 0, choose_method=uniform):
        self.state = state
        self.child_list = None
        self.visit_count = 0
        self.score_total = 0
        self.depth = depth
        self.choose_method = choose_method
    
    def make_child_list(self):
        self.child_list = []
        actions = self.state.valid_actions()
        for i in actions:
            temp_state = self.state.copy()
            child_state = temp_state.perform(i)
            child = Node(child_state,self.depth+1,self.choose_method)
            self.child_list.append(child)

    def children(self):
        if self.child_list is None: self.make_child_list()
        return self.child_list
    
    def get_score_estimates(self):
        score = np.array([0 if i.visit_count==0 else i.score_total/i.visit_count for i in self.child_list],dtype=float)
        if(self.state.is_max_players_turn() ):
            return score
        else:
            return -score
    
    def get_visit_counts(self):
        return np.array([i.visit_count for i in self.child_list])
    
    def choose_child(self):
        return self.choose_method(self)

def rollout(node, max_depth=None):
    if node.depth == max_depth or node.state.is_leaf():
        result = node.state.score_for_max_player()
    else:
        result = rollout(node.choose_child(), max_depth)
    node.visit_count += 1
    node.score_total += result
    return result

def decide_action(state, num_rollouts, choose_method=puct, max_depth=10, verbose=False):
    node = Node(state, choose_method=choose_method)
    for n in range(num_rollouts):
        if verbose and n % 10 == 0: print("Rollout %d of %d..." % (n+1, num_rollouts))
        rollout(node, max_depth=max_depth)
    return np.argmax(node.get_score_estimates()), node


class State(object):
    def __init__(self, size, turn,board=None):

        self.size = size # side length of board
        self.turn = turn # current player integer (1, 2, ...)

        if board is None: 
            board = setupBoard(USER[0],USER[1],self.size)
        self.board = board.copy()
        
        self.valid_action_list = None
        
    def __str__(self):
        viewBoard(self.board)
    
    def copy(self):
        return State(self.size, self.turn, self.board)
    
    def is_leaf(self):
        return game_over(self.board,self.turn)[0]
        
    def score_for_max_player(self):
        return evaluateCurrentScoreBasedOnPieces(self.board)
    
    def is_max_players_turn(self):
        return (self.turn % 2 == 1)
    
    def get_user(self):
        user = USER[1] if self.turn % 2==0 else USER[0]
        return user

    def valid_actions(self):
        if self.valid_action_list is not None:
            return self.valid_action_list
        
        user = USER[1] if self.turn % 2==0 else USER[0] 
    
        allPieces = getAllPiecesOfUser(self.board, user)
        actions = getAllMovesFromPieces(self.board, allPieces)

        # special case when no moves left for current player
        if len(actions) == 0: actions = [None]

        # cache results
        self.valid_action_list = actions
        
        return actions
    
    def perform(self, action):
        new_state = self.copy()
        new_state.turn = self.turn + 1

        if action is not None:
            movePiece(new_state.board,action)

        return new_state

def generate(board_size=3, num_games=1, num_rollouts=5, max_depth=4, choose_method=None):

    if choose_method is None: choose_method = puct

    data = []    
    for game in range(1,num_games+1):
    
        state = State(board_size, 0)
        for turn in it.count():
            print("game %d, turn %d..." % (game, turn))
    
            # Stop when game is over
            if state.is_leaf(): break
    
            # Act immediately if only one action available
            valid_actions = state.valid_actions()
            if len(valid_actions) == 1:
                state = state.perform(valid_actions[0])
                continue
            
            # Otherwise, use MCTS
            a, node = decide_action(state, num_rollouts, choose_method, max_depth)
            state = node.children()[a].state
            
            # Add child states and their values to the data
            Q = node.get_score_estimates()
            for c,child in enumerate(node.children()):
                data.append((child.state, Q[c]))

    return data

def get_batch(board_size=3, num_games=1, num_rollouts=100, max_depth=4, choose_method=None):
    data = generate(board_size,num_games,num_rollouts,max_depth,choose_method)
    n = len(data)
    input_data = []
    output_data = []
    for d in data:
        onehot = encode(d[0].board)
        input_data.append(onehot)
        output_data.append(d[1])

    output = tr.tensor(output_data,dtype=tr.float)
    output = tr.reshape(output,(n,1))
    
    inputs = tr.stack(input_data,0)
    inputs = tr.tensor(inputs,dtype=tr.float)
    
    tr.reshape(inputs,(n,6,board_size,board_size))

    return (inputs,output)

def Warzone_NN(board_size):
    m = Sequential(
        Flatten(),
        Linear(in_features=6*board_size*board_size, out_features=1,bias=True))
    return m

def calculate_loss(net, x, y_targ):
    y = net(x)
    e = tr.sum((y-y_targ)**2)
    return (y,e)

def optimization_step(optimizer, net, x, y_targ):
    optimizer.zero_grad()
    y,e = calculate_loss(net,x,y_targ)
    e.backward()
    optimizer.step()
    return (y,e)

def dump_data(board_size, num_games=50):
    inputs, outputs = get_batch(board_size, num_games=num_games)
    print(inputs[-1])
    print(outputs[-1])
    with open("Warzone_data_board_size_%d.pkl" % board_size, "wb") as f: pk.dump((inputs, outputs), f)
    
def train_model(board_size):
    net = Warzone_NN(board_size=board_size)
    
    with open("Warzone_data_board_size_%d.pkl" % board_size,"rb") as f: (x, y_targ) = pk.load(f)

    # Optimization loop
    optimizer = tr.optim.Adam(net.parameters())
    train_loss, test_loss = [], []
    shuffle = np.random.permutation(range(len(x)))
    split = 10
    train, test = shuffle[:-split], shuffle[-split:]
    for epoch in range(20000):
        y_train, e_train = optimization_step(optimizer, net, x[train], y_targ[train])
        y_test, e_test = calculate_loss(net, x[test], y_targ[test])
        if epoch % 10 == 0: print("%d: %f (%f)" % (epoch, e_train.item(), e_test.item()))
        train_loss.append(e_train.item() / (len(shuffle)-split))
        test_loss.append(e_test.item() / split)
    
    tr.save(net.state_dict(), "Warzone_nn_model%d.pth" % board_size)
    
    pt.plot(train_loss,'b-')
    pt.plot(test_loss,'r-')
    pt.legend(["Train","Test"])
    pt.xlabel("Iteration")
    pt.ylabel("Average Loss")
    pt.show()
    
    pt.plot(y_train.detach().numpy(), y_targ[train].detach().numpy(),'bo')
    pt.plot(y_test.detach().numpy(), y_targ[test].detach().numpy(),'ro')
    pt.legend(["Train","Test"])
    pt.xlabel("Actual output")
    pt.ylabel("Target output")
    pt.show()

def encode_state(state):
    n = len(state.board)
    board = state.board

    board_state = np.full((n,n),0.)
    for i in range(n):
        for j in range(n):
            if(board[i][j]!=None):
                if(board[i][j].piece.status=="Rock"):
                    board_state[i][j]=3
                if(board[i][j].piece.status=="King"):
                    if(board[i][j].piece.user=="x"):
                        board_state[i][j]=4
                    else:
                        board_state[i][j]=5
                if(board[i][j].piece.status=="Pawn"):
                    board_state[i][j]=2   
                if(board[i][j].piece.status=="AIPawn"):
                    board_state[i][j]=1       
    onehot = tr.zeros(6,n,n)

    for mv in range(6):
        x,y = tr.where(tr.tensor(board_state)==mv)
        for i,j in zip(x,y):
            onehot[mv][i][j]=1
    return onehot 

def nn_puct(node):
    with tr.no_grad():
        x = tr.stack(tuple(map(encode_state, [child.state for child in node.children()])))
        y = net(x)
        probs = tr.softmax(y.flatten(), dim=0)
        a = np.argmax(probs)
    return node.children()[a]

def nn_AI(state):
    a, node = decide_action(state, choose_method=nn_puct, num_rollouts=50, max_depth = 20, verbose=False)
    state = node.children()[a].state
    return state

def mixmatch(state):
    x = np.random.randint(1,101)
    if x<60:
        return baseline_AI(state)
    else:
        return minimax_AI(state)

def play_turn(player,state):
    if(player=="baseline"):
        return baseline_AI(state)
    elif (player=="minimax"):
        return minimax_AI(state)
    elif player=="human":
        return playHuman(state)
    elif player=="mixmatch":
        return mixmatch(state)
    else:
        return nn_AI(state)

def game_play(player1, player2, board_size, simulation=False):
    state = State(board_size,0)
    if(not simulation):
        viewBoard(state.board)
    while not state.is_leaf():
        if(state.turn % 2):
            print("Player 1 Turn ")
            state = play_turn(player1,state)               
        else:
            print("Player 2 Turn ")
            state = play_turn(player2,state)
        
        if(not simulation):
            viewBoard(state.board)
            print("\n")
    winner = game_result(state)[1]
    return state, winner

def evaluate_board(board):
    x,y=0,0
    m = np.where(board!=None)
    for i,j in zip(m[0],m[1]):
        if(board[i][j].piece.status!=ROCK ):
            if(board[i][j].piece.user==USER[0]):
                if PAWN in board[i][j].piece.status:
                    x+=1 
                else:
                    x+=3
            else:
                if PAWN in board[i][j].piece.status:
                    y+=1 
                else:
                    y+=3
    return x,y


if __name__ == "__main__":

    
    USER = ["x","y"] # AI : 1, User: 2
    print("---------------------------------------------")
    print("        ***   Welcome to Warzone   ***       ")
    print("---------------------------------------------")
    print()
    n = input("Please enter board size (3-7): ")

    while n not in ["3","4","5","6","7"]:
        n = input("Please enter a valid board size: ")
    N = int(n)
    
    net = Warzone_NN(N)
    net.load_state_dict(tr.load("Warzone_nn_model%d.pth" %N))
    
    print("1. Human (Play with friends)")
    print("2. Baseline AI (Easy and fun)")
    print("3. Tree-Based AI (if you are looking for a challenge)")
    print("4. Neural-Networks + Tree-Based AI")
    print()
    ai=input("Please enter the AI you want to play against(1, 2, 3, 4)")
    while ai not in ["1","2","3","4"]:
        ai = input("Please enter a valid AI choice: ")
    
    player_1 = ""
    if(ai=="1"):
        player_1 = "human"
    elif (ai==2):
        player_1 = "baseline"
    elif (ai==3):
        player_1 = "minimax"
    else:
        player_1 = "neural"

    game_play(player_1,"human",N)


    print("---------------------------------------------")
    print("       ***   Thank you for playing   ***     ")
    print("---------------------------------------------")
 
