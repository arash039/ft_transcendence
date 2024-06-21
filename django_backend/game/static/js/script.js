document.addEventListener('DOMContentLoaded', function() {
	// WebSocket setup
	var socket = new WebSocket('ws://' + window.location.host + '/ws/pong/');
	let playerId = Math.random() > 0.5 ? 'player1' : 'player2';

	let gameState = 'start';
	let paddle_1, paddle_2, board, ball, score_1, score_2, message;
	let paddle_1_coord, paddle_2_coord, initial_ball_coord, ball_coord, board_coord, paddle_common;

	socket.onopen = function() {
		console.log('Connected to the server');
	};

	socket.onmessage = function(e) {
		var data = JSON.parse(e.data);
		console.log('Received message:', data);
		if (data.type === 'move') {
			updateOpponentPosition(data);
		} else if (data.type === 'ballMove') {
			updateBallPosition(data);
		}
	};

	function updateOpponentPosition(data) {
		if (data.playerId !== playerId) {
			let opponentPaddle = playerId === 'player1' ? paddle_2 : paddle_1;
			opponentPaddle.style.top = data.position + 'px';
			if (playerId === 'player1') {
				paddle_2_coord = paddle_2.getBoundingClientRect();
			} else {
				paddle_1_coord = paddle_1.getBoundingClientRect();
			}
		}
	}

	function updateBallPosition(data) {
		if (playerId === 'player2') {
			ball.style.left = data.x + 'px';
			ball.style.top = data.y + 'px';
			ball_coord = ball.getBoundingClientRect();
		}
	}

	function showSection(sectionIds) {
		document.querySelectorAll('#screen > .container').forEach(function(section) {
			if (sectionIds.includes(section.id)) {
				section.style.display = 'block';
			} else {
				section.style.display = 'none';
			}
		});
	}

	document.getElementById('2pl').addEventListener('click', function() {
		showSection(['header-game', 'basic-game']);
		
		paddle_1 = document.querySelector('.paddle_1');
		paddle_2 = document.querySelector('.paddle_2');
		board = document.querySelector('.board');
		ball = document.querySelector('.ball');
		score_1 = document.querySelector('.player_1_score');
		score_2 = document.querySelector('.player_2_score');
		message = document.querySelector('.message');
		paddle_1_coord = paddle_1.getBoundingClientRect();
		paddle_2_coord = paddle_2.getBoundingClientRect();
		initial_ball_coord = ball.getBoundingClientRect();
		ball_coord = initial_ball_coord;
		board_coord = board.getBoundingClientRect();
		paddle_common = document.querySelector('.paddle').getBoundingClientRect();

		let dx = Math.floor(Math.random() * 4) + 3;
		let dy = Math.floor(Math.random() * 4) + 3;
		let dxd = Math.floor(Math.random() * 2);
		let dyd = Math.floor(Math.random() * 2);

		document.addEventListener('keydown', (e) => {
			if (e.key == 'Enter' && gameState === 'start') {
				gameState = 'play';
				message.innerHTML = 'Game Started';
				message.style.left = '42vw';
				if (playerId === 'player1') {
					requestAnimationFrame(() => {
						moveBall(dx, dy, dxd, dyd);
					});
				}
			}
			if (gameState == 'play') {
				let paddleToMove = playerId === 'player1' ? paddle_1 : paddle_2;
				let paddleCoord = playerId === 'player1' ? paddle_1_coord : paddle_2_coord;

				if ((playerId === 'player1' && (e.key == 'w' || e.key == 's')) ||
					(playerId === 'player2' && (e.key == 'ArrowUp' || e.key == 'ArrowDown'))) {
					
					let newTop;
					if (e.key == 'w' || e.key == 'ArrowUp') {
						newTop = Math.max(board_coord.top, paddleCoord.top - window.innerHeight * 0.06);
					} else {
						newTop = Math.min(board_coord.bottom - paddle_common.height, paddleCoord.top + window.innerHeight * 0.06);
					}
					
					paddleToMove.style.top = newTop + 'px';
					if (playerId === 'player1') {
						paddle_1_coord = paddle_1.getBoundingClientRect();
					} else {
						paddle_2_coord = paddle_2.getBoundingClientRect();
					}

					// Send paddle position to server
					socket.send(JSON.stringify({ type: 'move', playerId: playerId, position: newTop }));
				}
			}
		});

		function moveBall(dx, dy, dxd, dyd) {
			if (ball_coord.top <= board_coord.top) {
				dyd = 1;
			}
			if (ball_coord.bottom >= board_coord.bottom) {
				dyd = 0;
			}
			if (ball_coord.left <= paddle_1_coord.right && ball_coord.top >= paddle_1_coord.top && ball_coord.bottom <= paddle_1_coord.bottom) {
				dxd = 1;
				dx = Math.floor(Math.random() * 4) + 3;
				dy = Math.floor(Math.random() * 4) + 3;
			}
			if (ball_coord.right >= paddle_2_coord.left && ball_coord.top >= paddle_2_coord.top && ball_coord.bottom <= paddle_2_coord.bottom) {
				dxd = 0;
				dx = Math.floor(Math.random() * 4) + 3;
				dy = Math.floor(Math.random() * 4) + 3;
			}
			if (ball_coord.left <= board_coord.left || ball_coord.right >= board_coord.right) {
				if (ball_coord.left <= board_coord.left) {
					score_2.innerHTML = +score_2.innerHTML + 1;
				} else {
					score_1.innerHTML = +score_1.innerHTML + 1;
				}
				gameState = 'start';
				ball.style.top = initial_ball_coord.top + 'px';
				ball.style.left = initial_ball_coord.left + 'px';
				ball_coord = ball.getBoundingClientRect();
				message.innerHTML = 'Press Enter to Play';
				message.style.left = '38vw';
				return;
			}
			ball.style.top = ball_coord.top + dy * (dyd == 0 ? -1 : 1) + 'px';
			ball.style.left = ball_coord.left + dx * (dxd == 0 ? -1 : 1) + 'px';
			ball_coord = ball.getBoundingClientRect();

			// Send ball position to server
			socket.send(JSON.stringify({ type: 'ballMove', x: ball_coord.left, y: ball_coord.top }));

			requestAnimationFrame(() => {
				moveBall(dx, dy, dxd, dyd);
			});
		}
	});

	document.getElementById('restart').addEventListener('click', function() {
		showSection(['header-welcome', 'start']);
	});

	document.getElementById('play').addEventListener('click', function(event) {
		event.preventDefault(); // Prevent form submission
		var playerName = document.getElementById('player_name1').value;
		document.getElementById('player_left').textContent = playerName;
		showSection(['header-game', 'one_player']);
	});

	// Initially show only the start section
	showSection(['header-welcome', 'start']);
});