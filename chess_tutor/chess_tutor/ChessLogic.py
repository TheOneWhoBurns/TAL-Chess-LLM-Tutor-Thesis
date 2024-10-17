import chess
from .maia_engine import MaiaEngine
import os

class ChessLogicUnit:
    def __init__(self):
        self.board = chess.Board()
        self.move_history = []
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_dir = os.path.dirname(current_dir)
        self.maia_engine = MaiaEngine(project_dir)

    def get_current_position(self):
        """

        Get the current position of the board.

        Returns:
        str: FEN representation of the current board state
        """
        return self.board.fen()

    def make_move(self, move_san):
        """
        Make a move on the board.

        Args:
        move_san (str): The move in Standard Algebraic Notation (SAN) (e.g., "e4", "Nf3")

        Returns:
        bool: True if the move was legal and made, False otherwise
        """
        try:
            move = self.board.parse_san(move_san)
            if move in self.board.legal_moves:
                self.board.push(move)
                self.move_history.append(move_san)
                return True
            else:
                return False
        except ValueError:
            return False

    def get_maia_move(self):
        """
        Get a move from the Maia engine.

        Returns:
        str: The move in SAN
        """
        move = self.maia_engine.get_best_move(self.board)
        san_move = self.board.san(move)
        self.board.push(move)
        self.move_history.append(san_move)
        return san_move

    def get_current_turn(self):
        """
        Get whose turn it is to move.

        Returns:
        str: 'White' or 'Black'
        """
        return 'White' if self.board.turn == chess.WHITE else 'Black'

    def is_game_over(self):
        """
        Check if the game is over.

        Returns:
        bool: True if the game is over, False otherwise
        """
        return self.board.is_game_over()

    def get_game_result(self):
        """
        Get the result of the game if it's over.

        Returns:
        str: The result of the game ('1-0', '0-1', '1/2-1/2', or None if not over)
        """
        if self.board.is_checkmate():
            return '0-1' if self.board.turn == chess.WHITE else '1-0'
        elif self.board.is_stalemate() or self.board.is_insufficient_material() or self.board.is_seventyfive_moves() or self.board.is_fivefold_repetition():
            return '1/2-1/2'
        else:
            return None

    def get_legal_moves(self):
        """
        Get all legal moves in the current position.

        Returns:
        list: List of legal moves in SAN
        """
        return [self.board.san(move) for move in self.board.legal_moves]

    def get_move_history(self):
        """
        Get the history of moves made in the game.

        Returns:
        list: List of moves in SAN
        """
        return self.move_history

    def reset_game(self):
        """
        Reset the game to the starting position.
        """
        self.board.reset()
        self.move_history.clear()

    def handle_intent(self, intent, move=None):
        """
        Handle different intents from the intent classification system.

        Args:
        intent (str): The classified intent
        move (str, optional): The move if the intent is 'make_chess_move'

        Returns:
        dict: A response based on the intent
        """
        if intent == "make_chess_move":
            if move and self.make_move(move):
                maia_move = self.get_maia_move()
                return {"status": "success", "message": f"Move {move} made successfully. Maia responds with {maia_move}."}
            else:
                return {"status": "error", "message": "Invalid move."}
        elif intent == "ask_explanation":
            return {"status": "success", "message": "What would you like explained?"}
        elif intent == "request_game":
            self.reset_game()
            return {"status": "success", "message": "New game started."}
        elif intent == "general_chat":
            return {"status": "success", "message": "What would you like to chat about?"}
        elif intent == "quit_game":
            return {"status": "success", "message": "Game ended. Thanks for playing!"}
        else:
            return {"status": "error", "message": "Unknown intent."}

    def close(self):
        """
        Close the Maia engine.
        """
        self.maia_engine.close()

    def __del__(self):
        self.close()