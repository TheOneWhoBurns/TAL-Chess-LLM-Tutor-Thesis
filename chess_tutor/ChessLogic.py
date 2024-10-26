from typing import List, Dict, Optional
import chess
from .maia_engine import MaiaEngine
import os
<<<<<<< HEAD
from .intent import intent_classifier
from .PromptMaker import PromptMaker
from .models import model_manager
=======
>>>>>>> parent of de49885 (latetest updates)

class ChessLogicUnit:
    def __init__(self, project_dir=None):
        self.board = chess.Board()
        self.move_history = []
<<<<<<< HEAD
        if project_dir:
            self.maia_engine = MaiaEngine(project_dir)
        self.game_in_progress = False
        self.prompt_maker = PromptMaker()

    def get_move_history(self) -> List[str]:
        """Get the history of moves"""
        return self.move_history

    def get_current_position(self) -> str:
        """Get current FEN position"""
=======
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_dir = os.path.dirname(current_dir)
        self.maia_engine = MaiaEngine(project_dir)

    def get_current_position(self):
        """

        Get the current position of the board.

        Returns:
        str: FEN representation of the current board state
        """
>>>>>>> parent of de49885 (latetest updates)
        return self.board.fen()

    def handle_message(self, intent_result: Dict) -> Dict:
        """Main entry point for processing messages"""
        intent = intent_result["intent"]
        message = intent_result["message"]
        move = intent_result.get("move")

        # Handle game management first
        if intent == "request_game":
            self._reset_game()
            return {
                "status": "success",
                "message": "Let's play! I'll be black.",
                "moves": []
            }

        if intent == "quit_game":
            self.game_in_progress = False
            return {
                "status": "success",
                "message": "Game ended. Thanks for playing!",
                "moves": self.move_history
            }

        # Check if game is in progress for other intents
        if not self.game_in_progress:
            return {
                "status": "error",
                "message": "No game in progress. Type 'play' to start.",
                "moves": []
            }

        # Handle different intents
        if intent == "make_move" and move:
            return self._handle_move(message, move)
        elif intent == "ask_explanation":
            return self._handle_explanation(message)
        elif intent == "general_chat":
            return self._handle_chat(message)
        else:
            return self._handle_unknown(message)

    def _handle_move(self, message: str, move: str) -> Dict:
        """Handle move intent"""
        if not self._make_move(move):
            return {
                "status": "error",
                "message": "Invalid move.",
                "moves": self.move_history
            }

        # Get Maia's response
        maia_move = self._get_maia_move()

        # If it's just a move without question, don't add commentary
        if self.prompt_maker._is_lone_move(message):
            return {
                "status": "success",
                "message": f"{move}. Maia plays {maia_move}.",
                "moves": self.move_history
            }

        # Get analysis if user asked something with the move
        prompt = self.prompt_maker.create_move_prompt(
            user_move=move,
            maia_move=maia_move,
            board=self.board,
            user_message=message
        )

        if prompt:
            analysis = model_manager.quick_response(prompt)
            return {
                "status": "success",
                "message": f"{move}. Maia plays {maia_move}. {analysis}",
                "moves": self.move_history
            }

        return {
            "status": "success",
            "message": f"{move}. Maia plays {maia_move}.",
            "moves": self.move_history
        }

    def _handle_explanation(self, message: str) -> Dict:
        """Handle explanation requests"""
        prompt = self.prompt_maker.create_chat_prompt(
            board=self.board,
            user_message=message
        )
        response = model_manager.quick_response(prompt)
        return {
            "status": "success",
            "message": response,
            "moves": self.move_history
        }

    def _handle_chat(self, message: str) -> Dict:
        """Handle general chat"""
        prompt = self.prompt_maker.create_chat_prompt(
            board=self.board,
            user_message=message
        )
        response = model_manager.quick_response(prompt)
        return {
            "status": "success",
            "message": response,
            "moves": self.move_history
        }

    def _handle_unknown(self, message: str) -> Dict:
        """Handle unknown intents"""
        return {
            "status": "error",
            "message": "I didn't understand that. Could you rephrase?",
            "moves": self.move_history
        }

    def _make_move(self, move_san: str) -> bool:
        """Make a move on the board"""
        try:
            move = self.board.parse_san(move_san)
            if move in self.board.legal_moves:
                self.board.push(move)
                self.move_history.append(move_san)
                return True
            return False
        except ValueError:
            return False

    def _get_maia_move(self) -> str:
        """Get and make Maia's move"""
        move = self.maia_engine.get_best_move(self.board)
        san_move = self.board.san(move)
        self.board.push(move)
        self.move_history.append(san_move)
        return san_move

    def _reset_game(self):
        """Reset the game state"""
        self.board.reset()
        self.move_history.clear()
<<<<<<< HEAD
        self.game_in_progress = True
=======

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
>>>>>>> parent of de49885 (latetest updates)

    def close(self):
        """Clean up resources"""
        self.maia_engine.close()

    def __del__(self):
        self.close()