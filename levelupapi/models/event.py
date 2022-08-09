from django.db import models

class Event(models.Model):
    
    game = models.ForeignKey("Game", on_delete=models.CASCADE, related_name="events")
    description = models.TextField()
    # Does not need max length, is a block of text
    date = models.DateField()
    time = models.TimeField()
    #Date and Time fields doesn't need max length or any additional info
    organizer = models.ForeignKey("Gamer", on_delete=models.CASCADE, related_name="events")
    attendees = models.ManyToManyField("Gamer", through="EventGamer")
    # Works in background, gives all the events the gamer is attending

    @property
    def joined(self):
        return self.__joined

    @joined.setter
    def joined(self, value):
        self.__joined = value
