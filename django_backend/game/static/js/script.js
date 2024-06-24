// static/js/pong.js

document.addEventListener('DOMContentLoaded', () => {
    const socket = new WebSocket(`ws://${window.location.host}/ws/pong/`);
    let playerName = '';

    const gameArea = document.getElementById('game-area');
    const nameForm = document.getElementById('name-form');
    const nameInput = document.getElementById('name-input');
    const message = document.getElementById('message');
    const ball = document.getElementById('ball');
    const paddle1 = document.getElementById('paddle1');
    const paddle2 = document.getElementById('paddle2');
    const score1 = document.getElementById('score1');
    const score2 = document.getElementById('score2');

    nameForm.addEventListener('submit', (e) => {
        e.preventDefault();
        playerName = nameInput.value.trim();
        if (playerName) {
            socket.send(JSON.stringify({
                type: 'join',
                name: playerName
            }));
            nameForm.style.display = 'none';
            gameArea.style.display = 'block';
        }
    });

    document.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowUp' || e.key === 'ArrowDown') {
            socket.send(JSON.stringify({
                type: 'paddle_move',
                key: e.key,
                player: playerName
            }));
        }
    });

    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        switch (data.type) {
            case 'player_joined':
                message.textContent = `${data.name} joined the game`;
                break;
            case 'game_state':
                updateGameState(data.game_state);
                break;
            case 'game_over':
                message.textContent = `Game Over! ${data.winner} wins!`;
                break;
        }
    };

    function updateGameState(state) {
        ball.style.left = `${state.ball.x}px`;
        ball.style.top = `${state.ball.y}px`;
        paddle1.style.top = `${state.paddle1}px`;
        paddle2.style.top = `${state.paddle2}px`;
        score1.textContent = state.score.player1;
        score2.textContent = state.score.player2;
    }

    socket.onclose = (event) => {
        message.textContent = 'Connection closed. Please refresh the page.';
    };

    socket.onerror = (error) => {
        console.error('WebSocket Error:', error);
        message.textContent = 'An error occurred. Please refresh the page.';
    };
});