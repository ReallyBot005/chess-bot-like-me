from flask import Flask, render_template, request, jsonify
from bot_core import BotGame

app = Flask(__name__, template_folder="templates")

game = BotGame()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/new", methods=["POST"])
def new_game():
    data = request.get_json()
    color = data.get("color", "w")
    fen, chat, bot_san, bot_chat = game.new_game(color)
    return jsonify({
        "ok": True,
        "fen": fen,
        "chat": chat,
        "botSAN": bot_san,
        "botChat": bot_chat
    })

@app.route("/move", methods=["POST"])
def move():
    data = request.get_json()
    uci = data.get("uci")

    fen, msg, bot_san, bot_chat = game.make_move(uci)

    if fen is None:
        return jsonify({"ok": False, "error": msg})

    user_move = {"from": uci[0:2], "to": uci[2:4]}  # ✅ user squares

    bot_move = None
    if bot_san:  # ✅ if bot replied
        last_move = game.board.move_stack[-1]  # chess.Move object
        bot_move = {"from": last_move.uci()[0:2], "to": last_move.uci()[2:4]}

    return jsonify({
        "ok": True,
        "fen": fen,
        "chat": msg,
        "bot_san": bot_san,
        "bot_chat": bot_chat,
        "user_move": user_move,
        "bot_move": bot_move
    })


    # NEW: if game ended, include result + chat
    if game.board.is_game_over():
        res, end_chat = game.end_game()
        response["result"] = res
        response["chat"] = end_chat or msg

    return jsonify(response)

@app.route("/resign", methods=["POST"])
def resign():
    result, chat = game.resign()
    return jsonify({"ok": True, "result": result, "chat": chat})

if __name__ == "__main__":
    app.run(debug=True)

