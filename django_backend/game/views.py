from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from django.shortcuts import redirect
from django.utils.translation import activate
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from .models import Tournament, TournamentMatch
import random
from django.core.cache import cache
from django.urls import reverse
import uuid




# Required for the language
def set_language(request):
    if request.method == 'POST':
        language = request.POST.get('language')
        if language:
            request.session[translation.LANGUAGE_SESSION_KEY] = language
            activate(language)

    next_url = request.POST.get('next') or '/'
    return redirect(next_url)


# Create your views here.

def hello(request):
	return render(request, 'game/hello.html')

def offline_game(request):
    return render(request, 'game/offline-game.html')

@login_required
def game_start(request):
	return render(request, 'game/index.html', {})

def two_pl_game(request, session_id):
    if request.user.is_authenticated:
        print('session_id0:', session_id)
        return render(request, 'game/two-pl-game.html', {'session_id': session_id})
    else:
        return redirect('/')

def four_pl_game(request):
    if request.user.is_authenticated:
        return render(request, 'game/four-pl-game.html')
    else:
        return redirect('/')
    
# def tour(request):
#     if request.user.is_authenticated:
#         return render(request, 'game/tour.html')
#     else:
#         return redirect('/')
    
@login_required
def get_tournament_players(request):
    user = request.user
    return JsonResponse({'username': user.username})

# @login_required
# def tournament_view(request):
#     tournament = cache.get('tournament')

#     if tournament is None:
#         tournament = {
#             'semi_finals': [
#                 {'player1': None, 'player2': None},
#                 {'player1': None, 'player2': None}
#             ],
#             'final': {'player1': None, 'player2': None}
#         }

#     player_positions = [
#         ('semi_finals', 0, 'player1'),
#         ('semi_finals', 0, 'player2'),
#         ('semi_finals', 1, 'player1'),
#         ('semi_finals', 1, 'player2')
#     ]

#     user_position = None
#     for round_type, match_index, player_key in player_positions:
#         if tournament[round_type][match_index][player_key] == request.user.username:
#             user_position = (round_type, match_index, player_key)
#             break

#     if user_position is None:
#         available_positions = [
#             (round_type, match_index, player_key)
#             for round_type, match_index, player_key in player_positions
#             if tournament[round_type][match_index][player_key] is None
#         ]

#         if available_positions:
#             round_type, match_index, player_key = random.choice(available_positions)
#             tournament[round_type][match_index][player_key] = request.user.username
#             user_position = (round_type, match_index, player_key)

#             cache.set('tournament', tournament, timeout=3600)  # Cache for 1 hour

#     if user_position:
#         round_type, match_index, player_key = user_position
#         other_player_key = 'player1' if player_key == 'player2' else 'player2'
#         other_player = tournament[round_type][match_index][other_player_key]

#         if other_player:
#             # Both players are present, redirect to 2-player game
#             game_id = f"{round_type}_{match_index}"
#             #return redirect(reverse('two_pl_game', kwargs={'game_id': game_id}))
#             return redirect(reverse('two_pl_game'))

#     context = {
#         'tournament': tournament,
#         'user': request.user,
#     }
#     return render(request, 'game/tour.html', context)
    

# @login_required
# def tournament_view(request):
#     tournament = cache.get('tournament')

#     if tournament is None:
#         tournament = {
#             'semi_finals': [
#                 {'player1': None, 'player2': None},
#                 {'player1': None, 'player2': None}
#             ],
#             'final': {'player1': None, 'player2': None}
#         }

#     player_positions = [
#         ('semi_finals', 0, 'player1'),
#         ('semi_finals', 0, 'player2'),
#         ('semi_finals', 1, 'player1'),
#         ('semi_finals', 1, 'player2')
#     ]

#     user_position = None
#     for round_type, match_index, player_key in player_positions:
#         if tournament[round_type][match_index][player_key] == request.user.username:
#             user_position = (round_type, match_index, player_key)
#             break

