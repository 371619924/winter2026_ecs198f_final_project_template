class ChessLogic:
    def __init__(self):
        """
        Initalize the ChessLogic Object. External fields are board and result

        board -> Two Dimensional List of string Representing the Current State of the Board
            P, R, N, B, Q, K - White Pieces

            p, r, n, b, q, k - Black Pieces

            '' - Empty Square

        result -> The current result of the game
            w - White Win

            b - Black Win

            d - Draw

            '' - Game In Progress
        """
        self.board = [
            ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
            ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
            ['', '', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', ''],
            ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
            ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'],
        ]
        self.result = ""
        self.turn = "w"

    def _coord_to_index(self, coord: str):
        if len(coord) != 2:
            return None

        file_char = coord[0].lower()
        rank_char = coord[1]

        if file_char not in "abcdefgh" or rank_char not in "12345678":
            return None

        col = ord(file_char) - ord("a")
        row = 8 - int(rank_char)
        return row, col

    def _is_white(self, piece: str) -> bool:
        return piece != "" and piece.isupper()

    def _is_black(self, piece: str) -> bool:
        return piece != "" and piece.islower()

    def _same_color(self, piece1: str, piece2: str) -> bool:
        if piece1 == "" or piece2 == "":
            return False
        return (self._is_white(piece1) and self._is_white(piece2)) or (
            self._is_black(piece1) and self._is_black(piece2)
        )

    def _path_clear(self, sr: int, sc: int, er: int, ec: int) -> bool:
        dr = er - sr
        dc = ec - sc

        step_r = 0 if dr == 0 else (1 if dr > 0 else -1)
        step_c = 0 if dc == 0 else (1 if dc > 0 else -1)

        r = sr + step_r
        c = sc + step_c

        while (r, c) != (er, ec):
            if self.board[r][c] != "":
                return False
            r += step_r
            c += step_c

        return True

    def _valid_pawn_move(
        self, piece: str, sr: int, sc: int, er: int, ec: int, target: str
    ) -> bool:
        direction = -1 if self._is_white(piece) else 1
        start_row = 6 if self._is_white(piece) else 1

        dr = er - sr
        dc = ec - sc

        if dc == 0:
            if target != "":
                return False
            if dr == direction:
                return True
            if dr == 2 * direction and sr == start_row:
                middle_row = sr + direction
                return self.board[middle_row][sc] == ""
            return False

        if abs(dc) == 1 and dr == direction:
            return target != "" and not self._same_color(piece, target)

        return False

    def _valid_rook_move(self, sr: int, sc: int, er: int, ec: int) -> bool:
        if sr != er and sc != ec:
            return False
        return self._path_clear(sr, sc, er, ec)

    def _valid_knight_move(self, sr: int, sc: int, er: int, ec: int) -> bool:
        dr = abs(er - sr)
        dc = abs(ec - sc)
        return (dr, dc) in [(2, 1), (1, 2)]

    def _valid_bishop_move(self, sr: int, sc: int, er: int, ec: int) -> bool:
        if abs(er - sr) != abs(ec - sc):
            return False
        return self._path_clear(sr, sc, er, ec)

    def _valid_queen_move(self, sr: int, sc: int, er: int, ec: int) -> bool:
        if sr == er or sc == ec:
            return self._valid_rook_move(sr, sc, er, ec)
        if abs(er - sr) == abs(ec - sc):
            return self._valid_bishop_move(sr, sc, er, ec)
        return False

    def _valid_king_move(self, sr: int, sc: int, er: int, ec: int) -> bool:
        dr = abs(er - sr)
        dc = abs(ec - sc)
        return max(dr, dc) == 1

    def _is_valid_piece_move(
        self, piece: str, sr: int, sc: int, er: int, ec: int, target: str
    ) -> bool:
        if (sr, sc) == (er, ec):
            return False

        piece_type = piece.lower()

        if piece_type == "p":
            return self._valid_pawn_move(piece, sr, sc, er, ec, target)
        if piece_type == "r":
            return self._valid_rook_move(sr, sc, er, ec)
        if piece_type == "n":
            return self._valid_knight_move(sr, sc, er, ec)
        if piece_type == "b":
            return self._valid_bishop_move(sr, sc, er, ec)
        if piece_type == "q":
            return self._valid_queen_move(sr, sc, er, ec)
        if piece_type == "k":
            return self._valid_king_move(sr, sc, er, ec)

        return False

    def _build_notation(self, piece: str, start: str, end: str, capture: bool) -> str:
        prefix = "" if piece.lower() == "p" else piece.lower()
        if capture:
            return f"{prefix}{start}x{end}"
        return f"{prefix}{start}{end}"

    def play_move(self, move: str) -> str:
        """
        Function to make a move if it is a valid move. This function is called everytime a move in made on the board

        Args:
            move (str): The move which is proposed. The format is the following: starting_sqaure}{ending_square}

            i.e. e2e4 - This means that whatever piece is on E2 is moved to E4

        Returns:
            str: Extended Chess Notation for the move, if valid. Empty str if the move is invalid
        """
        if self.result != "":
            return ""

        if not isinstance(move, str) or len(move) != 4:
            return ""

        start = move[:2].lower()
        end = move[2:].lower()

        start_idx = self._coord_to_index(start)
        end_idx = self._coord_to_index(end)

        if start_idx is None or end_idx is None:
            return ""

        sr, sc = start_idx
        er, ec = end_idx

        piece = self.board[sr][sc]
        target = self.board[er][ec]

        if piece == "":
            return ""

        if self.turn == "w" and not self._is_white(piece):
            return ""
        if self.turn == "b" and not self._is_black(piece):
            return ""

        if self._same_color(piece, target):
            return ""

        if not self._is_valid_piece_move(piece, sr, sc, er, ec, target):
            return ""

        capture = target != ""

        self.board[er][ec] = piece
        self.board[sr][sc] = ""

        notation = self._build_notation(piece, start, end, capture)

        self.turn = "b" if self.turn == "w" else "w"

        return notation