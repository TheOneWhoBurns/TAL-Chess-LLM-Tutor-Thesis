# views.py
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os

from .intent import categorize_intent, intent_classifier
from .ChessLogic import ChessLogicUnit
<<<<<<< HEAD
from .PromptMaker import PromptMaker
from .models import model_manager

current_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(current_dir)
chess_logic = ChessLogicUnit(project_dir)
prompt_maker = PromptMaker()
=======

chess_logic = ChessLogicUnit()
>>>>>>> parent of de49885 (latetest updates)

def chat_view(request):
    return render(request, 'chat.html')

@csrf_exempt
def send_message(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        message = data.get('message', '')

<<<<<<< HEAD
            # Update intent classifier's board state
            intent_classifier.update_board(chess_logic.board)

            # Get intent result and original message
            intent_result = intent_classifier.classify(message)

            # Add original message to intent result for context
            intent_result["message"] = message

            # Process through chess logic
            response = chess_logic.handle_message(intent_result)

            return JsonResponse({
                'response': response["message"],
                'status': response["status"],
                'moves': response["moves"],
                'fen': chess_logic.get_current_position()
            })

        except Exception as e:
            print(f"Error in send_message: {str(e)}")
            return JsonResponse({
                'response': "I apologize, but I encountered an error.",
                'status': "error",
                'moves': chess_logic.get_move_history(),
                'fen': chess_logic.get_current_position()
            })

    return JsonResponse({'error': 'Invalid request method'}, status=400)
=======
        response = process_message(message)

        return JsonResponse({'response': response})
    return JsonResponse({'error': 'Invalid request method'}, status=400)

def process_message(message):
    intent_result = categorize_intent(message)
    predicted_intent = intent_result["intent"]
    confidence_score = intent_result["confidence"]
    extracted_move = intent_result["move"]

    response = chess_logic.handle_intent(predicted_intent, extracted_move)

    if response["status"] == "success":
        return response["message"]
    else:
        return f"Error: {response['message']} (Intent: {predicted_intent}, Confidence: {confidence_score:.2f})"
>>>>>>> parent of de49885 (latetest updates)