#     if user_position is None:
#         available_positions = [
#             (round_type, match_index, player_key)
#             for round_type, match_index, player_key in player_positions
#             if tournament[round_type][match_index][player_key] is None
#         ]

#         if available_positions:
#             round_type, match_index, player_key = random.choice(available_positions)
#             tournament[round_type][match_index][player_key] = request.user.username
#             user_position = (round_type, match_index, player_key)

#             cache.set('tournament', tournament, timeout=3600)  # Cache for 1 hour

#     context = {
#         'tournament': tournament,
#         'user': request.user,
#         'game_ready': False
#     }

#     if user_position:
#         round_type, match_index, player_key = user_position
#         other_player_key = 'player1' if player_key == 'player2' else 'player2'
#         other_player = tournament[round_type][match_index][other_player_key]

#         if other_player:
#             # Both players are present
#             context['game_ready'] = True

#     return render(request, 'game/tour.html', context)


# @login_required
# def check_game_status(request):
#     tournament = cache.get('tournament')
#     player_positions = [
#         ('semi_finals', 0, 'player1'),
#         ('semi_finals', 0, 'player2'),
#         ('semi_finals', 1, 'player1'),
#         ('semi_finals', 1, 'player2')
#     ]

#     for round_type, match_index, player_key in player_positions:
#         if tournament[round_type][match_index][player_key] == request.user.username:
#             other_player_key = 'player1' if player_key == 'player2' else 'player2'
#             other_player = tournament[round_type][match_index][other_player_key]
#             if other_player:
#                 return JsonResponse({'game_ready': True})

#     return JsonResponse({'game_ready': False})

@login_required
def tournament_view(request):
    tournament = cache.get('tournament')

    if tournament is None:
        tournament = {
            'semi_finals': [
                {'player1': None, 'player2': None, 'session_id': str(uuid.uuid4())},
                {'player1': None, 'player2': None, 'session_id': str(uuid.uuid4())}
            ],
            'final': {'player1': None, 'player2': None, 'session_id': str(uuid.uuid4())}
        }

    player_positions = [
        ('semi_finals', 0, 'player1'),
        ('semi_finals', 0, 'player2'),
        ('semi_finals', 1, 'player1'),
        ('semi_finals', 1, 'player2')
    ]

    user_position = None
    for round_type, match_index, player_key in player_positions:
        if tournament[round_type][match_index][player_key] == request.user.username:
            user_position = (round_type, match_index, player_key)
            break

    if user_position is None:
        available_positions = [
            (round_type, match_index, player_key)
            for round_type, match_index, player_key in player_positions
            if tournament[round_type][match_index][player_key] is None
        ]

        if available_positions:
            round_type, match_index, player_key = random.choice(available_positions)
            tournament[round_type][match_index][player_key] = request.user.username
            user_position = (round_type, match_index, player_key)

            cache.set('tournament', tournament, timeout=3600)  # Cache for 1 hour

    context = {
        'tournament': tournament,
        'user': request.user,
        'game_ready': False
    }

    if user_position:
        round_type, match_index, player_key = user_position
        other_player_key = 'player1' if player_key == 'player2' else 'player2'
        other_player = tournament[round_type][match_index][other_player_key]
        session_id = tournament[round_type][match_index]['session_id']

        if other_player:
            context['game_ready'] = True
            context['session_id'] = session_id

    return render(request, 'game/tour.html', context)

@login_required
def check_game_status(request):
    tournament = cache.get('tournament')
    player_positions = [
        ('semi_finals', 0, 'player1'),
        ('semi_finals', 0, 'player2'),
        ('semi_finals', 1, 'player1'),
        ('semi_finals', 1, 'player2')
    ]

    for round_type, match_index, player_key in player_positions:
        if tournament[round_type][match_index][player_key] == request.user.username:
            other_player_key = 'player1' if player_key == 'player2' else 'player2'
            other_player = tournament[round_type][match_index][other_player_key]
            session_id = tournament[round_type][match_index]['session_id']
            if other_player:
                return JsonResponse({'game_ready': True, 'session_id': session_id})

    return JsonResponse({'game_ready': False})