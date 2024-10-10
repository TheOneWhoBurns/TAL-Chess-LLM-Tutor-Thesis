# chess_tutor_cli.py

import requests
import json
import chess

API_URL = "http://localhost:8000/api/chess-tutor/"

def send_move(user_input, fen):
    payload = {
        "user_input": user_input,
        "fen": fen
    }
    try:
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error communicating with the server: {e}")
        return None

def display_board(board):
    print("\nCurrent board state:")
    print(board)
    print("\n" + "="*40)  # Separator for clarity

def main():
    print("Welcome to the Chess Tutor CLI!")
    print("You can interact with the tutor by describing your moves or using UCI notation.")
    print("Type 'board' to see the current board state.")
    print("Type 'quit' or 'exit' to end the game.")
    print("\n" + "="*40 + "\n")  # Separator for clarity

    board = chess.Board()
    move_history = []

    while True:
        display_board(board)
        user_input = input("\nEnter your move, 'board', or 'quit': ").strip().lower()

        if user_input in ['quit', 'exit']:
            break
        elif user_input == 'board':
            continue

        response = send_move(user_input, board.fen())

        if response:
            if 'error' in response:
                print(f"Error: {response['error']}")
                continue

            tutor_response = response['tutor_response']
            maia_move = response['maia_move']
            new_fen = response['new_fen']

            # Update move history
            move_history.append({
                'user_move': user_input,
                'tutor_response': tutor_response,
                'maia_move': maia_move
            })

            print("\nTutor's response:")
            print(tutor_response)
            print(f"\nMaia's move: {maia_move}")

            # Update the board state
            board = chess.Board(new_fen)

            # Print move history
            print("\nMove history:")
            for i, move in enumerate(move_history, 1):
                print(f"Turn {i}:")
                print(f"  Your move: {move['user_move']}")
                print(f"  Maia's move: {move['maia_move']}")
                print(f"  Tutor's advice: {move['tutor_response'][:100]}...")  # Truncate long responses
                print()

        else:
            print("Failed to get a response from the server. Please try again.")

    print("Thank you for using the Chess Tutor CLI!")

if __name__ == "__main__":
    main()