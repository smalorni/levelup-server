from django.db import models

class Game(models.Model):
    # Foreign keys are connected to the name of models/class name
    # On_delete means that specific row will be deleted that is related to games?
    game_type = models.ForeignKey("GameType", on_delete=models.CASCADE, related_name="games")
    # Max length needs to be less than 250 characters
    title = models.CharField(max_length=50)
    maker = models.CharField(max_length=50)
    gamer = models.ForeignKey("Gamer", on_delete=models.CASCADE, related_name="games")
    number_of_players = models.IntegerField()
    skill_level = models.IntegerField()