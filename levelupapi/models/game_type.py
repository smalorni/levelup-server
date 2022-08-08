from django.db import models

class GameType(models.Model):
    # No foreign keys in this class
    label = models.CharField(max_length=50)