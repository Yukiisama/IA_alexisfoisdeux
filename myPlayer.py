# -*- coding: utf-8 -*-

import time
import Reversi
import Reversi2
from random import randint
from playerInterface import *
import math
import time

#mobi,piecediff,corners,CornerClose,layers,diagonal,stability,front
#########GLOBALS##############
tab_greed = [0,0,0,  2,1/10,0,0,0]#
tab_early = [1/4,0,0,2,1/10,0,0,0]#
tab_mid   = [1/4,0,0,2,1/10,0,1,0]#
tab_late =  [1/4,0,0,2,1/10,0,1,0]
                             #
nbmove = 0                   #
MAX = 10000000               #
MIN =-10000000               #
##############################
#################################EVALUATE NODES#####################################################################
def evaluation(nbmove,b,mobi,piecediff,corners,CornerClose,layers,diagonal,stability,front):
    eval = 0
    if(mobi!=0):        eval += mobi        * b.mobility_heuristique() 
    if(piecediff!=0):   eval += piecediff   * b.piecediff_heuristique()
    if(corners!=0):     eval += corners     * b.corners_heuristique()
    if(CornerClose!=0): eval += CornerClose * b.CornerClose_heuristique() 
    if(layers!=0):      eval += layers      * b.static_layers_heuristique()
    if(diagonal!=0):    eval += diagonal    * b.vector_heuristique()
    if(stability!=0):   eval += stability   * b.stab_heuristique()
    if(front!=0):       eval += front       * b.circlefront_heuritisque()
    #eval += diagonal    * b.vector_heuristique()
    return eval

def evaluationV2(nbmove,b,tab_greed,tab_early,tab_mid,tab_late):
    if(nbmove<10):
        return evaluation(nbmove,b,tab_greed[0],tab_greed[1],tab_greed[2],tab_greed[3],tab_greed[4],tab_greed[5],tab_greed[6],tab_greed[7])
    elif(nbmove<30):
        return evaluation(nbmove,b,tab_early[0],tab_early[1],tab_early[2],tab_early[3],tab_early[4],tab_early[5],tab_early[6],tab_early[7])
    elif(nbmove<55):
        return evaluation(nbmove,b,tab_mid[0],tab_mid[1],tab_mid[2],tab_mid[3],tab_mid[4],tab_mid[5],tab_mid[6],tab_mid[7])
    else:
        return evaluation(nbmove,b,tab_late[0],tab_late[1],tab_late[2],tab_late[3],tab_late[4],tab_late[5],tab_late[6],tab_late[7])
#########################################SORTS#####################################################################
def GetSortedNodes(b,moves):
    global nbmove
    sortedNodes = []
    for move in moves:
        b.push(move)
        sortedNodes.append([move,evaluationV2(nbmove,b,tab_greed,tab_early,tab_mid,tab_late)])
        b.pop()
    sortedNodes = sorted(sortedNodes, key = lambda node: node[1], reverse = True)
    sortedNodes = [node[0] for node in sortedNodes]
    return sortedNodes
############################################NEGASCOUT###############################################################
#Not use anymore was slower :/
def NegascoutSN(b, player, depth, alpha, beta,mycolor,moves):
    if depth == 0 or b.is_game_over():
        return mycolor * evaluationV2(nbmove,b,tab_greed,tab_early,tab_mid,tab_late)
    #sortedNodes = GetSortedNodes(b,moves)
    firstChild = True
    for move in b.legal_moves():
        if not firstChild:
            b.push(move)
            new_moves = b.legal_moves()
            score = -NegascoutSN(b, player, depth - 1, -alpha - 1, -alpha, -mycolor,new_moves)
            if alpha < score and score < beta:
                score = -NegascoutSN(b, player, depth - 1, -beta, -score, -mycolor,new_moves)
            b.pop()
        else:
            firstChild = False
            b.push(move)
            score = -NegascoutSN(b, player, depth - 1, -beta, -alpha, -mycolor,b.legal_moves())
            b.pop()
        alpha = max(alpha, score)
        if alpha >= beta:
            return alpha
    return alpha

