# PromptMaker.py
import re
from typing import List, Dict

class PromptMaker:
    def __init__(self):
        # Define move pattern for detecting lone moves
        self._move_pattern = re.compile(r'^[NBRQK]?[a-h]?[1-8]?x?[a-h][1-8](?:=[NBRQ])?\+?\#?$|^O-O(-O)?$')

    def create_move_prompt(self, user_move: str, maia_move: str, move_history: List[str], chat_history: List[Dict[str, str]], user_message: str) -> str:
        """
        Create prompt for move analysis using move history and chat history

        Args:
            user_move: The current move made by the user
            maia_move: The response move by Maia
            move_history: List of all moves in the game so far in algebraic notation
            chat_history: List of dictionaries containing previous chat messages
                        Format: [{"role": "user"|"assistant", "content": "message"}]
            user_message: The current message from the user
        """

        # Format move history
        moves_formatted = " ".join(f"{i//2 + 1}.{move}" if i % 2 == 0 else move
                                   for i, move in enumerate(move_history))

        # Format recent chat context (last 3 exchanges)
        recent_chat = chat_history[-6:] if len(chat_history) > 6 else chat_history
        chat_formatted = "\n".join([
            f"{'User' if msg['role'] == 'user' else 'You'}: {msg['content']}"
            for msg in recent_chat
        ])

        return f"""
            You are an AI chess tutor designed to play chess with users while providing instruction to help them improve their skills. Your goal is to create an engaging and educational experience for the user.
            
            Game progress so far:
            {moves_formatted}
            
            Recent conversation:
            {chat_formatted}
            
            The user's latest move:
            {user_move}
            
            Maia's response move:
            {maia_move}
            
            Then, provide your response to the user. Your response should be very very short
            - For normal moves: Offer a brief, one-line comment. (THIS IS THE MOST IMPORTANT PART)
            - For crucial moves: Explain the move's importance and potential impact in 1 sentence.
            - If explaining a concept: Provide a concise explanation that hints at the best move without revealing it directly.
            
            Always maintain a friendly and encouraging tone, and adapt your explanations to the apparent skill level of the user. Keep your response concise and information-dense, avoiding walls of text.
            
            Remember to:
            - Make your response feel like a natural dialog not a commentary of the game that will continue as the game progress, as if being taught by another human or a friend, refer to black as "me" and white as "you", use emojis and talk casually (you may even have a bit of banter).
            - Consider the context of any previous conversation when responding.
            - If the user has been struggling with certain concepts (based on chat history), provide gentle guidance.
            """

    def create_chat_prompt(self, move_history: List[str], chat_history: List[Dict[str, str]], user_message: str) -> str:
        """
        Create prompt for chess questions/chat

        Args:
            move_history: List of all moves in the game
            chat_history: List of previous chat messages
            user_message: Current user message
        """
        moves_formatted = " ".join(f"{i//2 + 1}.{move}" if i % 2 == 0 else move
                                   for i, move in enumerate(move_history))

        recent_chat = chat_history[-6:] if len(chat_history) > 6 else chat_history
        chat_formatted = "\n".join([
            f"{'User' if msg['role'] == 'user' else 'You'}: {msg['content']}"
            for msg in recent_chat
        ])

        return f"""Game progress:
                  {moves_formatted}
                  
                  Recent conversation:
                  {chat_formatted}
                  
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