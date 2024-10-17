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

# Define chess-specific intents
CHESS_INTENTS = ["make_chess_move", "ask_explanation", "request_game", "general_chat", "quit_game"]

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
