"""View module for handling requests about events"""
from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from levelupapi.models import Event, Game, Gamer


class EventView(ViewSet):
    """Level up events view"""

    def list(self, request):
        """Handle GET requests to get all events

        Returns:
            Response -- JSON serialized list of events
        """
        events = Event.objects.all()
        # Add in the next 3 lines - purpose: you're getting the events for specific game - look at erd
        game = request.query_params.get('game', None)
        if game is not None:
            events = events.filter(game_id=game)
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk):
        """Handle GET requests for single event

        Returns:
            Response -- JSON serialized event
        """
        try:
            event = Event.objects.get(pk=pk)
            serializer = EventSerializer(event)
            return Response(serializer.data)
        # Responds with a 404 message - doesn't exist
        except Event.DoesNotExist as ex: 
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND) 
    
    def create(self, request):
        """Handle POST operations
        Returns Response -- JSON serialized event instance
        """
        # These are foreign keys to get the objects
        gamer = Gamer.objects.get(user=request.auth.user)
        game = Game.objects.get(pk=request.data["game"]) #game id

        event = Event.objects.create(
            #FK to game id
            game=game,
            description=request.data["description"],
            date=request.data["date"],
            time=request.data["time"],
            #FK to gamer id
            organizer=gamer
            )
        # Attendee related to gamer.id
        event.attendees.add(gamer.id)
        serializer = EventSerializer(event)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk):
        """Handle PUT requests for a game

            Returns:
        Response -- Empty body with 204 status code
        """
        # Get the event objects by pk (url)
        event = Event.objects.get(pk=pk)
        # Get description, date, time data
        event.description  = request.data["description"]
        event.date = request.data["date"]
        event.time = request.data["time"]

        # Connected to gamer, updates the current data with new data
        organizer = Gamer.objects.get(user=request.auth.user)
        event.organizer = organizer
        event.save()

        return Response(None, status=status.HTTP_204_NO_CONTENT)


# Make sure it outside of the first class
class EventSerializer(serializers.ModelSerializer):
    """JSON serializer for events
    """
    class Meta:
        model = Event
        fields = ('id', 'description', 'date', 'time', 'organizer', 'attendees')
        #depth = 2