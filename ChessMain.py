
import os
import random
import sys
import pygame as p
from Chess import ChessEngine, Chessai

WIDTH = HEIGHT = 512
LOG_WIDTH = 256 # --- ADDED: Extra width for the side panel ---
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def loadImages():
    pieces = ['bB', 'bK', 'bN', 'bp', 'bQ', 'bR', 'wp', 'wQ', 'wR', 'wN', 'wK', 'wB']
    for piece in pieces:
        image_filepath = resource_path("images/" + piece + ".png")
        IMAGES[piece] = p.transform.scale(p.image.load(image_filepath), (SQ_SIZE, SQ_SIZE))

'''change color of buttons and the hover highlight here'''
class Button():
    def __init__(self, x, y, width, height, text):
        self.rect = p.Rect(x, y, width, height)
        self.text = text

    def draw(self, screen):
        if self.rect.collidepoint(p.mouse.get_pos()):
            color = p.Color("#DAD4D0")
        else:
            color = p.Color("#828F91")
        p.draw.rect(screen, color, self.rect)
        p.draw.rect(screen, p.Color("black"), self.rect, 2)
        textObject = font.render(self.text, True, p.Color("black"))
        textRect = textObject.get_rect(center=self.rect.center)
        screen.blit(textObject, textRect)

    def clicked(self, position):
        return self.rect.collidepoint(position)

