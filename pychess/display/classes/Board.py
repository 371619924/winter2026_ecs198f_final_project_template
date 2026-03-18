import pygame
import copy

from display.classes.Square import Square
from display.classes.Piece import Piece

from logic.chess_logic import ChessLogic

class Board:
    def __init__(self, screen: pygame.Surface, width: int, height: int, logic: ChessLogic):
        """
        Object representing the Chess Board

        Args:
            width (int): The width of the Chess Board
            height (int): The height of the Chess Board
            logic (ChessLogic): ChessLogic object which implements the Chess Game Logic 
                (i.e. Board Representation, Move Making Logic)
        """
        self.screen = screen
        
        self.width = width
        self.height = height
        self.tile_width = width // 8
        self.tile_height = height // 8
        self.selected_piece = None

        self.logic = logic
        self.current_board = copy.deepcopy(logic.board)
        self.squares: list[Square] = self.generate_squares()

        self.start_square = None
        self.end_square = None

    def generate_squares(self):
        """
        Construct all Square Objects of the Chess Board
        """
        output = []
        for y in range(8):
            for x in range(8):
                piece = None
                if self.logic.board[y][x] != "":
                    piece = Piece(self.logic.board[y][x], self.tile_width, self.tile_height)
                square = Square(x, y, self.tile_width, self.tile_height)
                square.set_occuping_piece(piece)
                output.append(square)
        return output

    def update_squares(self):
        """
        Update all Square Objects of the Chess Board by placing pieces based on the ChessLogic Board Representation
        """
        for y in range(8):      # loop through every row
            for x in range(8):  # loop through every column
                piece = None
                if self.logic.board[y][x] != "":
                    # make this visual square's piece their current piece
                    piece = self.squares[y * 8 + x].occupying_piece
                    if self.logic.board[y][x] != self.current_board[y][x]:
                        # make this visual square's piece a new piece
                        piece = Piece(self.logic.board[y][x], self.tile_width, self.tile_height)
                self.squares[y * 8 + x].set_occuping_piece(piece)

    def get_square_from_pos(self, pos: tuple[int, int]) -> Square | None:
        """
        Get Square Object from Relative Position of Square

        Args:
            pos (tuple[int, int]): (x, y) coordinates of the Square
        
        Returns:
            Square | None: Square Object for Relative Position or None if invalid coordinates supplied
        """ 
        for square in self.squares:
            if (square.x, square.y) == (pos[0], pos[1]):
                return square
    
    def handle_click(self, mx: int, my: int):
        """
        Pygame Event Handler for when user clicks the board. 
        
        Calls the ChessLogic play_move function if a move has been parsed

        Args:
            mx (int): Absolute x coordinate of click
            my (int): Absolute y coordinate of click
        """
        x = mx // self.tile_width
        y = my // self.tile_height
        clicked_square = self.get_square_from_pos((x, y))
        if clicked_square is not None:
            # first click
            if self.start_square is None and clicked_square.occupying_piece is not None and clicked_square.occupying_piece.color == self.logic.turn:
                self.start_square = clicked_square
                self.start_square.highlight = True
                self.start_square.draw(self.screen)
            
            # second click / try playing move
            elif self.start_square is not None and self.end_square is None:
                self.end_square = clicked_square
                if self.start_square != self.end_square:
                    self.logic.play_move(f"{self.start_square.get_coord()}{self.end_square.get_coord()}")
                    self.update_squares()

                # reset clicked areas
                self.start_square.highlight = False
                self.start_square.draw(self.screen)
                self.start_square = None
                self.end_square.draw(self.screen)
                self.end_square = None

                # update visual
                self.draw(self.screen, None)
    
    def draw(self, display, font):
        """
        Draws the Board, with result message if applicable, on Pygame Screen

        Args:
            display: Pygame Screen Object
            font: Pygame Font Object
        """
        for square in self.squares:
            square.draw(display)
        if self.logic.result != "":
            white = (255, 255, 255)
            black = (0, 0, 0)
            red = (255, 0, 0)
            gray = (200, 200, 200)

            message = "Draw"
            if self.logic.result == "w":
                message = "White wins"
            elif self.logic.result == "b":
                message = "Black wins"
            text_surface = font.render(message, True, white)
            text_rect = text_surface.get_rect(center=(self.width // 2, self.height // 2))
            rect_width = text_rect.width + 40
            rect_height = text_rect.height + 20
            rect_x = text_rect.x - 20
            rect_y = text_rect.y - 10

            pygame.draw.rect(display, gray, (rect_x, rect_y, rect_width, rect_height))
            pygame.draw.rect(display, red, (rect_x, rect_y, rect_width, rect_height), 3)

            display.blit(text_surface, text_rect)