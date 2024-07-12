from django.urls import path, re_path
from . import views
from django.urls import path, include
from .views import get_tournament_players


urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),  # Include i18n URL for language setting
	path('', views.hello, name='hello'),
    path('game-start/', views.game_start, name='game_start'),
    path('two-pl-game/', views.two_pl_game, name='two_pl_game'),
    path('four-pl-game/', views.four_pl_game, name='four_pl_game'),
    path('offline-game/', views.offline_game, name='offline_game'),
    # path('tour/', views.tour, name='tour'),
    path('tournament/', views.tournament_view, name='tournament_view'),
    path('api/get_tournament_players/', get_tournament_players, name='get_tournament_players'),
    path('tournament/check_game_status/', views.check_game_status, name='check_game_status'),
    path('tournament/game/', views.two_pl_game, name='two_pl_game'),  
    re_path(r'ws/game/(?P<session_id>[0-9a-fA-F-]+)/$', views.two_pl_game, name='two_pl_game'),
]