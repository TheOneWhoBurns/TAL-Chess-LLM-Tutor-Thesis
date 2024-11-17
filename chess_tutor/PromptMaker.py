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
        """

        # If user asked about the move, create analysis prompt
        return f"""
            Here is the current chess position and the moves to evaluate:

            {board.fen()}
            {user_move}
            {maia_move}
            
            Instructions:
            1. Analyze the given chess position and the two moves (user's move and Maia's move).
            2. Evaluate the moves based on their strategic importance and impact on the game.
            3. Provide a concise response to the user, focusing on educational value.
            
            Use the following guidelines for your response:
            - For normal moves: Offer a brief, one-line comment.
            - For crucial moves: Explain the move's importance and potential impact in 2-3 sentences.
            - If explaining a concept: Provide a concise explanation that hints at the best move without revealing it directly.
            
            Always maintain a friendly and encouraging tone, and adapt your explanations to the apparent skill level of the user
            Then, provide your feedback to the user
            Remember to keep your response concise, at most one sentence, providing longer explanations only when strictly necessary for crucial moves or complex concepts."""

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