import chess
import chess.engine
import json
import os
import platform
import random


class EngineWrapper:
    def __init__(self, config_path):
        with open(config_path, encoding="utf-8") as f:
            self.config = json.load(f)

        self.use_fallback = False
        self.engine = None

        system = platform.system().lower()

        # 🚀 RENDER / LINUX → fallback engine
        if system == "linux":
            print("⚠️ Stockfish disabled on Render. Using fallback engine.")
            self.use_fallback = True
            return

        # 💻 WINDOWS / LOCAL → Stockfish
        engine_path = self.config.get("engine_path")
        if not engine_path or not os.path.exists(engine_path):
            raise FileNotFoundError(
                f"Invalid engine_path in config.json: {engine_path}"
            )

        self.engine = chess.engine.SimpleEngine.popen_uci(engine_path)
        self._configure_engine()

    def _configure_engine(self):
        if not self.engine:
            return

        options = {}

        if "skill_level" in self.config:
            options["Skill Level"] = int(self.config["skill_level"])

        if "uci_elo" in self.config:
            options["UCI_LimitStrength"] = True
            options["UCI_Elo"] = int(self.config["uci_elo"])

        if options:
            self.engine.configure(options)

    def play(self, board, limit):
        # 🎯 Fallback: random legal move
        if self.use_fallback:
            moves = list(board.legal_moves)
            return chess.engine.PlayResult(random.choice(moves), None)

        return self.engine.play(board, limit)

    def quit(self):
        if self.engine:
            self.engine.quit()
