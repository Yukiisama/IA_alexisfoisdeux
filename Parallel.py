# -*- coding: utf-8 -*- 
from math import *
import time
import Reversi
import Reversi2
from random import randint , choice,shuffle
from playerInterface import *
import threading
from threading import Thread
import queue

class ZobristTable():
    def __init__(self):
        self.table_size = 500
        self.table = [None for i in range(self.table_size)]
    def getEntry(self,hashkey):
        entry = self.table[((hashkey % self.table_size) + self.table_size) % self.table_size]
        if entry != None and entry.hashkey == hashkey : 
            return entry
        return None
    def storeEntry(self,entry):
        #print("Store entry with hashkey : ",entry.hashkey)
        pos = ((entry.hashkey % self.table_size) + self.table_size) % self.table_size
        if self.table[pos] == None : self.table[pos] = entry
        else : 
            if entry.depth > self.table[pos].depth : self.table[pos] = entry

        

class ZobristTableEntry():
    def __init__(self,hashkey,minscore,maxscore,move,depth):
        self.hashkey = hashkey
        self.minscore= minscore
        self.maxscore = maxscore
        self.move = move
        self.depth = depth

class ZobristHash():
    def __init__(self):
        self.tab = [[[randint(1,2**100) for color in range(3)]
                    for y in range(10)]
                    for x in range(10)] 
                    # array 10x10x3

    def GetHash(self,board):
        key = 0
        for x in range(10):
            for y in range(10):
                #we don't take care of empty cells
                piece = board._board[x][y]
                if(piece != board._EMPTY):
                    key ^= self.tab[x][y][piece]
        return key

#Use for parallelisation of alpha beta , makes a copy of the board to work with
class MyThread(Thread):
 
    def __init__(self, board,alpha,beta,move,color,profMax,joueurEnBlanc):
        Thread.__init__(self)
        self.board = Reversi2.Board(10)
        self.board._nextPlayer = board._nextPlayer
        self.board._mycolor = color
        #self.board._cpt_move = board._cpt_move
        self.alpha = alpha
        self.beta = beta
        self.move = move
        self.profMax = profMax
        self.joueurEnBlanc = joueurEnBlanc
        for x in range(10):
            for y in range(10):
                self.board._board[x][y] = board._board[x][y]

    def run(self):
        self.board.push(self.move)
        f(self.board,self.alpha,self.beta,self.move,self.profMax,self.joueurEnBlanc)
        self.board.pop()

zobrist_hash= None
zobrist = ZobristHash()
zobristtable = ZobristTable()

#The class Player 
class myPlayer(PlayerInterface):
    
    def __init__(self):
        self._board = Reversi.Board(10)
        self._mycolor = None
        self._cpt_move = 0
        global zobrist_hash
        zobrist_hash = ZobristHash().GetHash(self._board)

    def getPlayerName(self):
        return "AlphaBeta Parallel"

    def getPlayerMove(self):
        global zobrist_hash
        self._cpt_move+=1
        if self._board.is_game_over():
            print("Referee told me to play but the game is over!")
            return (-1,-1)
        moves = [m for m in self._board.legal_moves()]
        move = moves[0] #If only one move no need to alphabeta 
        # CORNER KILLER MOVE
        if([self._mycolor,0,0] in moves):
            move = [self._mycolor,0,0]
        elif([self._mycolor,0,9] in moves):
            move = [self._mycolor,0,9]
        elif([self._mycolor,9,0] in moves):
            move = [self._mycolor,9,0]
        elif([self._mycolor,9,9] in moves):
            move = [self._mycolor,9,9]
        #Late game A VERIFIER JE SUIS PAS SUR DU COMPORTEMENT
        elif(len(moves)>1 and self._cpt_move>80):
            move = IAMinMaxAlphaBetaPruning(self._board,0,1,self._mycolor,12,True) #objectif au moins 16 mais prends du temps
        elif(len(moves)>1):
            move = IAMinMaxAlphaBetaPruning(self._board,-inf,+inf,self._mycolor,5,True) # à faire false si noir , true si blanc max 8 avec heuristic pourri je
        self._board.push(move)
        zobrist_hash ^= zobrist.tab[move[1]][move[2]][move[0]]
        
        print("I am playing ", move)
        (c,x,y) = move
        assert(c==self._mycolor)
        print("My current board :")
        print(self._board)
        return (x,y) 

    def playOpponentMove(self, x,y):
        global zobrist_hash
        self._cpt_move+=1
        assert(self._board.is_valid_move(self._opponent, x, y))
        print("Opponent played ", (x,y))
        self._board.push([self._opponent, x, y])
        zobrist_hash ^= zobrist.tab[x][y][self._opponent]

    def newGame(self, color):
        self._mycolor = color
        self._opponent = 1 if color == 2 else 2

    def endGame(self, winner):
        if self._mycolor == winner:
            print("I won!!!")
        else:
            print("I lost :(!!")

