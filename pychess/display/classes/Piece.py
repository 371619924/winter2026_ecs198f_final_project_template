import pygame
import os

class Piece:
    def __init__(self, fen_notation: str, tile_width: int, tile_height: int):
        """
        Object representing one piece of the chess board
            Args:
                fen_notation (str): Fen Notation for piece i.e. R -> white rook, r -> black rook
                tile_width (int): Width of Tile Piece is Displayed in
                tile_height (int): Height of Tile Piece is Displayed in
        """
        self.color = "w"
        if fen_notation.islower():
            self.color = "b"
        piece_type = fen_notation.lower()
        piece_map = {
            "p": "pawn",
            "r": "rook",
            "n": "knight",
            "b": "bishop",
            "q": "queen",
            "k": "king"
        }
        self.img = pygame.image.load(os.path.join("display/imgs/", f"{self.color}_{piece_map[piece_type]}.png"))
        self.img = pygame.transform.scale(self.img, (tile_width - 10, tile_height - 10))