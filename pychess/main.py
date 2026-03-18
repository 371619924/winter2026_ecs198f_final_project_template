import pygame

from display.classes.Board import Board
from logic.chess_logic import ChessLogic

"""
Configuration Variables
"""
WINDOW_SIZE = (600, 600)

"""
Pygame Initialization
"""
pygame.init()
screen = pygame.display.set_mode(WINDOW_SIZE)
font = pygame.font.SysFont(None, 50)

"""
Chess Game Logic and Chess Board Initalization
"""
logic = ChessLogic()
board = Board(screen, WINDOW_SIZE[0], WINDOW_SIZE[1], logic, font)

def draw():
    """
    Draw/Update the current game state to Pygame Window

    Args:
        display: Pygame Screen Object
        font: Pygame Font Object
    """
    board.draw()
    pygame.display.update()

if __name__ == "__main__":
    """
    Game Loop
    """
    draw()
    running = True
    while running:
        mx, my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    board.handle_click(mx, my)
                    # print("Board:\n", logic.board)
            # elif event.type == pygame.KEYDOWN:
            #     if event.key == pygame.K_w:
            #         logic.result = "w"
            #         board.debug = "win"
        pygame.display.update()
        