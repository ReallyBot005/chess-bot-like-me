import chess.engine
import json


class EngineWrapper:
    def __init__(self, config_path):
        # Load configuration (engine path, time limit, etc.)
        with open(config_path, encoding="utf-8") as f:
            self.config = json.load(f)

        # Start the chess engine (Stockfish or whichever UCI engine is set)
        self.engine = chess.engine.SimpleEngine.popen_uci(self.config["engine_path"])

    def play(self, board, limit):
        """Play a move on the given board with the given limit (time/depth)."""
        return self.engine.play(board, limit)

    def quit(self):
        """Close the engine process cleanly."""
        self.engine.quit()
