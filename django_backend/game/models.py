from django.db import models
from django.contrib.auth.models import User

class Tournament(models.Model):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

class TournamentMatch(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    player1 = models.CharField(max_length=100, default="Player 1")
    player2 = models.CharField(max_length=100, default="Player 2")
    round = models.IntegerField()