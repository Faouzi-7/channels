from django.db import models

# Create your models here.



class Game(models.Model):
    game = models.CharField(max_length=100)
    player1 = models.CharField(max_length=100)
    player2 = models.CharField(max_length=100)
    # state = models.JSONField()  # Store game state
    created_at = models.DateTimeField(auto_now_add=True)