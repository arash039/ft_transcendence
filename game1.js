const canvas = document.getElementById('pongCanvas');
const context = canvas.getContext('2d');

let player1Score = 0;
let player2Score = 0;

const paddleWidth = 10;
const paddleHeight = 100;
const ballRadius = 10;

let paddle1Y = (canvas.height - paddleHeight) / 2;
let paddle2Y = (canvas.height - paddleHeight) / 2;

let ballX = canvas.width / 2;
let ballY = canvas.height / 2;
let ballSpeedX = 5;
let ballSpeedY = 2;

let upPressed = false;
let downPressed = false;
let wPressed = false;
let sPressed = false;

document.addEventListener('keydown', keyDownHandler, false);
document.addEventListener('keyup', keyUpHandler, false);

function keyDownHandler(e) {
    if (e.key === 'ArrowUp') {
        upPressed = true;
    }
    if (e.key === 'ArrowDown') {
        downPressed = true;
    }
    if (e.key === 'w' || e.key === 'W') {
        wPressed = true;
    }
    if (e.key === 's' || e.key === 'S') {
        sPressed = true;
    }
}

function keyUpHandler(e) {
    if (e.key === 'ArrowUp') {
        upPressed = false;
    }
    if (e.key === 'ArrowDown') {
        downPressed = false;
    }
    if (e.key === 'w' || e.key === 'W') {
        wPressed = false;
    }
    if (e.key === 's' || e.key === 'S') {
        sPressed = false;
    }
}

function drawRect(x, y, w, h, color) {
    context.fillStyle = color;
    context.fillRect(x, y, w, h);
}

function drawCircle(x, y, r, color) {
    context.fillStyle = color;
    context.beginPath();
    context.arc(x, y, r, 0, Math.PI * 2, false);
    context.closePath();
    context.fill();
}

function resetBall() {
    ballX = canvas.width / 2;
    ballY = canvas.height / 2;
    ballSpeedX = -ballSpeedX;
}

function moveBall() {
    ballX += ballSpeedX;
    ballY += ballSpeedY;

    if (ballY + ballRadius > canvas.height || ballY - ballRadius < 0) {
        ballSpeedY = -ballSpeedY;
    }

    if (ballX + ballRadius > canvas.width) {
        player1Score++;
        resetBall();
        updateScore();
    } else if (ballX - ballRadius < 0) {
        player2Score++;
        resetBall();
        updateScore();
    }

    if (ballX - ballRadius < paddleWidth && ballY > paddle1Y && ballY < paddle1Y + paddleHeight) {
        ballSpeedX = -ballSpeedX;
    }

    if (ballX + ballRadius > canvas.width - paddleWidth && ballY > paddle2Y && ballY < paddle2Y + paddleHeight) {
        ballSpeedX = -ballSpeedX;
    }
}

function movePaddles() {
    if (wPressed && paddle1Y > 0) {
        paddle1Y -= 7;
    } else if (sPressed && paddle1Y < canvas.height - paddleHeight) {
        paddle1Y += 7;
    }

    if (upPressed && paddle2Y > 0) {
        paddle2Y -= 7;
    } else if (downPressed && paddle2Y < canvas.height - paddleHeight) {
        paddle2Y += 7;
    }
}

function drawEverything() {
    drawRect(0, 0, canvas.width, canvas.height, 'black');
    drawRect(0, paddle1Y, paddleWidth, paddleHeight, 'white');
    drawRect(canvas.width - paddleWidth, paddle2Y, paddleWidth, paddleHeight, 'white');
    drawCircle(ballX, ballY, ballRadius, 'white');

    document.getElementById('scorePlayer1').innerText = `Player 1: ${player1Score}`;
    document.getElementById('scorePlayer2').innerText = `Player 2: ${player2Score}`;
}

function gameLoop() {
    moveBall();
    movePaddles();
    drawEverything();
}

setInterval(gameLoop, 1000 / 60);

document.getElementById('endGameBtn').addEventListener('click', () => {
    const winnerId = player1Score > player2Score ? 1 : 2;
    const result = {
        player1_id: 1,  // Replace with actual player ID
        player2_id: 2,  // Replace with actual player ID
        score_player1: player1Score,
        score_player2: player2Score,
        winner_id: winnerId,
        timestamp: new Date().toISOString(),
    };
    console.log('Game result:', result);
    // submitGameResult(result);  // Uncomment this line when you want to send results to backend
});

function submitGameResult(result) {
    fetch('/api/submit_game_result/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`,  // Use the actual token
        },
        body: JSON.stringify(result),
    })
    .then(response => response.json())
    .then(data => console.log('Game result submitted:', data))
    .catch(error => console.error('Error:', error));
}
