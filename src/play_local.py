import chess
import chess.engine
import chess.pgn
import json
import random
import os
from datetime import datetime
from engine_wrapper import EngineWrapper
from colorama import Fore, Style, init
import winsound

# Init colorama for colors
init(autoreset=True)

# --- Settings ---
BLUNDER_RATE = 0.01  # 15% chance bot makes a blunder

# Trash talk messages (merged Suraj + casual style)
TRASH_TALK = {
    "engine": [
        "That’s theory, buddy 😎",
        "Solid move, I learned that from you!",
        "This is peak Suraj aka ReallyBot prep 🍳",
        "Bet you didn’t expect me to pull this off!"
    ],
    "blunder": [
        "Oops… classic me 🤦",
        "Hehe, that was intentional… maybe.",
        "Lmao that’s exactly how I lose my games 😂"
    ],
    "your_blunder": [
        "Bruh, did you really just play that?",
        "Oh, that’s a gift, thanks 🎁",
        "Thanks for the free pawn 😏"
    ],
    "check": [
        "Check! 🔔",
        "Careful, king in trouble 👑",
        "Knock knock… mate’s coming 😉"
    ],
    "random": [
        "You trained me too well!",
        "I should be streaming this 😂",
        "Yo this feels like hostel blitz night 💡"
    ]
}

def say(category):
    if category in TRASH_TALK and random.random() < 0.9:  # 90% chance
        msg = random.choice(TRASH_TALK[category])
        print(Fore.CYAN + "💬 ReallyBot:" + Style.RESET_ALL, msg)

# --- Move database handling ---
MOVE_DB_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "move_db.json")

def load_move_db():
    if os.path.exists(MOVE_DB_FILE):
        with open(MOVE_DB_FILE, "r") as f:
            return json.load(f)
    return {}

def save_move_db(move_db):
    with open(MOVE_DB_FILE, "w") as f:
        json.dump(move_db, f, indent=2)

def choose_from_db(board, move_db):
    fen = board.fen()
    if fen in move_db:
        moves = []
        for move, count in move_db[fen].items():
            moves.extend([move] * count)
        return random.choice(moves)
    return None

def update_db_from_game(game, move_db):
    board = game.board()
    for move in game.mainline_moves():
        move_san = board.san(move)
        fen = board.fen()
        move_db.setdefault(fen, {})
        move_db[fen][move_san] = move_db[fen].get(move_san, 0) + 1
        board.push(move)

# --- Main game loop ---
def main():
    config_path = "config.json"
    eng = EngineWrapper(config_path)
    move_db = load_move_db()

    board = chess.Board()
    game = chess.pgn.Game()
    game.setup(board)
    node = game

    print(Fore.GREEN + "🎉 Game started! Type moves in UCI format (e2e4, g1f3, etc.)")
    print(Fore.YELLOW + "Type 'resign' or 'quit' to exit anytime.\n")

    color_choice = input("Do you want to play as White or Black? (w/b): ").strip().lower()
    user_is_white = (color_choice == "w")

    print(Fore.CYAN + "💬 ReallyBot:" + Style.RESET_ALL, "Ready to lose? Let’s go! 😎\n")

    resigned = False

    # Bot moves first if you chose Black
    if not user_is_white:
        node = bot_move(board, eng, move_db, node)

    try:
        while not board.is_game_over():
            if (board.turn == chess.WHITE and user_is_white) or (board.turn == chess.BLACK and not user_is_white):
                # --- Your move ---
                user_move = input(Fore.YELLOW + "\nYour move: ").strip().lower()

                if user_move in ["quit", "resign"]:
                    print(Fore.RED + "You resigned. Game over.")
                    resigned = True
                    break

                try:
                    move = chess.Move.from_uci(user_move)
                    if move in board.legal_moves:
                        board.push(move)
                        node = node.add_variation(move)
                        winsound.Beep(800, 120)  # tick sound for your move
                    else:
                        print(Fore.RED + "Illegal move, try again.")
                        continue
                except:
                    print(Fore.RED + "Invalid input. Use UCI like 'e2e4'.")
                    continue

                print(Fore.GREEN + "\nBoard after your move:")
                print(board)
            else:
                node = bot_move(board, eng, move_db, node)

        # --- Game outcome ---
        end_game(board, user_is_white, resigned, game)

        # --- Save PGN (safe) ---
        game.headers["Event"] = "Training vs ReallyBot"
        game.headers["Site"] = "Local PC"
        game.headers["Date"] = datetime.now().strftime("%Y.%m.%d")
        game.headers["White"] = "You" if user_is_white else "ReallyBot"
        game.headers["Black"] = "ReallyBot" if user_is_white else "You"

        filename = f"game_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pgn"
        with open(filename, "w", encoding="utf-8") as f:
            try:
                print(game, file=f)
            except Exception as e:
                print(Fore.RED + f"[Warning] Could not fully save PGN: {e}")
                f.write("[Result \"*\"]\n")  # fallback header

        print(Fore.YELLOW + f"\n✅ Game saved as {filename}")

        # --- Auto-learn ---
        update_db_from_game(game, move_db)
        save_move_db(move_db)
        print(Fore.GREEN + "📚 ReallyBot has learned from this game and updated move_db.json!")

    finally:
        eng.quit()