def controlsMenu(screen, moveLogFont):
    TOTAL_WIDTH = WIDTH + LOG_WIDTH

    while True:
        screen.fill(p.Color("#A8BAC0"))
        title = font.render("Controls", True, p.Color("black"))
        titleRect = title.get_rect(center=(TOTAL_WIDTH // 2, 60))
        screen.blit(title, titleRect)
        controls = [
            "Click a piece - Select piece",
            "Click a square - Move piece",
            "",
            "Z - Undo move permanently",
            "Left Arrow - Step backward",
            "Right Arrow - Step forward",
            "R - Restart game",
            "F - Flip board",
            "",
            "Click promotion piece when prompted",
            "",
            "Press ESC to return"]
        y = 120
        for line in controls:
            text = moveLogFont.render(line, True, p.Color("black"))
            # This perfectly centers every single line horizontally
            textRect = text.get_rect(center=(TOTAL_WIDTH // 2, y))
            screen.blit(text, textRect)
            y += 30
        p.display.flip()
        for e in p.event.get():
            if e.type == p.QUIT:
                p.quit()
                quit()
            if e.type == p.KEYDOWN:
                if e.key == p.K_ESCAPE:
                    return

'''change color of menu background color here'''
def choosePlayers(screen, moveLogFont):
    TOTAL_WIDTH = WIDTH + LOG_WIDTH
    centerX = (TOTAL_WIDTH // 2) - 150

    humanHuman = Button(centerX, 150, 300, 60, "Human vs Human")
    humanAI = Button(centerX, 240, 300, 60, "Human vs AI")
    controls = Button(centerX, 390, 300, 60, "Controls")

    while True:
        screen.fill(p.Color("#A8BAC0"))
        title = font.render("Subomi's Chess Engine and Chess AI", True, p.Color("black"))
        titleRect = title.get_rect(center=(TOTAL_WIDTH // 2, 60))
        subtitle = moveLogFont.render("Gifted to Bridge House College", True, p.Color("black"))
        subtitleRect = subtitle.get_rect(center=(TOTAL_WIDTH // 2, 90))
        screen.blit(subtitle, subtitleRect)
        screen.blit(title, titleRect)
        humanHuman.draw(screen)
        humanAI.draw(screen)
        controls.draw(screen)
        p.display.flip()
        for e in p.event.get():
            if e.type == p.QUIT:
                p.quit()
                quit()
            if e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()
                if humanHuman.clicked(location):
                    return True, True
                if humanAI.clicked(location):
                    return True, False
                if controls.clicked(location):
                    controlsMenu(screen, moveLogFont)

def main():
    p.init()
    p.display.set_icon(p.image.load(resource_path("icon.ico")))
    screen = p.display.set_mode((WIDTH + LOG_WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    animate = False

    global font
    font = p.font.SysFont("Helvetica", 32, True, False)
    moveLogFont = p.font.SysFont("Arial", 15, False, False)

    validMoves = gs.getValidMoves()
    moveMade = False
    redoStack = []

    loadImages()
    running = True
    sqSelected = ()
    playerClicks = []
    gameOver = False
    flipped = False
    playerOne, playerTwo = choosePlayers(screen, moveLogFont) #true if a human playing false if ai playing, ai plays black, player two
    if playerOne and not playerTwo:  # Human vs AI
        humanIsWhite = random.choice([True, False])
        if humanIsWhite:
            playerOne = True
            playerTwo = False
            flipped = False
        else:
            playerOne = False
            playerTwo = True
            flipped = True

    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
                    location = p.mouse.get_pos()
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if col < DIMENSION and row < DIMENSION:
                        if flipped:
                            row = 7 - row
                            col = 7 - col
                        if sqSelected == (row,col):
                            sqSelected = ()
                            playerClicks =[]
                        else:
                            sqSelected = (row, col)
                            playerClicks.append(sqSelected)
                        if len(playerClicks) == 2:
                            move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                            for validMove in validMoves:
                                if move == validMove:
                                    if validMove.pawnPromotion:
                                        color = 'w' if gs.whiteToMove else 'b'
                                        choice = drawPromotionUI(screen, color)
                                        validMove.promotionChoice = choice
                                    gs.makeMove(validMove)
                                    redoStack.clear()
                                    print(f"Move played: {validMove.getChessNotation()}")
                                    moveMade = True
                                    animate = True
                                    sqSelected = ()
                                    playerClicks = []
                                    break
                            if not moveMade:
                                playerClicks = [sqSelected]

            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    if len(gs.moveLog) > 0:
                        gs.undoMove()
                    moveMade = True
                    animate = False
                    gameOver = False
                    redoStack.clear()
                    redoStack.clear()
                    # --- Left arrow to step back one move at a time ---
                elif e.key == p.K_LEFT:
                    if len(gs.moveLog) > 0:
                        undoneMove = gs.moveLog[-1]
                        gs.undoMove()
                        redoStack.append(undoneMove)
                        moveMade = True
                        animate = False
                        gameOver = False
                    # --- Right arrow to step forward one move at a time ---
                elif e.key == p.K_RIGHT:
                    if len(redoStack) > 0:
                        moveToRedo = redoStack.pop()
                        gs.makeMove(moveToRedo)
                        moveMade = True
                        animate = False
                elif e.key == p.K_r:
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False
                    redoStack.clear()
                elif e.key == p.K_f:
                    flipped = not flipped

        if not gameOver and not humanTurn and len(redoStack) == 0 and not moveMade:
            AIMove = Chessai.findBestMove(gs, validMoves)
            if AIMove is None:
                AIMove = Chessai.findRandomMove(validMoves)
            gs.makeMove(AIMove)
            moveMade = True
            animate = True

        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock, flipped)
            validMoves = gs.getValidMoves()
            if len(gs.moveLog) != 0:
                lastMove = gs.moveLog[-1]

            lastMove.isCheck = gs.inCheck
            lastMove.isCheckMate = gs.checkMate
            moveMade = False
            animate = False
        drawGameState(screen, gs, validMoves, sqSelected, moveLogFont, flipped)

        if gs.checkMate:
            gameOver = True
            if gs.whiteToMove:
                drawText(screen, 'Black wins by checkmate')
            else:
                drawText(screen, 'White wins by checkmate')
        elif gs.staleMate:
            gameOver = True

            if gs.halfmoveClock >= 100:
                drawText(screen, 'Draw by 50 move rule')

            elif gs.positionLog.count(gs.getPosition()) >= 3:
                drawText(screen, 'Draw by repetition')

            else:
                drawText(screen, 'Stalemate')

        clock.tick(MAX_FPS)
        p.display.flip()

'''change move highlighting here with s.fill'''
def highlightSquares(screen, gs, validMoves,sqSelected, flipped):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(p.Color('orange'))
            drawRow = 7 - r if flipped else r
            drawCol = 7 - c if flipped else c

            screen.blit(s, (drawCol * SQ_SIZE, drawRow * SQ_SIZE))
            s.fill(p.Color('tan'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    endRow = 7 - move.endRow if flipped else move.endRow
                    endCol = 7 - move.endCol if flipped else move.endCol

                    screen.blit(s, (endCol * SQ_SIZE, endRow * SQ_SIZE))

def drawGameState(screen, gs, validMoves, sqSelected, moveLogFont, flipped):
    drawBoard(screen, flipped)
    highlightSquares(screen, gs, validMoves, sqSelected, flipped)
    drawPieces(screen, gs.board, flipped)
    drawMoveLog(screen, gs, moveLogFont)

'''change colors for board here with p.color'''
def drawBoard(screen, flipped):
    global colors
    colors = [p.Color("light blue"), p.Color("white")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            drawRow = 7 - r if flipped else r
            drawCol = 7 - c if flipped else c
            color = colors[((drawRow + drawCol) % 2)]
            p.draw.rect(screen, color, p.Rect(drawCol * SQ_SIZE, drawRow * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def drawPieces(screen, board, flipped):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                drawRow = 7 - r if flipped else r
                drawCol = 7 - c if flipped else c
                screen.blit(IMAGES[piece],
                            p.Rect(drawCol*SQ_SIZE,
                                   drawRow*SQ_SIZE,
                                   SQ_SIZE,
                                   SQ_SIZE))

'''change the color of the movelog with p.draw.rect and color of font of movelog using textobject'''
def drawMoveLog(screen, gs, moveLogFont):
    logRect = p.Rect(WIDTH, 0, LOG_WIDTH, HEIGHT)
    p.draw.rect(screen, p.Color('#636567'), logRect)
    moveLog = gs.moveLog
    moveTexts = []
    for i in range(0, len(moveLog), 2):
        moveString = f"{i // 2 + 1}. {moveLog[i]} "
        if i + 1 < len(moveLog):
            moveString += f"{moveLog[i + 1]}"
        moveTexts.append(moveString)
    movesPerRow = 3
    padding = 15
    textY = padding
    lineSpacing = 5
    for i in range(0, len(moveTexts), movesPerRow):
        text = ""
        for j in range(movesPerRow):
            if i + j < len(moveTexts):
                text += moveTexts[i + j] + "   "
        textObject = moveLogFont.render(text, 0, p.Color('white'))
        textLocation = logRect.move(padding, textY)
        screen.blit(textObject, textLocation)
        textY += textObject.get_height() + lineSpacing

'''change the animation speed here using framespersquare, decrease the number, faster animation'''
def animateMove(move, screen, board, clock, flipped):
    global colors
    coords = []
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 7
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(frameCount + 1):
        r, c = (move.startRow + dR*frame/frameCount, move.startCol + dC*frame/frameCount)
        drawBoard(screen, flipped)
        drawPieces(screen, board, flipped)
        endRow = 7 - move.endRow if flipped else move.endRow
        endCol = 7 - move.endCol if flipped else move.endCol
        color = colors[(endRow + endCol) % 2]
        endSquare = p.Rect(endCol * SQ_SIZE, endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        if move.pieceCaptured != '--':
            if move.enPassant:
                if flipped:
                    enPassantRow = 7 - move.startRow
                    enPassantCol = 7 - move.endCol
                else:
                    enPassantRow = move.startRow
                    enPassantCol = move.endCol
                enPassantSquare = p.Rect(enPassantCol * SQ_SIZE, enPassantRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
                screen.blit(IMAGES[move.pieceCaptured], enPassantSquare)
            else:
                screen.blit(IMAGES[move.pieceCaptured], endSquare)
        if move.castle:
            rookStartCol = 7 if move.endCol - move.startCol == 2 else 0
            rookEndCol = 5 if move.endCol - move.startCol == 2 else 3
            rookC = rookStartCol + (rookEndCol - rookStartCol) * frame / frameCount
            rookColor = colors[(move.endRow + rookEndCol) % 2]
            if flipped:
                rookDrawRow = 7 - move.endRow
                rookDrawCol = 7 - rookEndCol
                rookDrawC = 7 - rookC
            else:
                rookDrawRow = move.endRow
                rookDrawCol = rookEndCol
                rookDrawC = rookC
            rookSquare = p.Rect(rookDrawCol * SQ_SIZE, rookDrawRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            p.draw.rect(screen, rookColor, rookSquare)
            rookPiece = move.pieceMoved[0] + 'R'
            screen.blit(IMAGES[rookPiece], p.Rect(rookDrawC * SQ_SIZE, rookDrawRow * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        drawRow = 7 - r if flipped else r
        drawCol = 7 - c if flipped else c
        screen.blit(IMAGES[move.pieceMoved],
            p.Rect(drawCol * SQ_SIZE, drawRow * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)

def drawText(screen, text):
    global font
    shadowObject = font.render(text, 0, p.Color('black'))
    textObject = font.render(text, 0, p.Color('#B6AAA0'))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - textObject.get_width()/2, HEIGHT/2 - textObject.get_height()/2)
    screen.blit(shadowObject, textLocation.move(2, 2))
    screen.blit(textObject, textLocation)

def drawPromotionUI(screen, color):
    pieces = ['Q', 'R', 'B', 'N']
    # Draw a popup menu box in the middle of the screen
    menuRect = p.Rect(WIDTH // 2 - SQ_SIZE * 2, HEIGHT // 2 - SQ_SIZE // 2, SQ_SIZE * 4, SQ_SIZE)
    p.draw.rect(screen, p.Color('#DAD4D0'), menuRect)
    p.draw.rect(screen, p.Color('black'), menuRect, 2)  # Border
    for i, piece in enumerate(pieces):
        image = IMAGES[color + piece]
        imageRect = p.Rect(WIDTH // 2 - SQ_SIZE * 2 + i * SQ_SIZE, HEIGHT // 2 - SQ_SIZE // 2, SQ_SIZE, SQ_SIZE)
        screen.blit(image, imageRect)
    p.display.flip()
    while True:
        for e in p.event.get():
            if e.type == p.QUIT:
                return 'Q'  # Default to Queen if they try to close the window
            if e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()
                # Check if they clicked inside our menu box
                if menuRect.collidepoint(location):
                    # Calculate exactly which piece they clicked (0, 1, 2, or 3)
                    index = (location[0] - menuRect.left) // SQ_SIZE
                    return pieces[index]

if __name__ == "__main__":
    main()