def Nega(b,player,depth,alpha,beta,mycolor,moves):

    valueMax,moveMax = MAX,(moves[0])
    for move in b.legal_moves():
        b.push(move)
        val = NegascoutSN(b, player, depth, alpha, beta, mycolor,b.legal_moves())
        print(val)
        if valueMax == MAX or val > valueMax:
            valueMax,moveMax = val,move
        b.pop()
    return moveMax

############################################NEGAMAX###############################################################

def NegaBeta(self,b,depths,moves):
    self._start = time.time()
    valueMax,moveMax = MAX,(moves[randint(0,len(moves)-1)])
    for depth in range(3,self._maxdepth):
        if(time.time()-self._start > self._maxtime) : break
        #sortedNodes = GetSortedNodes(b,moves)
        scores = []
        for move in b.legal_moves():
            b.push(move)
            beta = -valueMax if valueMax != MAX else MAX
            score = -NegaBetaM(self,b,depth,MIN,beta)
            scores.append((score,move))
            if valueMax == MAX or score > valueMax: valueMax , moveMax = (score,move)
            b.pop()
    return moveMax

def NegaBetaM(self,b,depth,alpha,beta):
    if b.is_game_over():
        return killer(self,b) * abs(evaluationV2(nbmove,b,tab_greed,tab_early,tab_mid,tab_late))
    if depth == 0  or time.time() - self._start > self._maxtime:
        return evaluationV2(nbmove,b,tab_greed,tab_early,tab_mid,tab_late)
    #sortedNodes = GetSortedNodes(b,b.legal_moves())
    for move in b.legal_moves():
        b.push(move)
        score = -NegaBetaM(self,b,depth-1,(MIN,-beta)[beta!=MAX],(MAX,-alpha)[alpha!=MIN])
        b.pop()
        if alpha == MIN or score > alpha : alpha = score
        if alpha >= beta and alpha != MIN and beta != MAX: return beta
    return alpha

##########################################KILLER MOVE###############################################################
def corner_killer(color,moves):
    if([color,0,0] in moves):
        return [color,0,0]
    elif([color,0,9] in moves):
        return [color,0,9]
    elif([color,9,0] in moves):
        return [color,9,0]
    elif([color,9,9] in moves):
        return [color,9,9]
    return None
def killer(self,b):
    (nbwhites, nbblacks) = b.get_nb_pieces()
    if(self._mycolor == b._BLACK): return nbblacks - nbwhites
    return nbwhites - nbblacks


####################################################################################################################
class myPlayer(PlayerInterface):

    def __init__(self):
        self._board = Reversi2.Board(10)
        self._mycolor = None
        self._start = 0
        self._maxtime = 5.8
        self._maxdepth = 99
    def getPlayerName(self):
        return "Alexisfoisdeux"

    def getPlayerMove(self):
        global nbmove
        if self._board.is_game_over():
            print("Referee told me to play but the game is over!")
            return (-1,-1)

        moves = [m for m in self._board.legal_moves()]
        move = corner_killer(self._mycolor,moves)
        coeff_mid = 0
        if(len(moves)<7): coeff_mid = 6
        else : coeff_mid = 3
        if  (len(moves)==0): return (-1,-1)
        elif(len(moves)==1): move = moves[0]
        elif(move is None):
	#Now depth aren't fix but that was usefull before iterative deepening
            if  (nbmove <  60):  move = NegaBeta(self,self._board,3,moves)
            elif(nbmove >= 60):  move = NegaBeta(self,self._board,coeff_mid,moves)
            elif(nbmove >= 80):  move = NegaBeta(self,self._board,20,moves)
        self._board.push(move)
        print("I am playing ", move)
        (c,x,y) = move
        assert(c==self._mycolor)
        print("My current board :")
        print(self._board)
        nbmove+=1
        return (x,y) 

    def playOpponentMove(self, x,y):
        global nbmove
        assert(self._board.is_valid_move(self._opponent, x, y))
        print("Opponent played ", (x,y))
        self._board.push([self._opponent, x, y])
        nbmove+=1

    def newGame(self, color):
        self._mycolor = color
        self._opponent = 1 if color == 2 else 2

    def endGame(self, winner):
        if self._mycolor == winner:
            print("I won!!!")
        else:
            print("I lost :(!!")