# --- Bot move logic ---
def bot_move(board, eng, move_db, node):
    move = None
    user_like_move = choose_from_db(board, move_db)

    if user_like_move and random.random() > BLUNDER_RATE:
        try:
            move = board.parse_san(user_like_move)
            print(Fore.MAGENTA + f"\nBot (imitating you) plays: {user_like_move}")
        except:
            pass

    if move is None:
        if random.random() < BLUNDER_RATE:
            move = random.choice(list(board.legal_moves))
            print(Fore.RED + f"\nBot (blunder move!) plays: {board.san(move)}")
            say("blunder")
            winsound.MessageBeep(winsound.MB_ICONHAND)
        else:
            result = eng.play(board, chess.engine.Limit(time=eng.config["time_limit"]))
            move = result.move
            print(Fore.MAGENTA + f"\nBot (engine) plays: {board.san(move)}")
            say("engine")

    board.push(move)
    node = node.add_variation(move)

    if board.is_check():
        say("check")
        winsound.MessageBeep(winsound.MB_ICONASTERISK)
    if random.random() < 0.1:
        say("random")

    print(board)
    return node

# --- End game summary ---
def end_game(board, user_is_white, resigned, game):
    if resigned:
        game.headers["Result"] = "0-1" if user_is_white else "1-0"
        print(Fore.RED + "\nYou resigned. GG.")
        print(Fore.CYAN + "💬 ReallyBot:" + Style.RESET_ALL, "Running away already? 😂")
    elif board.is_checkmate():
        game.headers["Result"] = "0-1" if board.turn == chess.WHITE else "1-0"
        print(Fore.RED + "\nCheckmate!")
        if board.turn == (chess.WHITE if user_is_white else chess.BLACK):
            print(Fore.GREEN + "🎉 You won!")
            print(Fore.CYAN + "💬 ReallyBot:" + Style.RESET_ALL, "Ok ok… you got me this time 😅")
        else:
            print(Fore.RED + "💀 ReallyBot wins!")
            print(Fore.CYAN + "💬 ReallyBot:" + Style.RESET_ALL, "EZ clap. Thanks for playing 😎")
        winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
    elif board.is_stalemate():
        game.headers["Result"] = "1/2-1/2"
        print(Fore.BLUE + "\nStalemate!")
        print(Fore.CYAN + "💬 ReallyBot:" + Style.RESET_ALL, "Draw? Boring, but I’ll take it 😴")
    elif board.is_insufficient_material():
        game.headers["Result"] = "1/2-1/2"
        print(Fore.BLUE + "\nDraw: insufficient material.")
    else:
        game.headers["Result"] = "*"
        print(Fore.YELLOW + "\nGame over.")

if __name__ == "__main__":
    main()
