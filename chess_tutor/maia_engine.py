import chess
import chess.engine
import os
import subprocess

class MaiaEngine:
    def __init__(self, project_dir):
        self.project_dir = project_dir
        self.weights_dir = os.path.join(project_dir, "maia-chess", "maia_weights")
        self.engine_path = self._get_lc0_path()
        self.engine = None
        self._load_engine()

    def _get_lc0_path(self):
        try:
            return subprocess.check_output(["which", "lc0"]).decode().strip()
        except subprocess.CalledProcessError:
            raise RuntimeError("lc0 not found in PATH. Make sure it's installed correctly.")

    def _load_engine(self):
        weights_file = "maia-1500.pb.gz"
        weights_path = os.path.join(self.weights_dir, weights_file)
        if not os.path.exists(weights_path):
            raise FileNotFoundError(f"Maia 1500 weights not found at {weights_path}")

        self.engine = chess.engine.SimpleEngine.popen_uci([
            self.engine_path,
            f"--weights={weights_path}"
        ])

    def get_best_move(self, board, time_limit=1.0):
        """
        Get the best move for the given board position using Maia 1500.

        Args:
        board (chess.Board): The current board position
        time_limit (float): Time limit for the engine to think, in seconds

        Returns:
        chess.Move: The best move according to Maia 1500
        """
        if not self.engine:
            raise RuntimeError("Engine not initialized")

        result = self.engine.play(board, chess.engine.Limit(time=time_limit))
        return result.move

    def close(self):
        """
        Close the engine process.
        """
        if self.engine:
            self.engine.quit()
            self.engine = None

    def __del__(self):
        self.close()