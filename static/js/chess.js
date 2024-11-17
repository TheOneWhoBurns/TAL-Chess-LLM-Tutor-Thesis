// Initialize React in non-module context
import React from "react";

const { useState, useEffect, useRef } = React;

const ChessTutorInterface = () => {
    const boardRef = useRef(null);
    const gameRef = useRef(null);
    const moveHistoryRef = useRef(null);
    const [moveHistory, setMoveHistory] = useState([]);
    const [position, setPosition] = useState('start');

    useEffect(() => {
        // Initialize chess.js and chessboard
        const Chess = window.Chess;
        const Chessboard = window.Chessboard;

        gameRef.current = new Chess();

        boardRef.current = Chessboard('board', {
            position: 'start',
            draggable: true,
            dropOffBoard: 'snapback',
            pieceTheme: '/static/img/chesspieces/wikipedia/{piece}.png',
            onDrop: handleMove,
            onSnapEnd: updatePosition
        });

        // Make board responsive
        const handleResize = () => {
            if (boardRef.current) {
                boardRef.current.resize();
            }
        };

        window.addEventListener('resize', handleResize);

        // Set up functions on window for button access
        window.resetGame = resetGame;
        window.flipBoard = flipBoard;

        return () => {
            window.removeEventListener('resize', handleResize);
            if (boardRef.current) {
                boardRef.current.destroy();
            }
            // Clean up window functions
            delete window.resetGame;
            delete window.flipBoard;
        };
    }, []);

    // Auto-scroll move history
    useEffect(() => {
        if (moveHistoryRef.current) {
            moveHistoryRef.current.scrollTop = moveHistoryRef.current.scrollHeight;
        }
    }, [moveHistory]);

    const updatePosition = () => {
        setPosition(gameRef.current.fen());
    };

    const handleMove = (source, target, piece, newPos, oldPos, orientation) => {
        try {
            const move = gameRef.current.move({
                from: source,
                to: target,
                promotion: 'q' // always promote to queen for simplicity
            });

            if (move === null) return 'snapback';

            updatePosition();

            // Notify chat system about the move
            const moveStr = `${source}${target}`;
            const moveEvent = new CustomEvent('chessMove', {
                detail: {
                    move: moveStr,
                    fen: gameRef.current.fen(),
                    pgn: gameRef.current.pgn()
                }
            });
            window.dispatchEvent(moveEvent);

            return true;
        } catch (err) {
            console.error('Move error:', err);
            return 'snapback';
        }
    };

    const resetGame = () => {
        gameRef.current.reset();
        boardRef.current.start();
        setMoveHistory([]);
        setPosition('start');
        const resetEvent = new CustomEvent('chessReset');
        window.dispatchEvent(resetEvent);
    };

    const flipBoard = () => {
        boardRef.current.flip();
    };

    // Listen for server responses
    useEffect(() => {
        const handleServerResponse = (e) => {
            const data = e.detail;
            if (data.moves) {
                setMoveHistory(data.moves);
            }
            if (data.fen) {
                gameRef.current.load(data.fen);
                boardRef.current.position(data.fen);
                setPosition(data.fen);
            }
        };

        window.addEventListener('serverResponse', handleServerResponse);
        return () => window.removeEventListener('serverResponse', handleServerResponse);
    }, []);

    return (
        <div className="container">
            <div id="board-section">
                <div id="board"></div>
                <div className="board-controls">
                    <button onClick={resetGame}>New Game</button>
                    <button onClick={flipBoard}>Flip Board</button>
                </div>
            </div>

            <div className="right-panel">
                <div id="move-history">
                    <div className="history-header">
                        <h3>Move History</h3>
                    </div>
                    <div ref={moveHistoryRef} className="history-content">
                        {moveHistory.map((move, i) => (
                            <div key={i} className="move-row">
                                {i % 2 === 0 && (
                                    <span className="move-number">{Math.floor(i/2 + 1)}.</span>
                                )}
                                <span className="move-text">{move}</span>
                            </div>
                        ))}
                    </div>
                </div>

                <div id="chat-container">
                    <div id="chat-messages"></div>
                    <form id="chat-form">
                        <input type="text" id="user-input" placeholder="Type your move or message..." />
                        <button type="submit">Send</button>
                    </form>
                </div>
            </div>
        </div>
    );
};

// Mount the React component
ReactDOM.render(
    <ChessTutorInterface />,
    document.getElementById('root')
);