<<<<<<< HEAD
# intent.py
from typing import Dict, Optional
import re
import chess
from .models import model_manager
=======
from transformers import pipeline
import torch
from typing import Dict

# Check if a GPU is available
device = torch.device("cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu")
print(f"Using device: {device}")

# Load pre-trained intent detection model from Hugging Face
intent_pipeline = pipeline('zero-shot-classification',
                           model="facebook/bart-large-mnli",
                           device=device)

# Load pre-trained RoBERTa model from Hugging Face for move extraction
roberta_qa = pipeline("question-answering",
                      model="deepset/roberta-base-squad2",
                      device=device)
>>>>>>> parent of de49885 (latetest updates)

class IntentClassifier:
    INTENTS = [
        "make_move",
        "ask_explanation",
        "request_game",
        "general_chat",
        "quit_game"
    ]

<<<<<<< HEAD
    def __init__(self):
        self._move_patterns = [
            r'\b[NBRQK]?[a-h]?[1-8]?x?[a-h][1-8](?:=[NBRQ])?\+?\#?\b',
            r'\b[NBRQK][a-h1-8][a-h][1-8]\b',
            r'\b[a-h][1-8]\b',
            r'\bO-O(-O)?\b'
        ]
        self._move_regex = re.compile('|'.join(self._move_patterns))
        self.board = chess.Board()

    def classify(self, message: str) -> Dict[str, any]:
        """Classify intent and extract move if present"""
        # Check for move first (fastest)
        move = self.extract_move(message)
        if move and self.validate_move(move):
            return {
                "intent": "make_move",
                "move": move,
                "confidence": 0.9
            }

        # Then use model for intent
        result = model_manager.get_intent(message, self.INTENTS)
        return {
            "intent": result["labels"][0],
            "move": None,
            "confidence": result["scores"][0]
        }

    def extract_potential_moves(self, text: str) -> list[str]:
        """Extract potential chess moves using regex"""
        return [match.group() for match in self._move_regex.finditer(text)]

    def validate_move(self, move: str) -> bool:
        """Check if a move is legal in the current position"""
        try:
            chess_move = self.board.parse_san(move)
            return chess_move in self.board.legal_moves
        except ValueError:
            return False

    def extract_move(self, message: str) -> Optional[str]:
        """Extract and validate chess move from message"""
        potential_moves = self.extract_potential_moves(message)
        legal_moves = [self.board.san(move) for move in self.board.legal_moves]

        for move in potential_moves:
            if move.upper() in [m.upper() for m in legal_moves]:
                return move

        context = f"Legal moves are: {', '.join(legal_moves)}. Message: {message}"
        move = model_manager.extract_move(message, context)

        if move and move.upper() in [m.upper() for m in legal_moves]:
            return move

        return None

    def update_board(self, board: chess.Board):
        """Update the internal board state"""
        self.board = board.copy()

# Global instance
intent_classifier = IntentClassifier()

def categorize_intent(message: str) -> Dict[str, any]:
    """Wrapper for backwards compatibility"""
    return intent_classifier.classify(message)
=======
def extract_move(user_message: str) -> str:
    """
    Extract the chess move from the user's message using the RoBERTa model.

    Args:
    user_message (str): The user's input message.

    Returns:
    str: The extracted move or an error message.
    """
    try:
        # Use the RoBERTa model to extract the move
        question = "What chess move is being described in this message?"
        result = roberta_qa(question=question, context=user_message)

        # The answer might need further processing to ensure it's in proper chess notation
        extracted_move = result['answer'].strip()

        return extracted_move
    except Exception as e:
        return f"Error extracting move: {str(e)}"

def categorize_intent(user_message: str) -> Dict[str, str]:
    """
    Categorize the user's intent and extract the move if applicable.

    Args:
    user_message (str): The user's input message.

    Returns:
    Dict[str, str]: A dictionary containing the predicted intent, confidence score, and extracted move (if applicable).
    """
    predictions = intent_pipeline(user_message, CHESS_INTENTS)
    predicted_intent = predictions["labels"][0]
    confidence_score = predictions["scores"][0]

    if predicted_intent == "make_chess_move":
        extracted_move = extract_move(user_message)
        return {
            "intent": predicted_intent,
            "confidence": confidence_score,
            "move": extracted_move
        }
    else:
        return {
            "intent": predicted_intent,
            "confidence": confidence_score,
            "move": None
        }
>>>>>>> parent of de49885 (latetest updates)
