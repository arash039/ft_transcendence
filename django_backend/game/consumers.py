# pong/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
import asyncio
import random

class PongConsumer(AsyncWebsocketConsumer):
    players = {}
    game_state = {
        'ball': {'x': 390, 'y': 190, 'dx': 5, 'dy': 5},
        'paddle1': 160,
        'paddle2': 160,
        'score': {'player1': 0, 'player2': 0}
    }
    game_loop_task = None

    async def connect(self):
        await self.accept()
        print(f"Connection accepted for {self.channel_name}")

    async def disconnect(self, close_code):
        if self.channel_name in self.players:
            player_name = self.players[self.channel_name]
            del self.players[self.channel_name]
            await self.channel_layer.group_discard('pong_game', self.channel_name)
            print(f"Player {player_name} disconnected")
        if len(self.players) == 0 and self.game_loop_task:
            self.game_loop_task.cancel()

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data['type'] == 'join':
            await self.join_game(data['name'])
        elif data['type'] == 'paddle_move':
            await self.move_paddle(data['key'], data['player'])

    async def join_game(self, name):
        if len(self.players) < 2:
            self.players[self.channel_name] = name
            await self.channel_layer.group_add('pong_game', self.channel_name)
            await self.channel_layer.group_send(
                'pong_game',
                {
                    'type': 'player_joined',
                    'name': name
                }
            )
            if len(self.players) == 2:
                self.game_loop_task = asyncio.create_task(self.game_loop())

    async def move_paddle(self, key, player):
        paddle = 'paddle1' if player == list(self.players.values())[0] else 'paddle2'
        if key == 'ArrowUp' and self.game_state[paddle] > 0:
            self.game_state[paddle] -= 10
        elif key == 'ArrowDown' and self.game_state[paddle] < 320:
            self.game_state[paddle] += 10

    async def game_loop(self):
        while len(self.players) == 2:
            self.update_game_state()
            await self.channel_layer.group_send(
                'pong_game',
                {
                    'type': 'game_state_update',
                    'game_state': self.game_state
                }
            )
            await asyncio.sleep(0.033)  # Approximately 30 FPS

    def update_game_state(self):
        self.game_state['ball']['x'] += self.game_state['ball']['dx']
        self.game_state['ball']['y'] += self.game_state['ball']['dy']

        if self.game_state['ball']['y'] <= 0 or self.game_state['ball']['y'] >= 380:
            self.game_state['ball']['dy'] *= -1

        if (self.game_state['ball']['x'] <= 20 and 
            self.game_state['paddle1'] <= self.game_state['ball']['y'] <= self.game_state['paddle1'] + 80):
            self.game_state['ball']['dx'] *= -1
        elif (self.game_state['ball']['x'] >= 760 and 
              self.game_state['paddle2'] <= self.game_state['ball']['y'] <= self.game_state['paddle2'] + 80):
            self.game_state['ball']['dx'] *= -1

        if self.game_state['ball']['x'] <= 0:
            self.game_state['score']['player2'] += 1
            self.reset_ball()
        elif self.game_state['ball']['x'] >= 780:
            self.game_state['score']['player1'] += 1
            self.reset_ball()

        if self.game_state['score']['player1'] >= 5 or self.game_state['score']['player2'] >= 5:
            winner = list(self.players.values())[0] if self.game_state['score']['player1'] >= 5 else list(self.players.values())[1]
            asyncio.create_task(self.channel_layer.group_send(
                'pong_game',
                {
                    'type': 'game_over',
                    'winner': winner
                }
            ))

    def reset_ball(self):
        self.game_state['ball']['x'] = 390
        self.game_state['ball']['y'] = 190
        self.game_state['ball']['dx'] = random.choice([-5, 5])
        self.game_state['ball']['dy'] = random.choice([-5, 5])

    async def game_state_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'game_state',
            'game_state': event['game_state']
        }))

    async def player_joined(self, event):
        await self.send(text_data=json.dumps({
            'type': 'player_joined',
            'name': event['name']
        }))

    async def game_over(self, event):
        await self.send(text_data=json.dumps({
            'type': 'game_over',
            'winner': event['winner']
        }))