import copy

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
            ['',  '',  '',  '',  '',  '',  '',  '' ],
            ['',  '',  '',  '',  '',  '',  '',  '' ],
            ['',  '',  '',  '',  '',  '',  '',  '' ],
            ['',  '',  '',  '',  '',  '',  '',  '' ],
            ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
            ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'],
        ]

        # for testing
        # self.board = [
        #     ['k', '',  '',  '',  '',  '',  '',  'p' ],
        #     ['',  '',  '',  '',  '',  '',  'P',  '' ],
        #     ['',  '',  '',  '',  '',  '',  '',  '' ],
        #     ['',  '',  '',  '',  '',  '',  '',  '' ],
        #     ['',  '',  '',  '',  '',  '',  '',  '' ],
        #     ['',  '',  '',  '',  '',  'p',  '',  '' ],
        #     ['',  '',  '',  '',  '',  '',  '',  '' ],
        #     ['K', '',  '',  '',  '',  '',  'N',  '' ],
        # ]

        self.result = ""
        self.turn = "w"

        self.just_moved_x = None
        self.just_moved_y = None
        self.en_passant = False

        self.white_king_moved = False
        self.white_rook_left_moved = False
        self.white_rook_right_moved = False
        self.black_king_moved = False
        self.black_rook_left_moved = False
        self.black_rook_right_moved = False
        self.castle_queen_side = False
        self.castle_king_side = False

        self.checking_checkmate = False

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
    
    def _valid_en_passant(self, piece:str, target:str, check_row:int, check_col:int):
        en_passant_is_pawn = (self.board[check_row][check_col].lower() == "p")
        # if not en_passant_is_pawn:
        #     print("you cant en passant a non-pawn")
        
        en_passant_enemy = (not self._same_color(piece, self.board[check_row][check_col]))
        # if not en_passant_enemy:
        #     print("cant en passant an ally")

        en_passant_just_moved = (check_col == self.just_moved_x and check_row == self.just_moved_y)
        # if not en_passant_just_moved:
        #     print("pawn you're trying to en passant didn't move last turn")

        return (target == "" and en_passant_just_moved and en_passant_enemy and en_passant_is_pawn)

    def _valid_pawn_move(
        self, piece: str, sr: int, sc: int, er: int, ec: int, target: str
    ) -> bool:
        direction = -1 if self._is_white(piece) else 1
        start_row = 6 if self._is_white(piece) else 1

        dr = er - sr
        dc = ec - sc

        # handle moving "forward"
        if dc == 0:
            if target != "":
                return False
            if dr == direction:
                return True
            if dr == 2 * direction and sr == start_row:
                middle_row = sr + direction
                return self.board[middle_row][sc] == ""
            return False

        # handle moving "forward" diagonally to capture
        if abs(dc) == 1 and dr == direction:
            self.en_passant = self._valid_en_passant(piece, target, er-direction, ec)

            return (target != "" and not self._same_color(piece, target)) or self.en_passant

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

    def _valid_castle(self, sr:int, sc:int, er:int, ec:int):
        if sr != er:
            # print("castles only happen on the same row")
            return False
        
        castle_king_moved = self.black_king_moved if self.turn == "b" else self.white_king_moved
        if castle_king_moved:
            # print("you can't castle a moved king")
            return False
        
        # king side castling
        dc = ec - sc
        if dc == 2:
            target_rook = self.board[sr][ec+1]
            castle_rook_available = (self.turn == "b" and target_rook == "r") or (self.turn == "w" and target_rook == "R")
            if not castle_rook_available:
                # print("king side rook not available")
                return False

            castle_to_king_side = (self.turn == "b" and not self.black_rook_right_moved) or (self.turn == "w" and not self.white_rook_right_moved)
            if not castle_to_king_side:
                # print("you can't castle with a moved king side rook")
                return False

            # check if area is clear and safe            
            for i in range(1, 2+1, 1):
                if self.board[sr][sc+i] != "":
                    # print("cant king side castle with pieces in the way")
                    return False
                
                # print("castle checking:")
                simulated_board = copy.deepcopy(self.board)
                simulated_board[sr][sc+i] = "K" if self.turn == "w" else "k"
                simulated_board[sr][sc] = ""
                if self._turns_king_in_check(simulated_board, self.turn):
                    del simulated_board
                    # print("cant king side castle when area is in check")
                    return False
                del simulated_board
            self.castle_king_side = True
            return True
        
        # queen side castling
        elif dc == -3:
            target_rook = self.board[sr][ec-1]
            castle_rook_available = (self.turn == "b" and target_rook == "r") or (self.turn == "w" and target_rook == "R")
            if not castle_rook_available:
                # print("queen side rook not available")
                return False

            castle_to_queen_side = (self.turn == "b" and not self.black_rook_left_moved) or (self.turn == "w" and not self.white_rook_left_moved)
            if not castle_to_queen_side:
                # print("you can't castle with a moved queen side rook")
                return False
            
            # check if area is clear and safe            
            for i in range(1, 3+1, 1):
                if self.board[sr][sc-i] != "":
                    # print("cant queen side castle with pieces in the way")
                    return False
                
                # print("castle checking:")
                simulated_board = copy.deepcopy(self.board)
                simulated_board[sr][sc-i] = "K" if self.turn == "w" else "k"
                simulated_board[sr][sc] = ""
                if self._turns_king_in_check(simulated_board, self.turn):
                    del simulated_board
                    # print("cant queen side castle when area is in check")
                    return False
                del simulated_board
            self.castle_queen_side = True
            return True
        
        # print("you cant castle there")
        return False

    def _valid_king_move(self, sr: int, sc: int, er: int, ec: int) -> bool:
        dr = abs(er - sr)
        dc = ec - sc

        # allow if king is only moving one space
        if max(dr, abs(dc)) == 1:
            return True

        # castling
        if er != (0 if self.turn == "b" else 7):
            # print("castles can only happen on the starting row")
            return False

        return self._valid_castle(sr, sc, er, ec)
        
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
    
    def _get_piece_position(self, board:list[list[str]], piece:str):
        for y in range(8):
            for x in range(8):
                if board[y][x] == piece:
                    return (y, x)
        return None
    
    def _turns_king_in_check(self, board:list[list[str]], turn:str):
        king_pos = self._get_piece_position(board,
            "k" if turn == "b" else "K"
        )
        if king_pos is None:
            return None
        king_y, king_x = king_pos

        # check above
        for y in range(king_y-1, -1, -1):
            # print("up check")
            # skip over empty spaces
            if board[y][king_x] == "":
                continue
            # print("y:", y)
            
            # dont worry about turn's own piece
            if (self._is_black(board[y][king_x]) and turn == "b") or \
                (self._is_white(board[y][king_x]) and turn == "w"):
                break
            # print("piece is opponent's piece")
            
            piece = board[y][king_x].lower()
            # print("piece:", piece)

            # dont worry about these pieces
            if piece in ["p", "n", "b"]:
                break
            # print("piece not pawn, knight, or bishop")
            
            # check if king piece in range
            if piece == "k" and y != (king_y - 1):
                break

            # piece will be a rook or queen, therefore in check
            # print("will be in check")
            return True

        # check below
        for y in range(king_y+1, 8, 1):
            # print("down check")
            if board[y][king_x] == "":
                continue
            # print("y:", y)

            # dont worry about turn's own piece
            if (self._is_black(board[y][king_x]) and turn == "b") or \
                (self._is_white(board[y][king_x]) and turn == "w"):
                break
            # print("piece is opponent's piece")
            
            piece = board[y][king_x].lower()
            # print("piece:", piece)

            # dont worry about these pieces
            if piece in ["p", "n", "b"]:
                break
            # print("piece not pawn, knight, or bishop")
            
            # check if king piece in range
            if piece == "k" and y != (king_y + 1):
                break

            # piece will be a rook or queen, therefore in check
            # print("will be in check")
            return True

        # check left
        for x in range(king_x-1, -1, -1):
            # print("left check")
            # skip over empty spaces
            if board[king_y][x] == "":
                continue
            # print("x:", x)
            
            # dont worry about turn's own piece
            if (self._is_black(board[king_y][x]) and turn == "b") or \
                (self._is_white(board[king_y][x]) and turn == "w"):
                break
            # print("piece is opponent's piece")
            
            piece = board[king_y][x].lower()
            # print("piece:", piece)

            # dont worry about these pieces
            if piece in ["p", "n", "b"]:
                break
            # print("piece not pawn, knight, or bishop")
            
            # check if king piece in range
            if piece == "k" and x != (king_x - 1):
                break

            # piece will be a rook or queen, therefore in check
            # print("will be in check")
            return True

        # check right
        for x in range(king_x+1, 8, 1):
            # print("right check")
            # skip over empty spaces
            if board[king_y][x] == "":
                continue
            # print("x:", x)
            
            # dont worry about turn's own piece
            if (self._is_black(board[king_y][x]) and turn == "b") or \
                (self._is_white(board[king_y][x]) and turn == "w"):
                break
            # print("piece is opponent's piece")
            
            piece = board[king_y][x].lower()
            # print("piece:", piece)

            # dont worry about these pieces
            if piece in ["p", "n", "b"]:
                break
            # print("piece not pawn, knight, or bishop")
            
            # check if king piece in range
            if piece == "k" and x != (king_x + 1):
                break

            # piece will be a rook or queen, therefore in check
            # print("will be in check")
            return True

        # check up left
        for diag in range(1, min(king_x+1, king_y+1), 1):
            # print("up left check")
            check_x = king_x - diag
            check_y = king_y - diag

            # skip over empty spaces
            if board[check_y][check_x] == "":
                continue
            # print(f"({check_x}, {check_y})")

            # dont worry about turn's own piece
            if (self._is_black(board[check_y][check_x]) and turn == "b") or \
                (self._is_white(board[check_y][check_x]) and turn == "w"):
                break
            # print("piece is opponent's piece")
            
            piece = board[check_y][check_x].lower()
            # print("piece:", piece)

            # dont worry about these pieces
            if piece in ["r", "n"]:
                break
            # print("piece not pawn, knight, or bishop")
            
            # check if king or pawn piece in range
            if (piece == "k" or (piece == "p" and turn == "w")) and check_x != (king_x - 1) and check_y != (king_y - 1):
                break

            # piece will be a bishop or queen, therefore in check
            # print("will be in check")
            return True

        # check up right
        for diag in range(1, min(8 - king_x-1+1, king_y+1), 1):
            # print("up right check")
            check_x = king_x + diag
            check_y = king_y - diag

            # skip over empty spaces
            if board[check_y][check_x] == "":
                continue
            # print(f"({check_x}, {check_y})")

            # dont worry about turn's own piece
            if (self._is_black(board[check_y][check_x]) and turn == "b") or \
                (self._is_white(board[check_y][check_x]) and turn == "w"):
                break
            # print("piece is opponent's piece")
            
            piece = board[check_y][check_x].lower()
            # print("piece:", piece)

            # dont worry about these pieces
            if piece in ["r", "n"]:
                break
            # print("piece not pawn, knight, or bishop")
            
            # check if king or pawn piece in range
            if (piece == "k" or (piece == "p" and turn == "w")) and check_x != (king_x + 1) and check_y != (king_y - 1):
                break

            # piece will be a bishop or queen, therefore in check
            # print("will be in check")
            return True

        # check down left
        for diag in range(1, min(king_x+1, 8 - king_y-1+1), 1):
            # print("down left check")
            check_x = king_x - diag
            check_y = king_y + diag

            # skip over empty spaces
            if board[check_y][check_x] == "":
                continue
            # print(f"({check_x}, {check_y})")

            # dont worry about turn's own piece
            if (self._is_black(board[check_y][check_x]) and turn == "b") or \
                (self._is_white(board[check_y][check_x]) and turn == "w"):
                break
            # print("piece is opponent's piece")
            
            piece = board[check_y][check_x].lower()
            # print("piece:", piece)

            # dont worry about these pieces
            if piece in ["r", "n"]:
                break
            # print("piece not pawn, knight, or bishop")
            
            # check if king or pawn piece in range
            if (piece == "k" or (piece == "p" and turn == "b")) and check_x != (king_x - 1) and check_y != (king_y + 1):
                break

            # piece will be a bishop or queen, therefore in check
            # print("will be in check")
            return True

        # check down right
        for diag in range(1, min(8 - king_x-1+1, 8 - king_y-1+1), 1):
            # print("down right check")
            check_x = king_x + diag
            check_y = king_y + diag

            # skip over empty spaces
            if board[check_y][check_x] == "":
                continue
            # print(f"({check_x}, {check_y})")

            # dont worry about turn's own piece
            if (self._is_black(board[check_y][check_x]) and turn == "b") or \
                (self._is_white(board[check_y][check_x]) and turn == "w"):
                break
            # print("piece is opponent's piece")
            
            piece = board[check_y][check_x].lower()
            # print("piece:", piece)

            # dont worry about these pieces
            if piece in ["r", "n"]:
                break
            # print("piece not pawn, knight, or bishop")
            
            # check if king or pawn piece in range
            if (piece == "k" or (piece == "p" and turn == "b")) and check_x != (king_x + 1) and check_y != (king_y + 1):
                break

            # piece will be a bishop or queen, therefore in check
            # print("will be in check")
            return True

        # check knights
        knight_check_positions = [
            (-2, -1), (-1, -2), (1, -2), (2, -1),
            (-2,  1), (-1,  2), (1,  2), (2,  1)
        ]
        for pos in knight_check_positions:
            change_x, change_y = pos

            # keep in bounds of the board
            if (king_x + change_x) >= 8 or (king_x + change_x) < 0 or \
                (king_y + change_y) >= 8 or (king_y + change_y) < 0:
                continue
            piece = board[king_y + change_y][king_x + change_x]

            # only worry about knights
            if piece.lower() != "n":
                continue

            # check if its turn's own piece, if so then in check
            if (self._is_black(piece) and turn == "w") or \
                (self._is_white(piece) and turn == "b"):
                # print("will be in check")
                return True
        
        return False

    def _build_notation(self, piece: str, start: str, end: str, capture: bool) -> str:
        prefix = "" if piece.lower() == "p" else piece.lower()
        if capture:
            return f"{prefix}{start}x{end}"
        return f"{prefix}{start}{end}"
    
    def _turn_in_checkmate(self):
        king_possible_moves = [
            (-1, -1), (0, -1), (1, -1),
            (-1,  0), (0,  0),  (1,  0),
            (-1,  1), (0,  1), (1,  1)
        ]
        king_y, king_x = self._get_piece_position(self.board, "k" if self.turn == "b" else "K")
        checkmate = True
        empty_places = 0
        for pos in king_possible_moves:
            change_x, change_y = pos
            check_x = king_x + change_x
            check_y = king_y + change_y
            #skip invalid positions
            if (check_x < 0 or check_x > 7) or (check_y < 0 or check_y > 7):
                continue

            # skip places the king can't move
            if pos != (0, 0):
                if self.board[check_y][check_x] != "":
                    continue
                empty_places += 1
            # print(f"checking ({check_x}, {check_y})")

            simulated_board = copy.deepcopy(self.board)
            simulated_board[king_y][king_x] = ""
            simulated_board[check_y][check_x] = "K" if self.turn == "w" else "k"
            sim_king_in_check = self._turns_king_in_check(simulated_board, self.turn)
            if sim_king_in_check is None:
                return None
            elif not sim_king_in_check:
                checkmate = False
            del simulated_board
        
        return checkmate and (empty_places > 0)

    def play_move(self, move: str) -> str:
        """
        Function to make a move if it is a valid move. This function is called everytime a move in made on the board

        Args:
            move (str): The move which is proposed. The format is the following: starting_sqaure}{ending_square}

            i.e. e2e4 - This means that whatever piece is on E2 is moved to E4

        Returns:
            str: Extended Chess Notation for the move, if valid. Empty str if the move is invalid
        """
        # dont play a move if the game is over
        if self.result != "":
            return ""

        # dont handle moves that arent a string or arent 4 characters long
        if not isinstance(move, str) or len(move) != 4:
            return ""

        start = move[:2].lower()
        end = move[2:].lower()

        start_idx = self._coord_to_index(start)
        end_idx = self._coord_to_index(end)

        # dont handle moves that arent on the board
        if start_idx is None or end_idx is None:
            return ""

        sr, sc = start_idx
        er, ec = end_idx

        piece = self.board[sr][sc]
        target = self.board[er][ec]

        # dont handle moves with no piece to move
        if piece == "":
            return ""

        # dont handle moves from a side if it isnt their turn
        if self.turn == "w" and not self._is_white(piece):
            return ""
        if self.turn == "b" and not self._is_black(piece):
            return ""

        # dont handle moves that would capture piece on the same side
        if self._same_color(piece, target):
            return ""

        # dont handle invalid moves
        if not self._is_valid_piece_move(piece, sr, sc, er, ec, target):
            return ""

        # dont handle moves that would put the side in turn in check
        # (i.e dont do moves that put your own king in check silly)
        simulated_board = copy.deepcopy(self.board)
        simulated_board[er][ec] = piece
        simulated_board[sr][sc] = ""
        if self._turns_king_in_check(simulated_board, self.turn):
            del simulated_board
            return ""
        del simulated_board

        # perform move
        capture = (target != "") or self.en_passant
        self.just_moved_x = ec
        self.just_moved_y = er

        self.board[er][ec] = piece
        self.board[sr][sc] = ""

        # handle pawn promotion
        pawn_promoted = False
        if er == 0 and piece == "P":
            # print("promotion white")
            self.board[er][ec] = "Q"
            pawn_promoted = True
        elif er == 7 and piece == "p":
            # print("promotion black")
            self.board[er][ec] = "q"
            pawn_promoted = True

        # handle en passant
        if self.en_passant:
            self.board[er-1 if self.turn == "b" else er+1][ec] = ""
        
        # handle castling
        if self.castle_king_side:
            self.board[er][ec+1] = ""
            self.board[er][ec-1] = "r" if self.turn == "b" else "R"
        elif self.castle_queen_side:
            self.board[er][ec-1] = ""
            self.board[er][ec+1] = "r" if self.turn == "b" else "R"

        if   piece == "K":  self.white_king_moved = True
        elif piece == "k":  self.black_king_moved = True
        elif piece == "R":
            if   (sr == 7 and sc == 0):  self.white_rook_left_moved  = True
            elif (sr == 7 and sc == 7):  self.white_rook_right_moved = True
        elif piece == "r":
            if   (sr == 0 and sc == 0):  self.black_rook_left_moved  = True
            elif (sr == 0 and sc == 7):  self.black_rook_right_moved = True

        # return move notation
        notation = self._build_notation(piece, start, end, capture)
        if pawn_promoted:  notation += "=Q"
        if self.castle_king_side:  notation = "O-O"
        if self.castle_queen_side: notation = "O-O-O"

        self.turn = "b" if self.turn == "w" else "w"
        self.en_passant = False
        self.castle_queen_side = False
        self.castle_king_side = False

        # print("board:", self.board)
        
        if self._turn_in_checkmate():
            if not self._turns_king_in_check(self.board, self.turn):
                # print("stalemate")
                pass
            self.result = "w" if self.turn == "b" else "b"

        # print("Move:", notation)
        return notation