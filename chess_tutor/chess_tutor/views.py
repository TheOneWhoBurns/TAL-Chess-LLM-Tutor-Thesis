from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from .intent import categorize_intent
from .ChessLogic import ChessLogicUnit

chess_logic = ChessLogicUnit()

def chat_view(request):
    return render(request, 'chat.html')

@csrf_exempt
def send_message(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        message = data.get('message', '')

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