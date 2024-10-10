// static/js/chat.js
$(document).ready(function() {
    var board = null;
    var game = new Chess();
    var $chatBox = $('#chat-box');
    var $userInput = $('#user-input');
    var $chatForm = $('#chat-form');
    var $processing = $('.processing');

    function onDragStart (source, piece, position, orientation) {
        if (game.game_over()) return false;
        if (piece.search(/^b/) !== -1) return false;
    }

    function onDrop (source, target) {
        var move = game.move({
            from: source,
            to: target,
            promotion: 'q'
        });

        if (move === null) return 'snapback';

        // Send the move to the server
        sendMove(source + target);

        updateStatus();
    }

    function updateStatus () {
        var status = '';
        var moveColor = 'White';
        if (game.turn() === 'b') {
            moveColor = 'Black';
        }

        if (game.in_checkmate()) {
            status = 'Game over, ' + moveColor + ' is in checkmate.';
        } else if (game.in_draw()) {
            status = 'Game over, drawn position';
        } else {
            status = moveColor + ' to move';
            if (game.in_check()) {
                status += ', ' + moveColor + ' is in check';
            }
        }

        $chatBox.append('<p><strong>Status:</strong> ' + status + '</p>');
        $chatBox.scrollTop($chatBox[0].scrollHeight);
    }

    var config = {
        draggable: true,
        position: 'start',
        onDragStart: onDragStart,
        onDrop: onDrop
    };
    board = Chessboard('chess-board', config);

    function sendMove(move) {
        $processing.show();
        console.log("Sending move:", move); // Debug log
        $.ajax({
            url: '/api/chess-tutor/',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                user_input: move,
                fen: game.fen()
            }),
            success: function(response) {
                console.log("Received response:", response); // Debug log
                $chatBox.append('<p><strong>You:</strong> ' + move + '</p>');
                $chatBox.append('<p><strong>Tutor:</strong> ' + response.tutor_response + '</p>');
                $chatBox.append('<p><strong>Maia:</strong> ' + response.maia_move + '</p>');

                game.move(response.maia_move);
                board.position(game.fen());
                updateStatus();

                $chatBox.scrollTop($chatBox[0].scrollHeight);
                $processing.hide();
            },
            error: function(xhr, status, error) {
                console.error("AJAX error:", status, error); // Debug log
                $chatBox.append('<p><strong>Error:</strong> ' + error + '</p>');
                $chatBox.scrollTop($chatBox[0].scrollHeight);
                $processing.hide();
            }
        });
    }

    $chatForm.submit(function(e) {
        e.preventDefault();
        var userInput = $userInput.val().trim();
        if (userInput) {
            console.log("Form submitted with input:", userInput); // Debug log
            sendMove(userInput);
            $userInput.val('');
        }
    });

    updateStatus();
});