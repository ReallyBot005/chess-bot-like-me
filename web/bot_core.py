import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# web/bot_core.py
import chess, chess.engine, chess.pgn, json, random
from datetime import datetime
from src.engine_wrapper import EngineWrapper

BLUNDER_RATE = 0.01

TRASH_TALK = {
    "engine": ["That’s theory, buddy 😎", "Solid move, I learned that from you!",
               "This is peak Suraj aka ReallyBot prep 🍳", "Bet you didn’t expect me to pull this off!"],
    "blunder": ["Oops… classic me 🤦", "Hehe, that was intentional… maybe.",
                "Lmao that’s exactly how I lose my games 😂"],
    "your_blunder": ["Bruh, did you really just play that?", "Oh, that’s a gift, thanks 🎁",
                     "Thanks for the free pawn 😏"],
    "check": ["Check! 🔔", "Careful, king in trouble 👑", "Knock knock… mate’s coming 😉"],
    "random": ["You trained me too well!", "I should be streaming this 😂",
               "Yo this feels like hostel blitz night 💡"]
}

def say(category):
    if category in TRASH_TALK and random.random() < 0.9:
        return random.choice(TRASH_TALK[category])
    return None

# Move DB path
MOVE_DB_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "move_db.json")

def load_move_db():
    if os.path.exists(MOVE_DB_FILE):
        with open(MOVE_DB_FILE, "r") as f:
            return json.load(f)
    return {}

def save_move_db(move_db):
    with open(MOVE_DB_FILE, "w") as f:
        json.dump(move_db, f, indent=2)

class BotGame:
    def __init__(self, user_is_white=True):
        self.board = chess.Board()
        self.user_is_white = user_is_white
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.eng = EngineWrapper(os.path.join(base_dir, "config.json"))

        self.move_db = load_move_db()
        self.game = chess.pgn.Game()
        self.node = self.game

    # -------------------------------
    # start new game
    # -------------------------------
    def new_game(self, color):
        self.board.reset()
        self.user_is_white = (color == "w")
        self.game = chess.pgn.Game()
        self.node = self.game

        chat = f"Game started! You’re playing {'White' if color == 'w' else 'Black'}."
        bot_san, bot_chat = None, None

        # if bot is white, it moves first
        if color == "b":
            bot_san, fen, bot_chat = self.bot_move()
            return fen, chat, bot_san, bot_chat

        return self.board.fen(), chat, None, None

    # -------------------------------
    # handle a user move
    # -------------------------------
    def make_move(self, uci):
        ok, msg = self.user_move(uci)
        if not ok:
            return None, msg, None, None

        # if game ends after user move
        if self.board.is_game_over():
            res, chat = self.end_game()
            return self.board.fen(), chat, None, None

        # bot replies
        bot_san, fen, bot_chat = self.bot_move()
        return fen, f"You played {uci}", bot_san, bot_chat

    # -------------------------------
    def user_move(self, uci):
        try:
            move = chess.Move.from_uci(uci)
            if move not in self.board.legal_moves:
                return False, "Illegal move"
            self.board.push(move)
            self.node = self.node.add_variation(move)
            return True, None
        except:
            return False, "Invalid move"

    def bot_move(self):
        move = None
        fen = self.board.fen()

        # try mimic DB
        if fen in self.move_db and random.random() > BLUNDER_RATE:
            san_moves = list(self.move_db[fen].keys())
            try:
                move = self.board.parse_san(random.choice(san_moves))
            except:
                pass

        # else engine / blunder
        if move is None:
            if random.random() < BLUNDER_RATE:
                move = random.choice(list(self.board.legal_moves))
                chat = say("blunder")
            else:
                result = self.eng.play(self.board, chess.engine.Limit(time=self.eng.config["time_limit"]))
                move = result.move
                chat = say("engine")
        else:
            chat = say("engine")

        # ✅ FIX: get SAN before pushing the move
        san = self.board.san(move)
        self.board.push(move)
        self.node = self.node.add_variation(move)

        if self.board.is_check():
            chat = say("check")
        elif random.random() < 0.1:
            chat = say("random")

        return san, self.board.fen(), chat

    def end_game(self, resigned=False):
        res = "*"
        chat = None
        if resigned:
            res = "0-1" if self.user_is_white else "1-0"
            chat = "Running away already? 😂"
        elif self.board.is_checkmate():
            res = "0-1" if self.board.turn == chess.WHITE else "1-0"
            chat = "EZ clap. Thanks for playing 😎"
        elif self.board.is_stalemate() or self.board.is_insufficient_material():
            res = "1/2-1/2"
            chat = "Draw? Boring, but I’ll take it 😴"

        self.game.headers["Result"] = res
        filename = f"game_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pgn"
        with open(filename, "w", encoding="utf-8") as f:
            print(self.game, file=f)

        self._update_db()
        return res, chat

    def _update_db(self):
        board = self.game.board()
        for move in self.game.mainline_moves():
            san = board.san(move)
            fen = board.fen()
            self.move_db.setdefault(fen, {})
            self.move_db[fen][san] = self.move_db[fen].get(san, 0) + 1
            board.push(move)
        save_move_db(self.move_db)

    # -------------------------------
    # resign shortcut
    # -------------------------------
    def resign(self):
        res, chat = self.end_game(resigned=True)
        return res, chat
