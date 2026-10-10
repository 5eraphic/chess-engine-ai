
import random

pieceScore = {'K': 0, 'Q': 10, 'R': 5, 'B': 3, 'N': 3, 'p': 1}

knightScores = [[1, 1, 1, 1, 1, 1, 1, 1],
                [1, 2, 2, 2, 2, 2, 2, 1],
                [1, 2, 3, 3, 3, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 3, 3, 3, 2, 1],
                [1, 2, 2, 2, 2, 2, 2, 1],
                [1, 1, 1, 1, 1, 1, 1, 1]]

bishopScores = [[4, 3, 2, 1, 1, 2, 3, 4],
                [3, 4, 3, 2, 2, 3, 4, 3],
                [2, 3, 4, 3, 3, 4, 3, 2],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [2, 3, 4, 3, 3, 4, 3, 2],
                [3, 4, 3, 2, 2, 3, 4, 3],
                [4, 3, 2, 1, 1, 2, 3, 4]]

rookScores = [[4, 3, 4, 4, 4, 4, 3, 4],
              [4, 4, 4, 4, 4, 4, 4, 4],
              [1, 1, 2, 3, 3, 2, 1, 1],
              [1, 2, 3, 4, 4, 3, 2, 1],
              [1, 2, 3, 4, 4, 3, 2, 1],
              [1, 1, 2, 3, 3, 2, 1, 1],
              [4, 4, 4, 4, 4, 4, 4, 4],
              [4, 3, 4, 4, 4, 4, 3, 4]]

queenScores = [[1, 1, 1, 3, 1, 1, 1, 1],
               [1, 2, 3, 3, 3, 2, 1, 1],
               [1, 4, 3, 3, 3, 4, 2, 1],
               [1, 2, 3, 3, 3, 2, 2, 1],
               [1, 2, 3, 3, 3, 2, 2, 1],
               [1, 4, 3, 3, 3, 4, 2, 1],
               [1, 2, 3, 3, 3, 2, 1, 1],
               [1, 1, 1, 3, 1, 1, 1, 1]]

whitePawnScores = [[8, 8, 8, 8, 8, 8, 8, 8],
                   [8, 8, 8, 8, 8, 8, 8, 8],
                   [5, 6, 6, 7, 7, 6, 6, 5],
                   [2, 3, 3, 5, 5, 3, 3, 2],
                   [1, 2, 3, 4, 4, 3, 2, 1],
                   [1, 1, 2, 3, 3, 2, 1, 1],
                   [1, 1, 1, 0, 0, 1, 1, 1],
                   [0, 0, 0, 0, 0, 0, 0, 0]]

blackPawnScores = [[0, 0, 0, 0, 0, 0, 0, 0],
                   [1, 1, 1, 0, 0, 1, 1, 1],
                   [1, 1, 2, 3, 3, 2, 1, 1],
                   [1, 2, 3, 4, 4, 3, 2, 1],
                   [2, 3, 3, 5, 5, 3, 3, 2],
                   [5, 6, 6, 7, 7, 6, 6, 5],
                   [8, 8, 8, 8, 8, 8, 8, 8],
                   [8, 8, 8, 8, 8, 8, 8, 8]]

piecePositionScores = {"N": knightScores, "B": bishopScores, "R": rookScores,
                       "Q": queenScores, "wp": whitePawnScores, "bp": blackPawnScores}

CHECKMATE = 1000
STALEMATE = 0
DEPTH = 3


def findRandomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves)-1)]

def findBestMoveMinMaxNoRecursion(gs, validMoves):
    turnMultiplier = 1 if gs.whiteToMove else -1
    opponentMinMaxScore = CHECKMATE
    bestPlayerMove = validMoves[0]
    random.shuffle(validMoves)
    for playerMove in validMoves:
        gs.makeMove(playerMove)
        opponentsMoves = gs.getValidMoves()
        if gs.staleMate:
            opponentMaxScore = STALEMATE
        elif gs.checkMate:
            opponentMaxScore = -CHECKMATE
        else:
            opponentMaxScore = -CHECKMATE
            for opponentsMove in opponentsMoves:
                gs.makeMove(opponentsMove)
                gs.getValidMoves()
                if gs.checkMate:
                    score = CHECKMATE
                elif gs.staleMate:
                    score = STALEMATE
                else:
                    score = -turnMultiplier * scoreMaterial(gs.board)
                if score > opponentMaxScore:
                   opponentMaxScore = score
                gs.undoMove()
        if opponentMaxScore < opponentMinMaxScore:
            opponentMinMaxScore = opponentMaxScore
            bestPlayerMove = playerMove
        gs.undoMove()
    return bestPlayerMove

def findBestMove(gs, validMoves):
    global nextMove, counter
    counter = 0
    # Instead of calling AlphaBeta directly, use your iterative deepening loop
    nextMove = getBestMoveIterativeDeepening(gs, DEPTH)
    print("Nodes searched:", counter)
    return nextMove

