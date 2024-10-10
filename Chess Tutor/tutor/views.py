# views.py

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
import chess
from .llm_integration import get_llm_response
from .maia_integration import get_maia_move

@csrf_exempt
@require_http_methods(["POST"])
def chess_tutor(request):
    try:
        # Parse the request data
        data = json.loads(request.body)
        user_input = data.get('user_input', '')
        current_fen = data.get('fen', '')

        # Create a chess board from the current FEN
        board = chess.Board(current_fen)

        # Generate LLM response to user input
        llm_prompt = f"User: {user_input}\nAssistant: As a chess tutor, I'll analyze your move and provide feedback. Let me check with the chess engine."
        llm_response = get_llm_response(llm_prompt)

        # Get Maia's move
        maia_move = get_maia_move(current_fen)

        # Generate final response
        final_prompt = f"{llm_response} The chess engine suggests the move {maia_move}. Let me explain this move and provide some advice."
        final_response = get_llm_response(final_prompt)

        return JsonResponse({
            'tutor_response': final_response,
            'maia_move': maia_move
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)