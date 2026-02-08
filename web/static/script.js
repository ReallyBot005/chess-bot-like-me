
const chatBox = document.getElementById('chat');
const moveList = document.getElementById('movelist');
const statusBox = document.getElementById('status');
let game = new Chess();
let board = null;
let userColor = 'w'; // default

// History State
let historyStack = [];
let currentHistoryIndex = -1;

// --- Start Screen Logic ---

function showColorSelection() {
    document.getElementById('start-actions').style.display = 'none';
    document.getElementById('color-selection').style.display = 'block';
}

function hideColorSelection() {
    document.getElementById('start-actions').style.display = 'block';
    document.getElementById('color-selection').style.display = 'none';
}

function startGame(color) {
    // Hide Start Screen
    document.getElementById('start-screen').style.display = 'none';

    // Show Game Area
    const gameArea = document.getElementById('game-area');
    gameArea.style.display = 'grid';
    gameArea.classList.add('fade-in');

    // Initialize Game
    // Important: Resize board because it was hidden
    if (board) board.resize();

    newGame(color);
}

function returnToMenu() {
    // Stop game?
    // Show Start Screen
    document.getElementById('game-area').style.display = 'none';
    document.getElementById('start-screen').style.display = 'flex';

    // Reset Start Screen state
    hideColorSelection();
}


// --- UI Helpers ---

function appendChat(text, bot = true) {
    const div = document.createElement('div');
    div.className = `chat-msg ${bot ? 'bot' : 'user'}`;
    div.innerHTML = bot
        ? `<b>ReallyBot:</b> ${text}`
        : `<b>You:</b> ${text}`;
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function pushMove(san) {
    const span = document.createElement('span');
    span.className = 'move-item';
    span.textContent = san;
    moveList.appendChild(span);
    moveList.scrollTop = moveList.scrollHeight;

    // Update history
    historyStack.push(game.fen());
    currentHistoryIndex = historyStack.length - 1;
    updateNavButtons();
}

function setStatus(msg, ok = true) {
    statusBox.textContent = msg;
    statusBox.style.color = ok ? '#c3c3c3' : '#ff6b6b';
}

// --- History Navigation ---

function updateNavButtons() {
    // Buttons: Start, Prev, Next, End
    const btns = document.querySelectorAll('.nav-btn');
    if (btns.length < 4) return;

    const atStart = currentHistoryIndex <= 0;
    const atEnd = currentHistoryIndex >= historyStack.length - 1;

    btns[0].disabled = atStart; // Start
    btns[1].disabled = atStart; // Prev
    btns[2].disabled = atEnd;   // Next
    btns[3].disabled = atEnd;   // End
}

function loadHistoryState(index) {
    if (index < 0 || index >= historyStack.length) return;

    currentHistoryIndex = index;
    const fen = historyStack[index];
    board.position(fen);

    // Optional: reload game state into a temp game object to see checks etc?
    // For now purely visual board update is fine.
    // BUT we must block interaction if not at end.

    updateNavButtons();
}

function navStart() {
    loadHistoryState(0);
}

function navPrev() {
    if (currentHistoryIndex > 0) {
        loadHistoryState(currentHistoryIndex - 1);
    }
}

function navNext() {
    if (currentHistoryIndex < historyStack.length - 1) {
        loadHistoryState(currentHistoryIndex + 1);
    }
}

function navEnd() {
    loadHistoryState(historyStack.length - 1);
}


// --- Chess Logic ---

function removeHighlights() {
    $('#board .square-55d63').removeClass('highlight-source highlight-target');
}

function removeGrayHighlights() {
    $('#board .square-55d63').removeClass('highlight-hint highlight-capture');
}

function highlightMove(source, target) {
    removeHighlights();
    $('#board .square-' + source).addClass('highlight-source');
    $('#board .square-' + target).addClass('highlight-target');
}

function onDragStart(source, piece, position, orientation) {
    // 1. Game over check
    if (game.game_over()) return false;

    // 2. History check: ONLY allow move if we are at the latest state
    if (currentHistoryIndex !== historyStack.length - 1) {
        return false;
    }

    // 3. Color check
    if ((userColor === 'w' && piece.search(/^b/) !== -1) ||
        (userColor === 'b' && piece.search(/^w/) !== -1)) return false;
    if ((userColor === 'w' && game.turn() !== 'w') ||
        (userColor === 'b' && game.turn() !== 'b')) return false;

    // Show legal moves
    const moves = game.moves({
        square: source,
        verbose: true
    });

    if (moves.length === 0) return;

    removeGrayHighlights();
    for (let i = 0; i < moves.length; i++) {
        const move = moves[i];
        if (move.flags.includes('c') || move.flags.includes('e')) {
            $('#board .square-' + move.to).addClass('highlight-capture');
        } else {
            $('#board .square-' + move.to).addClass('highlight-hint');
        }
    }
}

function onDrop(source, target) {
    removeGrayHighlights();

    // Safety check again
    if (currentHistoryIndex !== historyStack.length - 1) return 'snapback';

    let move = game.move({
        from: source,
        to: target,
        promotion: 'q'
    });

    if (move === null) return 'snapback';

    highlightMove(source, target);
    board.position(game.fen());
    pushMove(move.san); // Pushes new FEN to stack

    if (checkGameOver()) return;

    // Send to server
    fetch("/move", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ uci: source + target })
    })
        .then(r => r.json())
        .then(data => {
            if (data.error) {
                alert("Error: " + data.error);
                // revert
                game.undo();
                historyStack.pop();
                currentHistoryIndex--;
                board.position(game.fen());
                return;
            }

            // Human-like delay 400-800ms
            const delay = Math.floor(Math.random() * 400) + 400;

            setTimeout(() => {
                game.load(data.fen);
                board.position(data.fen);

                if (data.bot_move) {
                    highlightMove(data.bot_move.from, data.bot_move.to);
                }
                if (data.bot_san) {
                    pushMove(data.bot_san); // Pushes bot move to stack
                    appendChat(`Played ${data.bot_san}. ${data.bot_chat || ""}`, true);
                }

                checkGameOver();
            }, delay);
        })
        .catch(err => console.error(err));
}

