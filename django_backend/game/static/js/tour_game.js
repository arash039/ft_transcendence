export function startGame(sessionId, oldSocket) {
	//cleanupOldGame();
	const tourGameHTML = `
		<div id="game-area_tour">
			<p class="text-center"><h3 id="message_tour" class="message"></h3></p>
			<div id="ball_tour"></div>
			<div id="paddle1_tour" class="paddle"></div>
			<div id="paddle2_tour" class="paddle"></div>
			<div id="player1-name_tour" class="player-name"></div>
			<div id="score1_tour">0</div>
			<div id="player2-name_tour" class="player-name"></div>
			<div id="score2_tour">0</div>
		</div>
	`;
	setElementinnerHTML(document.getElementById('tour-game'), tourGameHTML);
	showElement(document.getElementById('tour-game'));
	let sId = window.location.hash.split('!')[1];
	sessionId = sId;
	const socket = new WebSocket(`wss://${window.location.host}/tour_game/${sId}/`);
	console.log('ws connection established');
	const gameArea = document.getElementById('game-area_tour');
	const message = document.getElementById('message_tour');
	const ball = document.getElementById('ball_tour');
	const paddle1 = document.getElementById('paddle1_tour');
	const paddle2 = document.getElementById('paddle2_tour');
	const score1 = document.getElementById('score1_tour');
	const score2 = document.getElementById('score2_tour');
	const player1 = document.getElementById('player1-name_tour');
	const player2 = document.getElementById('player2-name_tour');
	let stat_check_tour = false;


	message.textContent = `waiting for player...`;

	document.addEventListener('keydown', (e) => {
		if ((e.key === 'ArrowUp' || e.key === 'ArrowDown') && stat_check_tour === true){
			socket.send(JSON.stringify({
				type: 'paddle_move',
				key: e.key
			}));
		}
	});

	socket.onmessage = (event) => {
		const data = JSON.parse(event.data);
		switch (data.type) {
			case 'player_joined':
				message.textContent = `${data.name} ${JOINED}`;
				player1.textContent = data.name;
				setTimeout(() => {
					message.textContent = '';
				}, 1000);
				break;
			case 'both_players_joined':
				console.log('Both players joined');
				message.textContent = `${GET_READY}`;
				console.log(data.name);
				player2.textContent = data.name;
				break;
			case 'countdown':
				message.textContent = data.message;
				break;
			case 'game_state':
				updateGameState(data.game_state);
				break;
			case 'game_started':
				message.style.fontSize = '40px';
				message.textContent = `${STARTED}!`;
				stat_check_tour = true;
				setTimeout(() => {
					message.textContent = '';
					message.style.fontSize = '10px';
				}, 1000);
				break;
			case 'game_over':
				message.textContent = `${GAME_OVER2} ${data.winner} ${WON}!`;
				stat_check_tour = false;
				break;
			case 'game_stop':
				message.textContent = data.message;
				stat_check_tour = false;
				break;
			case 'player_rejoined':
				message.textContent = `${data.name} ${REJOINED}`;
				player1.textContent = data.name;
				player2.textContent = data.opponent;
				setTimeout(() => {
					message.textContent = '';
				}, 3000);
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
		message.textContent = `${REDIR_HOME}`;
		stat_check_tour = false;
		if (socket.readyState === WebSocket.CLOSED) {
			setTimeout(() => {
				window.location.hash = 'tour-hall';
			}, 3000);
		}
	};

	socket.onerror = (error) => {
		console.error('WebSocket Error:', error);
		message.textContent = 'An error occurred. Please refresh the page.';
	};

	function cleanupOldGame() {
		const gameContainer = document.getElementById('tour-game');
		if (gameContainer) {
			gameContainer.innerHTML = ''; // Clear the old HTML content
		}
	}

	function cleanupGame() {
		console.log('Cleaning up game');
		socket.close();
		deactivateListeners();
		cleanupOldGame();
		//history.pushState(null, '', window.location.href);
	};

	function deactivateListeners() {
		window.removeEventListener('beforeunload', cleanupGame);
		window.removeEventListener('popstate', cleanupGame);
	};
	
	function setupEventListeners() {
		window.addEventListener('beforeunload', cleanupGame);
		window.addEventListener('popstate', cleanupGame);
	};

	setupEventListeners();
};
