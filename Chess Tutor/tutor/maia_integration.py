# maia_integration.py

import chess
import chess.engine
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MaiaBot:
    def __init__(self, weights_path, lc0_path='lc0'):
        self.weights_path = weights_path
        self.lc0_path = lc0_path
        self.engine = None

    def start(self):
        if not self.engine:
            command = [self.lc0_path, f"--weights={self.weights_path}"]
            try:
                logger.info(f"Starting Maia engine with command: {' '.join(command)}")
                self.engine = chess.engine.SimpleEngine.popen_uci(command)
                logger.info("Maia engine started successfully")
            except Exception as e:
                logger.error(f"Error starting Maia engine: {e}")
                raise

    def get_move(self, board):
        if not self.engine:
            self.start()
        try:
            logger.info(f"Getting move for position: {board.fen()}")
            result = self.engine.play(board, chess.engine.Limit(nodes=1))
            logger.info(f"Maia suggested move: {result.move.uci()}")
            return result.move.uci()
        except Exception as e:
            logger.error(f"Error getting move from Maia: {e}")
            return None

    def quit(self):
        if self.engine:
            logger.info("Shutting down Maia engine")
            self.engine.quit()
            self.engine = None

def get_maia_move(fen):
    board = chess.Board(fen)
    return maia_bot.get_move(board)

# Initialize the Maia bot
weights_path = os.path.join(os.path.dirname(__file__), "maia-1100.pb.gz")
maia_bot = MaiaBot(weights_path)

if __name__ == "__main__":
    # Test the bot
    board = chess.Board()
    move = maia_bot.get_move(board)
    print(f"Maia's move for the starting position: {move}")
    maia_bot.quit()