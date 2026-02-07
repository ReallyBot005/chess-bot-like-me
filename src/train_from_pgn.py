import os
import chess.pgn
import json
from collections import defaultdict

PGN_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "pgns")
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "move_db.json")

def train_from_pgns():
    move_db = defaultdict(lambda: defaultdict(int))

    for filename in os.listdir(PGN_DIR):
        if filename.endswith(".pgn"):
            filepath = os.path.join(PGN_DIR, filename)
            with open(filepath) as f:
                game = chess.pgn.read_game(f)
                board = game.board()

                for move in game.mainline_moves():
                    move_san = board.san(move)
                    fen = board.fen()
                    move_db[fen][move_san] += 1
                    board.push(move)

    # Save as JSON
    with open(OUTPUT_FILE, "w") as f:
        json.dump(move_db, f, indent=2)

    print(f"Training complete! Learned from {len(os.listdir(PGN_DIR))} PGN files.")
    print(f"Database saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    train_from_pgns()