def orderMoves(validMoves, bestMove=None):
    # Piece values for MVV-LVA
    PIECE_VALUES = {'Q': 90, 'R': 50, 'B': 30, 'N': 30, 'p': 10}

    def getMoveScore(move):
        score = 0
        if move == bestMove: return 100000
        if move.isCapture:
            victim = PIECE_VALUES.get(move.pieceCaptured[1], 0)
            aggressor = PIECE_VALUES.get(move.pieceMoved[1], 0)
            score += 1000 + (victim * 10) - aggressor
        if move.isCheck: score += 500
        if move.castle: score += 400
        if move.pawnPromotion: score += 300
        if move.pieceMoved[1] == 'p' and not move.isCapture:
            score -= 50
        return score

    # IMPORTANT: Actually sort the list in-place!
    validMoves.sort(key=getMoveScore, reverse=True)

# In your main game loop (where you trigger the AI turn):
def getBestMoveIterativeDeepening(gs, max_depth):
    global nextMove
    bestMove = None
    nextMove = None
    for current_depth in range(1, max_depth + 1):
        findMoveNegaMaxAlphaBeta(gs, gs.getValidMoves(), current_depth, -CHECKMATE, CHECKMATE,
                                 1 if gs.whiteToMove else -1, bestMove)
        if nextMove is not None:
            bestMove = nextMove
    return bestMove

def findMoveMinMax(gs, validMoves, depth, whiteToMove):
    global nextMove
    if depth == 0:
        return scoreMaterial(gs.board)
    if whiteToMove:
        maxScore = -CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = findMoveMinMax(gs, nextMoves, depth - 1, False)
            if score > maxScore:
                maxScore = score
                if depth == DEPTH:
                    nextMove = move
            gs.undoMove()
        return maxScore
    else:
        minScore = CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = findMoveMinMax(gs, nextMoves, depth - 1, True)
            if score < minScore:
                minScore = score
                if depth == DEPTH:
                    nextMove = move
            gs.undoMove()
        return minScore

def findMoveNegaMax(gs, validMoves, depth, turnMultiplier):
    global nextMove, counter
    counter += 1
    if depth == 0:
        return turnMultiplier * scoreboard(gs)
    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = -findMoveNegaMax(gs, nextMoves, depth - 1, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
        gs.undoMove()
    return maxScore

def findMoveNegaMaxAlphaBeta(gs, validMoves, depth, alpha, beta, turnMultiplier, bestMove=None, original_depth = None):
    global nextMove, counter
    if original_depth is None:
        original_depth = depth
    counter += 1
    if depth == 0:
        return turnMultiplier * scoreboard(gs)
    # 1. Order moves once at this node
    if len(validMoves) > 1:
        orderMoves(validMoves, bestMove)
    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move)
        if gs.checkForPinsAndChecks()[0]:
            move.isCheck = True
        else:
            move.isCheck = False
        nextMoves = gs.getValidMoves()
        score = -findMoveNegaMaxAlphaBeta(gs, nextMoves, depth - 1, -beta, -alpha, -turnMultiplier, None, original_depth)
        gs.undoMove()
        if score > maxScore:
            maxScore = score
            if depth == original_depth:
                nextMove = move
        elif score == maxScore and depth == original_depth:
            if random.random() < 0.3:  # 30% chance to pick this move instead
                nextMove = move
        if maxScore > alpha:
            alpha = maxScore
        if alpha >= beta:
            break
    return maxScore

'''change smartness of ai by multiplying the piecepostionScore by a weight
 0.1   # Mostly material
 0.2   # Good balance (recommended)
 0.3   # More positional
 0.5   # Strong positional influence'''
def scoreboard(gs):
    if gs.checkMate:
        if gs.whiteToMove:
            return -CHECKMATE
        else:
            return CHECKMATE
    elif gs.staleMate:
        return STALEMATE
    score = 0
    for row in range(len(gs.board)):
        for col in range(len(gs.board[row])):
            square = gs.board[row][col]
            if square != "--":
                piecePositionScore = 0
                if square[1] != "K":
                    if square[1] == "p":
                        piecePositionScore = piecePositionScores[square][row][col]
                    else:
                        piecePositionScore = piecePositionScores[square[1]][row][col]
                if square[0] == 'w':
                    score += pieceScore[square[1]] + piecePositionScore * 0.4
                elif square[0] == 'b':
                    score -= pieceScore[square[1]] + piecePositionScore * 0.4
    return score

def scoreMaterial(board):
    score = 0
    for row in board:
        for square in row:
            if square[0] == 'w':
                score += pieceScore[square[1]]
            elif square[0] == 'b':
                score -= pieceScore[square[1]]
    return score
