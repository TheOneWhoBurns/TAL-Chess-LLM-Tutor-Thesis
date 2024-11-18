// No need for React imports since we're using from CDN
const ChessGame = {
    init: function() {
        this.board = null;
        this.game = new Chess();
        this.initBoard();
        this.setupEventListeners();
    },

    initBoard: function() {
        this.board = Chessboard('board', {
            position: 'start',
            draggable: true,
            dropOffBoard: 'snapback',
            pieceTheme: '/static/img/chesspieces/wikipedia/{piece}.png',
            onDrop: this.handleMove.bind(this)
        });

        // Make board responsive
        window.addEventListener('resize', () => {
            if (this.board) {
                this.board.resize();
            }
        });
    },

    setupEventListeners: function() {
        // Set up button handlers
        window.resetGame = this.resetGame.bind(this);
        window.flipBoard = this.flipBoard.bind(this);

        // Listen for server responses
        window.addEventListener('serverResponse', this.handleServerResponse.bind(this));
    },

    handleMove: function(source, target) {
        try {
            const move = this.game.move({
                from: source,
                to: target,
                promotion: 'q'
            });

            if (move === null) return 'snapback';

            // Send move to chat system as UCI format
            const moveStr = `${source}-${target}`;
            // Send the move through chat system just like if it was typed
            const chatForm = document.getElementById('chat-form');
            const userInput = document.getElementById('user-input');
            userInput.value = moveStr;
            // Trigger the form's submit event
            const submitEvent = new Event('submit', {
                bubbles: true,
                cancelable: true,
            });
            chatForm.dispatchEvent(submitEvent);

            return true;
        } catch (err) {
            console.error('Move error:', err);
            return 'snapback';
        }
    },

    handleServerResponse: function(e) {
        const data = e.detail;
        if (data.moves) {
            this.updateMoveHistory(data.moves);
        }
        if (data.fen) {
            this.game.load(data.fen);
            this.board.position(data.fen);
        }
    },

    updateMoveHistory: function(moves) {
        const historyContent = document.querySelector('.history-content');
        if (!historyContent) return;

        historyContent.innerHTML = '';
        for (let i = 0; i < moves.length; i += 2) {
            const moveElement = document.createElement('div');
            moveElement.className = 'move-row';

            let rowHtml = `<span class="move-number">${Math.floor(i/2 + 1)}.</span>`;
            rowHtml += `<span class="white-move">${moves[i]}</span>`;
            if (moves[i + 1]) {
                rowHtml += `<span class="black-move">${moves[i + 1]}</span>`;
            }

            moveElement.innerHTML = rowHtml;
            historyContent.appendChild(moveElement);
        }

        historyContent.scrollTop = historyContent.scrollHeight;
    },

    resetGame: function() {
        this.game.reset();
        this.board.start();
        const resetEvent = new CustomEvent('chessReset');
        window.dispatchEvent(resetEvent);
    },

    flipBoard: function() {
        this.board.flip();
    }
};

// Initialize when DOM is fully loaded
document.addEventListener('DOMContentLoaded', () => {
    // Make sure Chess and Chessboard are available
    if (typeof Chess !== 'undefined' && typeof Chessboard !== 'undefined') {
        ChessGame.init();
    } else {
        console.error('Chess or Chessboard library not loaded');
    }
});