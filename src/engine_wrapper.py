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

        # ===============================
        # 🚀 RENDER / LINUX
        # ===============================
        if system == "linux":
            base_dir = "/opt/render/project/src"
            engine_dir = os.path.join(base_dir, ".stockfish")
            binary_path = os.path.join(engine_dir, "stockfish")

            if os.path.exists(binary_path):
                return binary_path

            os.makedirs(engine_dir, exist_ok=True)

            print("⬇️ Downloading Stockfish (Linux x86_64)...")

            tar_path = os.path.join(engine_dir, "stockfish.tar.gz")

            subprocess.run(
                [
                    "curl",
                    "-L",
                    "-o",
                    tar_path,
                    "https://github.com/official-stockfish/Stockfish/releases/download/sf_16/stockfish-ubuntu-x86-64-avx2.tar.gz",
                ],
                check=True,
            )

            subprocess.run(
                ["tar", "-xzf", tar_path, "-C", engine_dir],
                check=True,
            )

            # Locate real binary
            for root, _, files in os.walk(engine_dir):
                for f in files:
                    if f.startswith("stockfish") and "." not in f:
                        real_binary = os.path.join(root, f)
                        os.rename(real_binary, binary_path)
                        os.chmod(binary_path, stat.S_IRWXU)
                        return binary_path

            raise RuntimeError("Stockfish binary not found after extraction")

        # ===============================
        # 💻 WINDOWS (LOCAL)
        # ===============================
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
