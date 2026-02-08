import chess.engine
import json
import os
import platform


class EngineWrapper:
    def __init__(self, config_path):
        with open(config_path, encoding="utf-8") as f:
            self.config = json.load(f)

        engine_path = self._get_engine_path()
        self.engine = chess.engine.SimpleEngine.popen_uci(engine_path)

        self._configure_engine()

    def _get_engine_path(self):
        """
        Windows (local): use engine_path from config.json
        Linux (Render): use system-installed Stockfish
        """

        system = platform.system().lower()

        # 🚀 RENDER / LINUX
        if system == "linux":
            engine_path = "/usr/bin/stockfish"

            if not os.path.exists(engine_path):
                raise FileNotFoundError(
                    "Stockfish not found at /usr/bin/stockfish. "
                    "Ensure it is installed via apt-get on Render."
                )

            return engine_path

        # 💻 LOCAL WINDOWS
        engine_path = self.config.get("engine_path")

        if not engine_path or not os.path.exists(engine_path):
            raise FileNotFoundError(
                f"Invalid engine_path in config.json: {engine_path}"
            )

        return engine_path

    def _configure_engine(self):
        options = {}

        if "skill_level" in self.config:
            options["Skill Level"] = int(self.config["skill_level"])

        if "uci_elo" in self.config:
            options["UCI_LimitStrength"] = True
            options["UCI_Elo"] = int(self.config["uci_elo"])

        if options:
            self.engine.configure(options)

    def play(self, board, limit):
        return self.engine.play(board, limit)

    def quit(self):
        self.engine.quit()