nbNods = 0

def maxValue(b,alpha,beta,prof,profMax = 3, joueurEnBlanc = True):
    global nbNods
    global zobrist_hash
    nbNods += 1
    if b.is_game_over():
        return 1
    
    entry = zobristtable.getEntry(zobrist.GetHash(b))
    if entry != None :
        
        if entry.depth >= profMax: return entry.maxscore
    
    if profMax == 0:
        eval = 78.982 * b.mobility_heuristique() + 10* b.piecediff_heuristique()+801.24*b.corners_heuristique()+382.026 * b.CornerClose_heuristique() 
                
        

        return eval 
    else:
        for moves in b.legal_moves():
            b.push(moves)
            old = zobrist_hash
            zobrist_hash ^= zobrist.tab[moves[1]][moves[2]][moves[0]]
            alpha = max(alpha, minValue(b,alpha,beta,prof,profMax -1,joueurEnBlanc))
            b.pop()
            if alpha >= beta:
                new_entry = ZobristTableEntry(zobrist_hash,beta,alpha,moves,prof)
                zobristtable.storeEntry(new_entry)
                return beta
            zobrist_hash = old
    return alpha

def minValue(b,alpha,beta,prof,profMax = 3,joueurEnBlanc = True):
    global nbNods
    global zobrist_hash
    nbNods += 1
    if b.is_game_over(): 
        return 1
   

    entry = zobristtable.getEntry(zobrist.GetHash(b))
    if entry != None :
        
        if entry.depth >= profMax: return entry.minscore
    
    if profMax == 0:
        eval = 78.982 * b.mobility_heuristique() + 10* b.piecediff_heuristique()+801.24*b.corners_heuristique()+382.026 * b.CornerClose_heuristique()
        
        return eval
    else:
        for moves in b.legal_moves():
            b.push(moves)
            old = zobrist_hash
            zobrist_hash ^= zobrist.tab[moves[1]][moves[2]][moves[0]]
            beta = min(beta, maxValue(b,alpha,beta, prof, profMax -1,joueurEnBlanc))
            b.pop()
            if alpha>=beta:
                new_entry = ZobristTableEntry(zobrist_hash,beta,alpha,moves,prof)
                zobristtable.storeEntry(new_entry)
                return alpha
            zobrist_hash = old
    return beta

Q = queue.Queue()
def IAMinMaxAlphaBetaPruning(b,alpha,beta,color, profMax = 3, joueurEnBlanc = True):
    global nbNods
    nbNods += 1
    threads = []
    resultats = []
    list_move = b.legal_moves()
    shuffle(list_move)
    for move in list_move:
        threads.append(MyThread(b,alpha,beta,move,color, profMax - 1,joueurEnBlanc))
    for th in threads:
        th.start()
    for i in range(len(b.legal_moves())):
        resultats.append(Q.get())
    max_tuple = resultats[0] # max_tuple = (move,val)
    print("Result 0 ",max_tuple)
    for i in range(len(resultats)):

        if resultats[i][1] > max_tuple[1]:
            max_tuple = resultats[i]
        print("Max tuple : ",max_tuple)
        print("Resultats : ",resultats[i])
    print(max_tuple)
    return max_tuple[0]


def f(b,alpha,beta,move,profMax = 3, joueurEnBlanc = True):
    #b.push(move)
    val = maxValue(b,alpha,beta,profMax-1, profMax - 1,joueurEnBlanc)
    Q.put((move,val))
    #b.pop()
