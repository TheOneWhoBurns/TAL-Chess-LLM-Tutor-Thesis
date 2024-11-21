from typing import List, Dict
import chess
from .maia_engine import MaiaEngine
from .PromptMaker import PromptMaker
from .models import model_manager

class ChessLogicUnit:
    def __init__(self, project_dir=None):
        self.board = chess.Board()
        self.move_history = []
        self.chat_history = []
        if project_dir:
            self.maia_engine = MaiaEngine(project_dir)
        self.game_in_progress = False
        self.prompt_maker = PromptMaker()
        self.player_color = chess.WHITE  # Player is always white

    def get_move_history(self) -> List[str]:
        """Get the history of moves"""
        return self.move_history

    def get_current_position(self) -> str:
        """Get current FEN position"""
        return self.board.fen()

    def _is_player_turn(self) -> bool:
        """Check if it's the player's turn"""
        return self.board.turn == self.player_color

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

        # Handle move intent with turn checking
        if intent == "make_move" and move:
            if not self._is_player_turn():
                return {
                    "status": "error",
                    "message": "It's not your turn yet.",
                    "moves": self.move_history
                }
            return self._handle_move(message, move)

        elif intent == "ask_explanation":
            return self._handle_explanation(message)
        elif intent == "general_chat":
            return self._handle_chat(message)
        else:
            return self._handle_unknown(message)

    def _make_move(self, move_str: str) -> bool:
        """Make a move on the board with improved move parsing"""
        try:
            # Check for same square move
            if len(move_str) >= 4 and move_str[:2] == move_str[2:4]:
                return False

            # Clean up the move string
            move_str = move_str.replace('-', '').strip()

            # Try parsing as SAN first (e4, Nf3 format)
            try:
                move = self.board.parse_san(move_str)
                if move in self.board.legal_moves:
                    self.board.push(move)
                    self.move_history.append(move_str)
                    return True
            except ValueError:
                pass

            # Check for castling notation (O-O or O-O-O)
            if move_str.upper() in ['OO', 'OOO', '00', '000']:
                is_kingside = len(move_str) <= 2
                if is_kingside:
                    castle_move = 'e1g1' if self.board.turn else 'e8g8'
                else:
                    castle_move = 'e1c1' if self.board.turn else 'e8c8'
                try:
                    move = chess.Move.from_uci(castle_move)
                    if move in self.board.legal_moves:
                        san_move = self.board.san(move)
                        self.board.push(move)
                        self.move_history.append(san_move)
                        return True
                except ValueError:
                    pass
                
            # Try parsing as UCI (e2e4 format)
            try:
                move = chess.Move.from_uci(move_str)
                if move in self.board.legal_moves:
                    san_move = self.board.san(move)  # Convert to SAN for history
                    self.board.push(move)
                    self.move_history.append(san_move)
                    return True
            except ValueError:
                pass

            # Special handling for piece moves with ambiguous notation
            if move_str[0].isupper() and len(move_str) >= 3:  # Piece move (e.g., "Nc3")
                piece_symbol = move_str[0].lower()
                if piece_symbol in chess.PIECE_SYMBOLS:
                    piece_type = chess.PIECE_SYMBOLS.index(piece_symbol)

                    # Extract destination square from the move string
                    dest_str = move_str[-2:]  # Last two characters should be the destination
                    try:
                        dest_square = chess.parse_square(dest_str)
                    except ValueError:
                        return False

                    # Find all pieces of the correct type that can move to the destination
                    valid_moves = []
                    for legal_move in self.board.legal_moves:
                        piece = self.board.piece_at(legal_move.from_square)
                        if (piece and
                                piece.piece_type == piece_type and
                                piece.color == self.board.turn and
                                legal_move.to_square == dest_square):
                            valid_moves.append(legal_move)

                    # If we found exactly one valid move, make it
                    if len(valid_moves) == 1:
                        move = valid_moves[0]
                        san_move = self.board.san(move)  # Convert to SAN for history
                        self.board.push(move)
                        self.move_history.append(san_move)
                        return True

            return False

        except (ValueError, AttributeError) as e:
            print(f"Move error: {str(e)}")
            return False

    def _handle_move(self, message: str, move: str) -> Dict:
        """Handle move intent"""
        # Check for same square move
        if len(move) >= 4 and move[:2] == move[2:4]:
            return {
                "status": "ignore",
                "message": "",
                "moves": self.move_history
            }

        if not self._make_move(move):
            return {
                "status": "error",
                "message": "Invalid move.",
                "moves": self.move_history
            }

        # Get Maia's response
        maia_move = self.maia_engine.get_best_move(self.board)
        san_response = self.board.san(maia_move)  # Convert Move object to SAN
        self.board.push(maia_move)
        self.move_history.append(san_response)

        # If it's just a move without question, don't add commentary
        if self.prompt_maker._is_lone_move(message):
            response_msg = f"{move}. Maia plays {san_response}."
            self.chat_history.append({"role": "user", "content": message})
            self.chat_history.append({"role": "assistant", "content": response_msg})
            return {
                "status": "success",
                "message": response_msg,
                "moves": self.move_history
            }

        # Get analysis if user asked something with the move
        prompt = self.prompt_maker.create_move_prompt(
            user_move=move,
            maia_move=san_response,
            move_history=self.move_history,
            chat_history=self.chat_history,
            user_message=message
        )

        if prompt:
            analysis = model_manager.quick_response(prompt)
            self.chat_history.append({"role": "user", "content": message})
            self.chat_history.append({"role": "assistant", "content": analysis})
            return {
                "status": "success",
                "message": analysis,
                "moves": self.move_history
            }

        response_msg = f"{move}. Maia plays {san_response}."
        self.chat_history.append({"role": "user", "content": message})
        self.chat_history.append({"role": "assistant", "content": response_msg})
        return {
            "status": "success",
            "message": response_msg,
            "moves": self.move_history
        }

    def _handle_explanation(self, message: str) -> Dict:
        """Handle explanation requests"""
        prompt = self.prompt_maker.create_chat_prompt(
            move_history=self.move_history,
            chat_history=self.chat_history,
            user_message=message
        )
        response = model_manager.quick_response(prompt)
        self.chat_history.append({"role": "user", "content": message})
        self.chat_history.append({"role": "assistant", "content": response})
        return {
            "status": "success",
            "message": response,
            "moves": self.move_history
        }

    def _handle_chat(self, message: str) -> Dict:
        """Handle general chat"""
        prompt = self.prompt_maker.create_chat_prompt(
            move_history=self.move_history,
            chat_history=self.chat_history,
            user_message=message
        )
        response = model_manager.quick_response(prompt)
        self.chat_history.append({"role": "user", "content": message})
        self.chat_history.append({"role": "assistant", "content": response})
        return {
            "status": "success",
            "message": response,
            "moves": self.move_history
        }

    def _reset_game(self):
        """Reset the game state"""
        self.board.reset()
        self.move_history.clear()
        self.chat_history.clear()  # Clear chat history when starting new game
        self.game_in_progress = True
        self.player_color = chess.WHITE  # Reset player color

    def _handle_unknown(self, message: str) -> Dict:
        """Handle unknown intents"""
        return {
            "status": "error",
            "message": "I didn't understand that. Could you rephrase?",
            "moves": self.move_history
        }

    def close(self):
        """Clean up resources"""
        if hasattr(self, 'maia_engine'):
            self.maia_engine.close()

    def __del__(self):
        self.close()