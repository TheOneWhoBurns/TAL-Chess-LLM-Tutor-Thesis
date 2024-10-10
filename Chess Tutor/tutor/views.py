# tutor/views.py

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import chess

from .llm_integration import get_llm_response
from .maia_integration import get_maia_move

def chat_view(request):
    return render(request, 'tutor/chat.html')

@csrf_exempt
@require_http_methods(["POST"])
def chess_tutor_api(request):
    try:
        data = json.loads(request.body)
        user_input = data.get('user_input', '')
        current_fen = data.get('fen', '')

        board = chess.Board(current_fen)

        # Interpret the user's move
        user_move_uci = interpret_move(user_input, board)

        # Validate and apply the user's move
        try:
            user_move = chess.Move.from_uci(user_move_uci)
            if user_move not in board.legal_moves:
                return JsonResponse({'error': 'Illegal move'}, status=400)
            board.push(user_move)
        except ValueError:
            return JsonResponse({'error': 'Invalid move format'}, status=400)

        # Get Maia's move
        maia_move = get_maia_move(board.fen())
        if maia_move:
            maia_chess_move = chess.Move.from_uci(maia_move)
            if maia_chess_move in board.legal_moves:
                board.push(maia_chess_move)
            else:
                return JsonResponse({'error': 'Maia suggested an illegal move'}, status=500)
        else:
            return JsonResponse({'error': 'Failed to get move from Maia'}, status=500)

        # Generate LLM response
        llm_prompt = (f"As a chess tutor, analyze this position:\n"
                      f"User's last move: {user_move_uci}\n"
                      f"Maia's response: {maia_move}\n"
                      f"Current board state (FEN): {board.fen()}\n"
                      f"Provide a brief analysis of the moves and some advice for the user.")
        llm_response = get_llm_response(llm_prompt)

        return JsonResponse({
            'tutor_response': llm_response,
            'maia_move': maia_move,
            'new_fen': board.fen()
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def interpret_move(move_input, board):
    if is_uci_move(move_input):
        return move_input
    else:
        llm_prompt = f"Given the chess position FEN: {board.fen()}\n" \
                     f"Interpret the following chess move: '{move_input}'.\n" \
                     f"Respond with only the UCI notation."
        return get_llm_response(llm_prompt).strip()

def is_uci_move(move_str):
    return len(move_str) in (4, 5) and all(c.isalnum() for c in move_str)