
import sys
import os

# Add web directory to path so we can import bot_core
sys.path.append(os.path.abspath("web"))

try:
    from bot_core import BotGame
    print("Import successful")
    
    game = BotGame()
    print("BotGame initialized")
    
    print(f"Style loaded: {game.style}")
    print(f"Book loaded keys count: {len(game.book)}")
    
    # Check if style has expected keys
    if "blunder_chance" in game.style:
        print(f"Blunder chance: {game.style['blunder_chance']}")
    else:
        print("WARNING: blunder_chance not found in style")

    print("Verification passed!")

except Exception as e:
    print(f"Verification failed: {e}")
    sys.exit(1)
