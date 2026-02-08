import chess.engine
import json
import os
import platform
import subprocess
import stat


class EngineWrapper:
    def __init__(self, config_path):
        with open(config_path, encoding="utf-8") as f:
            self.config = json.load(f)

        engine_path = self._get_engine_path()
        self.engine = chess.engine.SimpleEngine.popen_uci(engine_path)
        self._configure_engine()

    def _get_engine_path(self):
        system = platform.system().lower()

        # 🚀 RENDER / LINUX (download at runtime)
        if system == "linux":
            engine_dir = "/opt/render/project/src/.stockfish"
            engine_path = os.path.join(engine_dir, "stockfish")

            if not os.path.exists(engine_path):
                os.makedirs(engine_dir, exist_ok=True)

                print("⬇️ Downloading Stockfish for Render...")
                subprocess.run(
                    [
                        "curl",
                        "-L",
                        "https://stockfishchess.org/files/stockfish-ubuntu-x86-64-avx2.tar",
                        "-o",
                        f"{engine_dir}/sf.tar",
                    ],
                    check=True,
                )

                subprocess.run(
                    ["tar", "-xf", f"{engine_dir}/sf.tar", "-C", engine_dir],
                    check=True,
                )

                # Find extracted binary
                for root, _, files in os.walk(engine_dir):
                    for f in files:
                        if f.startswith("stockfish") and "." not in f:
                            extracted = os.path.join(root, f)
                            os.rename(extracted, engine_path)
                            break

                os.chmod(engine_path, stat.S_IRWXU)

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
