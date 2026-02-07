import argparse, json, os
import chess.pgn
from collections import defaultdict, Counter

def build_opening_book(pgn_path, max_plies=16):
    book = defaultdict(Counter)
    games = 0
    with open(pgn_path, encoding="utf-8", errors="ignore") as f:
        while True:
            game = chess.pgn.read_game(f)
            if game is None:
                break
            games += 1
            board = game.board()
            ply = 0
            for mv in game.mainline_moves():
                fen_key = board.fen()  # key BEFORE the move
                san = board.san(mv)
                book[fen_key][san] += 1
                board.push(mv)
                ply += 1
                if ply >= max_plies:
                    break
    # convert counters to sorted lists
    out = {}
    for fen, counter in book.items():
        out[fen] = sorted(
            [{"san": san, "count": cnt} for san, cnt in counter.items()],
            key=lambda x: x["count"], reverse=True
        )
    return out, games

def build_style(pgn_path):
    captures = checks = total = 0
    with open(pgn_path, encoding="utf-8", errors="ignore") as f:
        while True:
            game = chess.pgn.read_game(f)
            if game is None:
                break
            board = game.board()
            for mv in game.mainline_moves():
                san = board.san(mv)
                total += 1
                if "x" in san: captures += 1
                if "+" in san: checks += 1
                board.push(mv)
    cap_ratio = captures / total if total else 0.2
    chk_ratio = checks / total if total else 0.05
    # heuristic style knobs (simple, editable later)
    randomness = min(0.6, 0.15 + 0.7 * chk_ratio)   # more checks → more spice
    blunder = max(0.01, 0.03 - 0.02 * cap_ratio)    # more captures → slightly fewer blunders
    return {
        "randomness": round(randomness, 2),
        "blunder_chance": round(blunder, 3),
        "captures_per_move": round(cap_ratio, 3),
        "checks_per_move": round(chk_ratio, 3),
        "notes": "Heuristic defaults. You can edit these numbers."
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pgn", default=os.path.join("data", "all_games.pgn"))
    ap.add_argument("--out", default="persona")
    ap.add_argument("--plies", type=int, default=16)
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    book, games = build_opening_book(args.pgn, args.plies)
    style = build_style(args.pgn)

    with open(os.path.join(args.out, "opening_book.json"), "w", encoding="utf-8") as f:
        json.dump(book, f)
    with open(os.path.join(args.out, "style.json"), "w", encoding="utf-8") as f:
        json.dump(style, f, indent=2)

    print(f"Built opening book from {games} games → {len(book)} positions.")
    print("Saved persona/opening_book.json and persona/style.json")

if __name__ == "__main__":
    main()
