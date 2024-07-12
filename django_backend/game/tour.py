import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pong_game.settings')
django.setup()

import json
from channels.generic.websocket import AsyncWebsocketConsumer
import asyncio
import random
from users.models import Profile
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from datetime import datetime
import time
import uuid

User = get_user_model()

class PongConsumer(AsyncWebsocketConsumer):
    game_sessions = {}
    disconnected_players = {}
    rejoin_timeout = 10
    waiting_players = []

    async def connect(self):
        await self.accept()
        user = self.scope['user']
        if user.is_authenticated:
            self.add_to_waiting_players(user.username)
            if len(self.waiting_players) >= 4:
                await self.start_tournament()
        else:
            await self.close()

    async def disconnect(self, close_code):
        user = self.scope['user']
        if user.username in self.waiting_players:
            self.waiting_players.remove(user.username)
        if hasattr(self, 'session_id') and self.session_id in self.game_sessions:
            player_name = self.game_sessions[self.session_id]['players'].pop(self.channel_name, None)
            other_player = next(iter(self.game_sessions[self.session_id]['players'].values()), None)
            if player_name:
                self.disconnected_players[player_name] = {
                    'session_id': self.session_id,
                    'rejoin_deadline': time.time() + self.rejoin_timeout,
                    'opponent': other_player
                }
                await self.channel_layer.group_discard(self.session_id, self.channel_name)
                if 'game_loop_task' in self.game_sessions[self.session_id]:
                    self.game_sessions[self.session_id]['game_loop_task'].cancel()
                    self.game_sessions[self.session_id]['game_loop_task'] = None
                asyncio.create_task(self.check_player_rejoin_timeout(self.session_id, player_name, other_player))

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data['type'] == 'paddle_move':
            await self.move_paddle(data['key'])

    async def move_paddle(self, key):
        user = self.scope['user']
        if user.username == list(self.game_sessions[self.session_id]['players'].values())[1]:
            paddle = 'paddle1'
        else:
            paddle = 'paddle2'
        if key == 'ArrowUp' and self.game_sessions[self.session_id]['game_state'][paddle] > 0:
            self.game_sessions[self.session_id]['game_state'][paddle] -= 10
        elif key == 'ArrowDown' and self.game_sessions[self.session_id]['game_state'][paddle] < 300:
            self.game_sessions[self.session_id]['game_state'][paddle] += 10

    def add_to_waiting_players(self, username):
        self.waiting_players.append(username)

    async def start_tournament(self):
        players = self.waiting_players[:4]
        self.waiting_players = self.waiting_players[4:]
        for i in range(2):
            session_id = f"game_session_{uuid.uuid4()}"
            self.game_sessions[session_id] = {
                'players': {},
                'game_state': {
                    'ball': {'x': 390, 'y': 190, 'dx': 5, 'dy': 5},
                    'paddle1': 160,
                    'paddle2': 160,
                    'score': {'player1': 0, 'player2': 0}
                },
                'game_loop_task': None
            }
            for j in range(2):
                username = players.pop(0)
                self.add_player_to_session(session_id, username, self.channel_name)
                await self.channel_layer.group_add(session_id, self.channel_name)
            self.game_sessions[session_id]['game_loop_task'] = asyncio.create_task(self.start_game_countdown(session_id))

    def add_player_to_session(self, session_id, username, channel_name):
        self.game_sessions[session_id]['players'][channel_name] = username

    async def start_game_countdown(self, session_id):
        await asyncio.sleep(2)
        for i in range(3, 0, -1):
            await self.channel_layer.group_send(
                session_id,
                {
                    'type': 'countdown',
                    'message': f"Game starts in {i} seconds..."
                }
            )
            await asyncio.sleep(1)
        await self.channel_layer.group_send(
            session_id,
            {
                'type': 'game_started'
            }
        )
        self.game_sessions[session_id]['game_loop_task'] = asyncio.create_task(self.game_loop(session_id))

    async def game_loop(self, session_id):
        while len(self.game_sessions[session_id]['players']) == 2:
            self.update_game_state(session_id)
            await self.channel_layer.group_send(
                session_id,
                {
                    'type': 'game_state_update',
                    'game_state': self.game_sessions[session_id]['game_state']
                }
            )
            await asyncio.sleep(0.033)

    def update_game_state(self, session_id):
        game_state = self.game_sessions[session_id]['game_state']
        game_state['ball']['x'] += game_state['ball']['dx']
        game_state['ball']['y'] += game_state['ball']['dy']

        if game_state['ball']['y'] <= 0 or game_state['ball']['y'] >= 380:
            game_state['ball']['dy'] *= -1

        if (game_state['ball']['x'] <= 20 and game_state['paddle1'] <= game_state['ball']['y'] <= game_state['paddle1'] + 80):
            game_state['ball']['dx'] *= -1
        elif (game_state['ball']['x'] >= 760 and game_state['paddle2'] <= game_state['ball']['y'] <= game_state['paddle2'] + 80):
            game_state['ball']['dx'] *= -1

        if game_state['ball']['x'] <= 0:
            game_state['score']['player2'] += 1
            self.reset_ball(session_id)
        elif game_state['ball']['x'] >= 780:
            game_state['score']['player1'] += 1
            self.reset_ball(session_id)

        if game_state['score']['player1'] >= 2 or game_state['score']['player2'] >= 2:
            winner = list(self.game_sessions[session_id]['players'].values())[1] if game_state['score']['player1'] >= 2 else list(self.game_sessions[session_id]['players'].values())[0]
            result = {
                'players': list(self.game_sessions[session_id]['players'].values()),
                'winner': winner,
                'score': game_state['score']
            }
            asyncio.create_task(self.send_game_result(result, session_id, winner))
            self.reset_game(session_id)

    def reset_ball(self, session_id):
        game_state = self.game_sessions[session_id]['game_state']
        game_state['ball']['x'] = 390
        game_state['ball']['y'] = 190
        game_state['ball']['dx'] = random.choice([-5, 5])
        game_state['ball']['dy'] = random.choice([-5, 5])

    def reset_game(self, session_id):
        self.game_sessions[session_id]['game_state'] = {
            'ball': {'x': 390, 'y': 190, 'dx': 5, 'dy': 5},
            'paddle1': 160,
            'paddle2': 160,
            'score': {'player1': 0, 'player2': 0}
        }
        self.game_sessions[session_id]['players'] = {}
        if self.game_sessions[session_id]['game_loop_task']:
            self.game_sessions[session_id]['game_loop_task'].cancel()
            self.game_sessions[session_id]['game_loop_task'] = None

    async def game_state_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'game_state',
            'game_state': event['game_state']
        }))

    async def countdown(self, event):
        await self.send(text_data=json.dumps({
            'type': 'countdown',
            'message': event['message']
        }))

    async def game_started(self, event):
        await self.send(text_data=json.dumps({
            'type': 'game_started',
            'message': 'Game started!'
        }))

    async def game_over(self, event):
        await self.send(text_data=json.dumps({
            'type': 'game_over',
            'winner': event['winner']
        }))
        await asyncio.sleep(2)
        await self.close()

    async def send_game_result(self, result, session_id, winner):
        user = self.scope['user']
        opponent_username = result['players'][1] if user.username == result['players'][0] else result['players'][0]
        opponent_user = await self.get_user_by_username(opponent_username)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if result['winner'] == user.username:
            winner = user.username
            looser = opponent_username
        else:
            winner = opponent_username
            looser = user.username

        historyString = f"{current_time}, {winner}, {looser};"

        await self.update_game_history(user, historyString)
        await self.update_game_history(opponent_user, historyString)

        await self.channel_layer.group_send(
            session_id,
            {
                'type': 'game_over',
                'winner': result['winner']
            }
        )

    async def get_user_by_username(self, username):
        return await sync_to_async(User.objects.get)(username=username)

    async def update_game_history(self, user, history_string):
        profile = await sync_to_async(Profile.objects.get)(user=user)
        profile.history += history_string
        await sync_to_async(profile.save)()

    async def check_player_rejoin_timeout(self, session_id, player_name, opponent):
        await asyncio.sleep(self.rejoin_timeout)
        if player_name in self.disconnected_players and time.time() >= self.disconnected_players[player_name]['rejoin_deadline']:
            await self.channel_layer.group_send(
                session_id,
                {
                    'type': 'game_over',
                    'winner': opponent
                }
            )
            self.reset_game(session_id)
            del self.disconnected_players[player_name]