function checkGameOver() {
    if (game.game_over()) {
        let msg = "Game Over: ";
        if (game.in_checkmate()) {
            msg += (game.turn() === 'w' ? "Black" : "White") + " wins by Checkmate!";
        } else if (game.in_draw()) {
            msg += "Draw!";
        } else {
            msg += "Game ended.";
        }
        setStatus(msg, false);
        return true;
    }
    return false;
}

function onSnapEnd() {
    // If we are reviewing history, do NOT snap to game.fen()
    // Snap to the dragged position? No, drag is disabled in history.
    // So if drag happened, we MUST be current.
    board.position(game.fen(), false);
}

// --- Game Control ---

async function newGame(color) {
    userColor = color;
    game.reset(); // reset local chess.js

    // Init History
    historyStack = [game.fen()];
    currentHistoryIndex = 0;
    updateNavButtons();

    // Update board orientation
    if (board) {
        board.orientation(color === 'w' ? 'white' : 'black');
        board.start();
    }

    // Clear UI
    chatBox.innerHTML = "";
    moveList.innerHTML = "";
    removeHighlights();
    removeGrayHighlights();
    setStatus("Starting new game...");

    try {
        const res = await fetch('/new', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ color })
        });
        const data = await res.json();

        if (!data.ok) {
            setStatus("Failed to start", false);
            return;
        }

        game.load(data.fen);
        board.position(data.fen);

        // Update history with server start state (might be same)
        historyStack[0] = data.fen;

        if (data.chat) appendChat(data.chat, true);

        // If bot plays first (user selected Black)
        if (data.botSAN) {
            setTimeout(() => {
                pushMove(data.botSAN);
                if (data.botChat) appendChat(data.botChat, true);
                game.load(data.fen);
                board.position(game.fen(), true);
            }, 500);
        }

        setStatus("Your move.");
    } catch (e) {
        console.error(e);
        setStatus("Network error starting game.", false);
    }
}

async function resign() {
    if (game.game_over()) return; // Already over

    try {
        const res = await fetch('/resign', { method: 'POST' });
        const data = await res.json();
        if (data.ok) {
            appendChat(data.chat || "You resigned.", true);
            setStatus("Game Over: " + data.result);
            // game.reset(); 
        }
    } catch (e) {
        console.error(e);
    }
}

// --- Initialization ---

window.onload = function () {
    // NO AUTO START
    // Initialize board but it will be hidden

    board = Chessboard('board', {
        draggable: true,
        position: 'start',
        pieceTheme: '/static/img/chesspieces/{piece}.png',
        onDragStart: onDragStart,
        onDrop: onDrop,
        onSnapEnd: onSnapEnd,
        moveSpeed: 200,
        snapbackSpeed: 200,
        snapSpeed: 100
    });

    // Handle window resize to keep board responsive
    window.addEventListener('resize', () => {
        board.resize();
    });
};
