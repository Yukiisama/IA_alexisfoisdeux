# -*- coding: utf-8 -*-

''' Fichier de règles du Reversi pour le tournoi Masters Info 2019 en IA.
    Certaines parties de ce code sont fortement inspirée de 
    https://inventwithpython.com/chapter15.html

    '''
import math
class Board:
    _BLACK = 1
    _WHITE = 2
    _EMPTY = 0

    # Attention, la taille du plateau est donnée en paramètre
    def __init__(self, boardsize = 8):
      self._nbWHITE = 2
      self._nbBLACK = 2
      self._nextPlayer = self._BLACK
      self._boardsize = boardsize
      self._board = []
      for x in range(self._boardsize):
          self._board.append([self._EMPTY]* self._boardsize)
      _middle = int(self._boardsize / 2)
      self._board[_middle-1][_middle-1] = self._BLACK 
      self._board[_middle-1][_middle] = self._WHITE
      self._board[_middle][_middle-1] = self._WHITE
      self._board[_middle][_middle] = self._BLACK 
      
      self._stack= []
      self._successivePass = 0

    def reset(self):
        self.__init__()

    # Donne la taille du plateau 
    def get_board_size(self):
        return self._boardsize

    # Donne le nombre de pieces de blanc et noir sur le plateau
    # sous forme de tuple (blancs, noirs) 
    # Peut être utilisé si le jeu est terminé pour déterminer le vainqueur
    def get_nb_pieces(self):
      return (self._nbWHITE, self._nbBLACK)

    # Vérifie si player a le droit de jouer en (x,y)
    def is_valid_move(self, player, x, y):
        if x == -1 and y == -1:
            return not self.at_least_one_legal_move(player)
        return self.lazyTest_ValidMove(player,x,y)

    def _isOnBoard(self,x,y):
        return x >= 0 and x < self._boardsize and y >= 0 and y < self._boardsize 

    # Renvoie la liste des pieces a retourner si le coup est valide
    # Sinon renvoie False
    # Ce code est très fortement inspiré de https://inventwithpython.com/chapter15.html
    # y faire référence dans tous les cas
    def testAndBuild_ValidMove(self, player, xstart, ystart):
        if self._board[xstart][ystart] != self._EMPTY or not self._isOnBoard(xstart, ystart):
            return False
    
        self._board[xstart][ystart] = player # On pourra remettre _EMPTY ensuite 
    
        otherPlayer = self._flip(player)
    
        tilesToFlip = [] # Si au moins un coup est valide, on collecte ici toutes les pieces a retourner
        for xdirection, ydirection in [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]]:
            x, y = xstart, ystart
            x += xdirection 
            y += ydirection
            if self._isOnBoard(x, y) and self._board[x][y] == otherPlayer:
                # There is a piece belonging to the other player next to our piece.
                x += xdirection
                y += ydirection
                if not self._isOnBoard(x, y):
                    continue
                while self._board[x][y] == otherPlayer:
                    x += xdirection
                    y += ydirection
                    if not self._isOnBoard(x, y): # break out of while loop, then continue in for loop
                        break
                if not self._isOnBoard(x, y):
                    continue
                if self._board[x][y] == player: # We are sure we can at least build this move. Let's collect
                    while True:
                        x -= xdirection
                        y -= ydirection
                        if x == xstart and y == ystart:
                            break
                        tilesToFlip.append([x, y])
    
        self._board[xstart][ystart] = self._EMPTY # restore the empty space
        if len(tilesToFlip) == 0: # If no tiles were flipped, this is not a valid move.
            return False
        return tilesToFlip

    # Pareil que ci-dessus mais ne revoie que vrai / faux (permet de tester plus rapidement)
    def lazyTest_ValidMove(self, player, xstart, ystart):
        if self._board[xstart][ystart] != self._EMPTY or not self._isOnBoard(xstart, ystart):
            return False
    
        self._board[xstart][ystart] = player # On pourra remettre _EMPTY ensuite 
    
        otherPlayer = self._flip(player)
    
        for xdirection, ydirection in [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]]:
            x, y = xstart, ystart
            x += xdirection 
            y += ydirection
            if self._isOnBoard(x, y) and self._board[x][y] == otherPlayer:
                # There is a piece belonging to the other player next to our piece.
                x += xdirection
                y += ydirection
                if not self._isOnBoard(x, y):
                    continue
                while self._board[x][y] == otherPlayer:
                    x += xdirection
                    y += ydirection
                    if not self._isOnBoard(x, y): # break out of while loop, then continue in for loop
                        break
                if not self._isOnBoard(x, y): # On a au moins 
                    continue
                if self._board[x][y] == player: # We are sure we can at least build this move. 
                    self._board[xstart][ystart] = self._EMPTY
                    return True
                 
        self._board[xstart][ystart] = self._EMPTY # restore the empty space
        return False

    def _flip(self, player):
        if player == self._BLACK:
            return self._WHITE 
        return self._BLACK

    def is_game_over(self):
        if self.at_least_one_legal_move(self._nextPlayer):
            return False
        if self.at_least_one_legal_move(self._flip(self._nextPlayer)):
            return False
        return True 

    def push(self, move):
        [player, x, y] = move
        assert player == self._nextPlayer
        if x==-1 and y==-1: # pass
            self._nextPlayer = self._flip(player)
            self._stack.append([move, self._successivePass, []])
            self._successivePass += 1
            return
        toflip = self.testAndBuild_ValidMove(player,x,y)
        self._stack.append([move, self._successivePass, toflip])
        self._successivePass = 0
        self._board[x][y] = player
        for xf,yf in toflip:
            self._board[xf][yf] = self._flip(self._board[xf][yf])
        if player == self._BLACK:
            self._nbBLACK += 1 + len(toflip)
            self._nbWHITE -= len(toflip)
            self._nextPlayer = self._WHITE
        else:
            self._nbWHITE += 1 + len(toflip)
            self._nbBLACK -= len(toflip)
            self._nextPlayer = self._BLACK

    def pop(self):
        [move, self._successivePass, toflip] = self._stack.pop()
        [player,x,y] = move
        self._nextPlayer = player 
        if len(toflip) == 0: # pass
            assert x == -1 and y == -1
            return
        self._board[x][y] = self._EMPTY
        for xf,yf in toflip:
            self._board[xf][yf] = self._flip(self._board[xf][yf])
        if player == self._BLACK:
            self._nbBLACK -= 1 + len(toflip)
            self._nbWHITE += len(toflip)
        else:
            self._nbWHITE -= 1 + len(toflip)
            self._nbBLACK += len(toflip)

    # Est-ce que on peut au moins jouer un coup ?
    # Note: cette info pourrait être codée plus efficacement
    def at_least_one_legal_move(self, player):
        for x in range(0,self._boardsize):
            for y in range(0,self._boardsize):
                if self.lazyTest_ValidMove(player, x, y):
                   return True
        return False

    # Renvoi la liste des coups possibles
    # Note: cette méthode pourrait être codée plus efficacement
    def legal_moves(self):
        moves = []
        for x in range(0,self._boardsize):
            for y in range(0,self._boardsize):
                if self.lazyTest_ValidMove(self._nextPlayer, x, y):
                    moves.append([self._nextPlayer,x,y])
        if len(moves) is 0:
            moves = [[self._nextPlayer, -1, -1]] # We shall pass
        return moves

    # Exemple d'heuristique tres simple : compte simplement les pieces
    def heuristique(self, player=None):
        if player is None:
            player = self._nextPlayer
        if player is self._WHITE:
            return self._nbWHITE - self._nbBLACK
        return self._nbBLACK - self._nbWHITE

  
    def nb_legalmoves(self,player):
        cpt = 0
        for x in range(0,self._boardsize):
            for y in range(0,self._boardsize):
                if self.lazyTest_ValidMove(player, x, y):
                    cpt+=1
        return cpt

    def stable_add(self,_list,stable_discs):
            for pts in _list:
                st = False
                for disc in stable_discs:
                    if(pts == disc):
                        st=True
                        break
                if not st: stable_discs.append(pts) 
            #print("LEN : ",len(stable_discs))
            return stable_discs
    

    def stable_size(self,i,j,player=None,opponent=None):
        stable_discs = []
        mi = 0
        mj = 0
        
        _list =[]
        mi = i - 1
        mj = j
        while(mi>0 and self._board[mi][mj] == player):
            _list.append((mi,mj))
            mi-=1
        for pts in _list:
                st = False
                for disc in stable_discs:
                    if(pts == disc):
                        st=True
                        break
                if not st: stable_discs.append(pts) 
        _list =[]
        mi = i + 1
        mj = j
        while(mi<9 and self._board[mi][mj] == opponent):
            _list.append((mi,mj))
            mi+=1
        stable_discs = self.stable_add(_list,stable_discs)
        
        _list =[]
        mi = i - 1
        mj = j - 1
        while(mj>0 and self._board[mi][mj] == opponent):
            _list.append((mi,mj))
            mj-=1
        stable_discs = self.stable_add(_list,stable_discs)
        
        _list =[]
        mi = i - 1
        mj = j + 1
        while(mj<9 and self._board[mi][mj] == opponent):
            _list.append((mi,mj))
            mj+=1
        stable_discs = self.stable_add(_list,stable_discs)
        
        _list =[]
        mi = i - 1
        mj = j - 1
        while(mi>0 and mj > 0 and self._board[mi][mj] == opponent):
            _list.append((mi,mj))
            mi-=1
            mj-=1
        stable_discs = self.stable_add(_list,stable_discs)
        
        _list =[]
        mi = i - 1
        mj = j + 1
        while(mi>0 and mj < 9 and self._board[mi][mj] == opponent):
            _list.append((mi,mj))
            mi-=1
            mj+=1
        stable_discs = self.stable_add(_list,stable_discs)
        
        _list =[]
        mi = i + 1
        mj = j - 1
        while(mi<9 and mj > 0 and self._board[mi][mj] == opponent):
            _list.append((mi,mj))
            mi+=1
            mj-=1
        stable_discs = self.stable_add(_list,stable_discs)
        
        _list =[]
        mi = i + 1
        mj = j + 1
        
        while(mi<9 and mj < 9 and self._board[mi][mj] == opponent):
            _list.append((mi,mj))
            mi+=1
            mj+=1
        stable_discs = self.stable_add(_list,stable_discs)
        return len(stable_discs)
    
    def stab_heuristique(self,player = None):
        if player is None:
            player = self._nextPlayer
        opponent = self._BLACK if player is self._WHITE else self._WHITE
        score_ally   = 0
        score_opp    = 0
        if self._board[0][0]==player:   score_ally += self.stable_size(0,0,player,opponent)
        if self._board[0][9]==player:   score_ally += self.stable_size(0,9,player,opponent)
        if self._board[9][0]==player:   score_ally += self.stable_size(9,0,player,opponent)
        if self._board[9][9]==player:   score_ally += self.stable_size(9,9,player,opponent)
        if self._board[0][0]==opponent: score_opp  += self.stable_size(0,0,opponent,player)
        if self._board[0][9]==opponent: score_opp  += self.stable_size(0,9,opponent,player)
        if self._board[9][0]==opponent: score_opp  += self.stable_size(9,0,opponent,player)
        if self._board[9][9]==opponent: score_opp  += self.stable_size(9,9,opponent,player)
        
        return 100 * (score_ally - score_opp)/(score_ally+score_opp+1)
    
    def circle(self,player):
        front_valid = []
        opponent = self._BLACK if player is self._WHITE else self._WHITE
        for i in range(10):
            for j in range(10):
                if self._board[i][j]==opponent:
                    front = []
                    if (i>0 and self._board[i-1][j])==0: front.append((i-1,j))
                    if (i<9 and self._board[i+1][j])==0: front.append((i+1,j))
                    if (j<9 and self._board[i][j+1])==0: front.append((i,j+1))
                    if (j>0 and self._board[i][j-1])==0: front.append((i,j-1))
                    if (i>0 and j>0 and self._board[i-1][j-1])==0 : front.append((i-1,j-1))
                    if (i>0 and j<9 and self._board[i-1][j+1])==0 : front.append((i-1,j+1))
                    if (i<9 and j>0 and self._board[i+1][j-1])==0 : front.append((i+1,j-1))
                    if (i<9 and j<9 and self._board[i+1][j+1])==0 : front.append((i+1,j+1))
                    front_valid = self.stable_add(front,front_valid)
        return len(front_valid)
    def circlefront_heuritisque(self,player=None):
        if player is None:
            player = self._nextPlayer
        opponent = self._BLACK if player is self._WHITE else self._WHITE
        score_ally   = self.circle(player)
        score_opp    = self.circle(opponent)
        return 100 * (score_ally - score_opp)/(score_ally+score_opp+1)
    
    def piecediff_heuristique(self,player=None):
        if player is None:
            player = self._nextPlayer
        if (player is self._WHITE and self._nbWHITE >= self._nbBLACK ):
            return (100 * self._nbWHITE) / (self._nbWHITE + self._nbBLACK)
        elif(player is self._WHITE and self._nbWHITE < self._nbBLACK ):
            return -(100 * self._nbBLACK) / (self._nbWHITE + self._nbBLACK)
        elif (player is self._BLACK and self._nbBLACK > self._nbWHITE):
            return (100 * self._nbBLACK) / (self._nbWHITE + self._nbBLACK)
        elif(player is self._BLACK and self._nbBLACK < self._nbWHITE):
            return -(100 * self._nbWHITE) / (self._nbWHITE + self._nbBLACK)
        else:
            return 0
    # ajout moi
    def mobility_heuristique(self,player=None):
        white_mov = self.nb_legalmoves(self._WHITE)
        black_mov = self.nb_legalmoves(self._BLACK)
        if player is None:
            player = self._nextPlayer
        if (player is self._WHITE and white_mov > black_mov):
            return (100 * white_mov) / (white_mov + black_mov)
        elif(player is self._WHITE and white_mov < black_mov ):
            return -(100 * black_mov) / (white_mov + black_mov)
        elif (player is self._BLACK and black_mov > white_mov):
            return (100 * black_mov) / (white_mov + black_mov)
        elif(player is self._BLACK and black_mov < white_mov ):
            return -(100 * white_mov) / (white_mov + black_mov)
        else:
            return 0
    def corners_heuristique(self,player=None):
        cpt_ally = 0
        cpt_ennemi = 0
        opponent = 0
        if player is None:
            player = self._nextPlayer
        opponent = self._BLACK if player is self._WHITE else self._WHITE
        if self._board[0][0]==player:
            cpt_ally+=1
        elif self._board[0][0]==opponent:
            cpt_ennemi+=1
        if self._board[9][0]==player:
            cpt_ally+=1
        elif self._board[9][0]==opponent:
            cpt_ennemi+=1
        if self._board[0][9]==player:
            cpt_ally+=1
        elif self._board[0][9]==opponent:
            cpt_ennemi+=1
        if self._board[9][9]==player:
            cpt_ally+=1
        elif self._board[9][9]==opponent:
            cpt_ennemi+=1
        return 25 * (cpt_ally - cpt_ennemi) # 100 / 4 corners
    

    def layers_heuristique(self,player=None):
        cpt = 0
        opponent = 0
        if player is None:
            player = self._nextPlayer
        opponent = self._BLACK if player is self._WHITE else self._WHITE
        for i in range(10):
            cpt += 1 if self._board[0][i]==player else -1
            if self._board[0][i]==player: cpt -= 1
            cpt += 1 if self._board[i][0]==player else -1
            if self._board[i][0]==player: cpt -= 1
            cpt += 1 if self._board[9][i]==player else -1
            if self._board[9][i]==player: cpt -= 1
            cpt += 1 if self._board[i][9]==player else -1
            if self._board[i][9]==player: cpt -= 1

        for i in range(1, 8):
            cpt += -1 if self._board[1][i]==player else 1
            if self._board[1][i]==player: cpt += 1
            cpt += -1 if self._board[i][1]==player else 1
            if self._board[i][1]==player: cpt += 1
            cpt += -1 if self._board[8][i]==player else 1
            if self._board[8][i]==player: cpt += 1
            cpt += -1 if self._board[i][8]==player else 1
            if self._board[i][8]==player: cpt += 1

        return cpt

    def diagonal_heuristique(self,player = None):
        cpt = 0
        if player is None:
            player = self._nextPlayer
        opponent = self._BLACK if player is self._WHITE else self._WHITE

        i = 0
        while (i < 10 and self._board[i][i] != opponent):
            i += 1
        if (i == 10):
            cpt += 100

        i = 0
        while (i < 10 and self._board[i][9-i] != opponent):
            i += 1
        if (i == 10):
            cpt += 100

        i = 0
        while (i < 10 and self._board[i][i] != player):
            i += 1
        if (i == 10):
            cpt -= 100

        i = 0
        while (i < 10 and self._board[i][9-i] != player):
            i += 1
        if (i == 10):
            cpt -= 100

        return cpt
            
    


    def CornerClose_heuristique(self,player = None):
        cpt_ally = 0
        cpt_ennemi = 0
        opponent = 0
        if player is None:
            player = self._nextPlayer
        opponent = self._BLACK if player is self._WHITE else self._WHITE

        if self._board[0][0]==self._EMPTY:
            if self._board[0][1]==player:
                cpt_ally+=1
            elif self._board[0][1]==opponent:
                cpt_ennemi+=1
            if self._board[1][0]==player:
                cpt_ally+=1
            elif self._board[1][0]==opponent:
                cpt_ennemi+=1
            if self._board[1][1]==player:
                cpt_ally+=1
            elif self._board[1][1]==opponent:
                cpt_ennemi+=1
        if self._board[0][9]==self._EMPTY:
            if self._board[0][8]==player:
                cpt_ally+=1
            elif self._board[0][8]==opponent:
                cpt_ennemi+=1
            if self._board[1][8]==player:
                cpt_ally+=1
            elif self._board[1][8]==opponent:
                cpt_ennemi+=1
            if self._board[1][9]==player:
                cpt_ally+=1
            elif self._board[1][9]==opponent:
                cpt_ennemi+=1
        if self._board[9][0]==self._EMPTY:
            if self._board[8][0]==player:
                cpt_ally+=1
            elif self._board[8][0]==opponent:
                cpt_ennemi+=1
            if self._board[8][1]==player:
                cpt_ally+=1
            elif self._board[8][1]==opponent:
                cpt_ennemi+=1
            if self._board[9][1]==player:
                cpt_ally+=1
            elif self._board[9][1]==opponent:
                cpt_ennemi+=1
        if self._board[9][9]==self._EMPTY:
            if self._board[8][9]==player:
                cpt_ally+=1
            elif self._board[8][9]==opponent:
                cpt_ennemi+=1
            if self._board[8][8]==player:
                cpt_ally+=1
            elif self._board[8][8]==opponent:
                cpt_ennemi+=1
            if self._board[9][8]==player:
                cpt_ally+=1
            elif self._board[9][8]==opponent:
                cpt_ennemi+=1
        return -12.5 * (cpt_ally - cpt_ennemi) # 100 / 8 


    def stability_heuristique(self,player = None):
        if player is None:
            player = self._nextPlayer
        opponent = self._BLACK if player is self._WHITE else self._WHITE

    def static_layers_heuristique(self,player = None):
        if player is None:
            player = self._nextPlayer
        opponent = self._BLACK if player is self._WHITE else self._WHITE
        W = [
        [200 , -100, 100 , 100,  50,  50, 100,100 , -100,  200],
        [-100, -200,100  , -50, -50, -50, -50, 100,-200 , -100],
        [100 ,  100, 100 ,  50,   25,   25, 50 , 100,  100,  100],
        [50  ,  -50, 25   ,  50,   15,   15, 50 , 25  ,  -50,   50],
        [50  ,  -50, 15   ,   15,  50,  50,  25 , 15 ,  -50,   50],
        [50  ,  -50, 15   ,   15,  50,  50,  25 , 15  ,  -50,   50],
        [50  ,  -50, 25  ,  50,   15,   25, 50 , 25  ,  -50,   50],
        [100 ,  100, 100 , 50 ,   25,   25, 50 , 100,  100,  100],
        [-100, -200, 100 , -50, -50, -50, -50, 100,-200 , -100],
        [200 , -100, 100 , 100,  50,  50, 100,100 , -100,  200]]


        # if(self._board[0][0] != 0):
        #     for i in range(3) :
        #         for j in range(3):
        #             W[i][j] = 0

        # if(self._board[0][9] != 0):
        #     for i in range(3) :
        #         for j in range(7,10) :
        #             W[i][j] = 0

        # if(self._board[9][0] != 0):
        #     for i in range(7,10) :
        #         for j in range(3) :
        #             W[i][j] = 0

        # if(self._board[9][9] != 0):
        #     for i in range(7,10) :
        #         for j in range(7,10) :
        #             W[i][j] = 0 
                
        ally = 0
        ennemi = 0

        for i in range(10) :
            for j in range(10) :
                if(self._board[i][j]==player):   ally += W[i][j]
                if(self._board[i][j]==opponent): ennemi += W[i][j]
        if(ally+ennemi == 0):
            return (ally)
        else:
            return ((ally)) 
    
    def vector_heuristique(self, player=None):
        cpt = 0
        opponent = 0
        if player is None:
            player = self._nextPlayer
        opponent = self._BLACK if player is self._WHITE else self._WHITE
        empty = 0

        vectors_type = []
        vectors = []
        for i in range(60):
            vectors.append([])

        for i in range(10):
            for j in range(10):
                vectors[i].append(self._board[i][j])

        for j in range(10):
            for i in range(10):
                vectors[i+10].append(self._board[i][j])

        for i in range(10):
            for j in range(i+1):
                vectors[i+20].append(self._board[i-j][j])
                vectors[i+30].append(self._board[9-(i-j)][9-j])

        for i in range(10):
            for j in range(9-i):
                vectors[i+40].append(self._board[i+j][j])
                vectors[i+50].append(self._board[j][i+j])

        for vector in vectors:

            if empty in vector and not opponent in vector and not player in vector:
                vectors_type.append("empty")
            elif opponent in vector and not empty in vector and not player in vector:
                vectors_type.append("opponent")
            elif player in vector and not opponent in vector and not empty in vector:
                vectors_type.append("player")
            
            for i in range(len(vector)):
                vector_type = ""
                for kind in [[player, "player"], [opponent, "opponent"], [empty, "empty"]]:
                    if vector[i] == kind[0] and vector_type.split('_')[-1] != kind[1]:
                        if vector_type == "":
                            vector_type += kind[1]
                        elif vector_type.split('').count('_') < 2:
                            vector_type += "_"+kind[1]
                        else:
                            vectors_type.append("invalid")
                            break
                vectors_type.append(vector_type)

        i = -1
        for vector_type in vectors_type:
            i += 1
            value = 0
            if vector_type == "player":
                value = 10
            elif vector_type == "opponent":
                value = -10
            vector_type = vector_type.split('_')
            vector_type_reverse = vector_type.reverse()
            if (len(vector_type) == 2):
                if (vector_type[0] == "empty" and vector_type[1] == "opponent") or (vector_type_reverse[0] == "empty" and vector_type_reverse[1] == "opponent"):
                    value = -5
                elif (vector_type[0] == "empty" and vector_type[1] == "player") or (vector_type_reverse[0] == "empty" and vector_type_reverse[1] == "player"):
                    value = 5
            elif (len(vector_type) == 3):
                if (vector_type[0] == "player" and vector_type[1] == "opponent" and vector_type[2] == "empty") or (vector_type_reverse[0] == "player" and vector_type_reverse[1] == "opponent" and vector_type_reverse[2] == "empty"):
                    nb_empty = 0
                    for el in vectors[i]:
                        if el == empty:
                            nb_empty += 1
                    if (nb_empty % 2) == 0:
                        value = -5
                    else:
                        value = 5
                if (vector_type[0] == "opponent" and vector_type[1] == "player" and vector_type[2] == "empty") or (vector_type_reverse[0] == "opponent" and vector_type_reverse[1] == "player" and vector_type_reverse[2] == "empty"):
                    nb_empty = 0
                    for el in vectors[i]:
                        if el == empty:
                            nb_empty += 1
                    if (nb_empty % 2) == 0:
                        value = 5
                    else:
                        value = -5
                if (vector_type[0] == "empty" and vector_type[1] == "player" and vector_type[2] == "empty") or (vector_type_reverse[0] == "empty" and vector_type_reverse[1] == "player" and vector_type_reverse[2] == "empty"):
                        value = 5
                if (vector_type[0] == "empty" and vector_type[1] == "opponent" and vector_type[2] == "empty") or (vector_type_reverse[0] == "empty" and vector_type_reverse[1] == "opponent" and vector_type_reverse[2] == "empty"):
                        value = -5

                
            
            dist = max((i%10)%9, (9-(i%10))%9) 
            value *= 1 / (1+dist)
            cpt += value

        return cpt








    def _piece2str(self, c):
        if c==self._WHITE:
            return 'O'
        elif c==self._BLACK:
            return 'X'
        else:
            return '.'

    def __str__(self):
        toreturn=""
        for l in self._board:
            for c in l:
                toreturn += self._piece2str(c)
            toreturn += "\n"
        toreturn += "Next player: " + ("BLACK" if self._nextPlayer == self._BLACK else "WHITE") + "\n"
        toreturn += str(self._nbBLACK) + " blacks and " + str(self._nbWHITE) + " whites on board\n"
        toreturn += "(successive pass: " + str(self._successivePass) + " )"
        return toreturn

    __repr__ = __str__


