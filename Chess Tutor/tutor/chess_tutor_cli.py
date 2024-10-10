
import requests
import json
import chess

API_URL = "http://localhost:8000/api/chess-tutor/"

def send_move(user_input, fen):
    payload = {
        "user_input": user_input,
        "fen": fen
    }
    response = requests.post(API_URL, json=payload)
    if response.status_code == 200:
        data = response.json()
        print("Tutor's response:")
        print(data['tutor_response'])
        print(f"\nMaia's suggested move: {data['maia_move']}")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None


def main():
    print("Welcome to the Chess Tutor CLI!")
    print("You can interact with the tutor by describing your moves.")
    print("To quit, type 'quit' or 'exit'.")

    board = chess.Board()

    while True:
        print(f"\nCurrent board:\n{board}")
        user_input = input("\nDescribe your move (or type 'quit' to exit): ")
        if user_input.lower() in ['quit', 'exit']:
            break

        maia_move = send_move(user_input, board.fen())

        if maia_move:
            try:
                user_move = chess.Move.from_uci(input("Enter your move in UCI format (e.g., e2e4): "))
                if user_move in board.legal_moves:
                    board.push(user_move)
                    maia_chess_move = chess.Move.from_uci(maia_move)
                    board.push(maia_chess_move)
                else:
                    print("Invalid move. Please try again.")
            except ValueError:
                print("Invalid move format. Please use UCI format (e.g., e2e4).")

    print("Thank you for using the Chess Tutor CLI!")

if __name__ == "__main__":
    main()
