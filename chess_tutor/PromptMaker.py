# PromptMaker.py
import chess
import re

class PromptMaker:
    def __init__(self):
        # Define move pattern for detecting lone moves
        self._move_pattern = re.compile(r'^[NBRQK]?[a-h]?[1-8]?x?[a-h][1-8](?:=[NBRQ])?\+?\#?$|^O-O(-O)?$')

    def create_move_prompt(self, user_move: str, maia_move: str, board: chess.Board, user_message: str) -> str:
        """
        Create prompt for move analysis only if needed
        - For lone moves: no prompt needed
        - For move questions: create analysis prompt
        """
        # If it's just a move notation, no prompt needed
        if self._is_lone_move(user_message):
            return ""

        # If user asked about the move, create analysis prompt
        return f"""Looking at the chess position {board.fen()}, 
                  what do you think about the moves {user_move} and {maia_move}?"""

    def create_chat_prompt(self, board: chess.Board, user_message: str) -> str:
        """Create prompt for chess questions/chat"""
        return f"""Current chess position: {board.fen()}
                  User asks: {user_message}"""

    def create_game_start_response(self) -> str:
        """Fixed response for new game"""
        return "Let's play! I'll be black."

    def create_game_end_response(self, result: str) -> str:
        """Fixed response for game end"""
        responses = {
            "resign": "Good game! Would you like to play again?",
            "checkmate": "Checkmate! Good game! Would you like to play again?",
            "draw": "Game drawn. Would you like to play again?",
        }
        return responses.get(result, "Game over. Would you like to play again?")

    def create_no_game_response(self) -> str:
        """Fixed response when no game is in progress"""
        return "No game in progress. Type 'play' to start."

    def _is_lone_move(self, message: str) -> bool:
        """Check if message is just a move notation"""
        return bool(self._move_pattern.match(message.strip()))

# Global instance
prompt_maker = PromptMaker()