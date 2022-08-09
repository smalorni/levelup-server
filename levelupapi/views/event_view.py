"""View module for handling requests about events"""
from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from levelupapi.models import Event, Game, Gamer
from rest_framework.decorators import action


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
        # Needed this because gamer was undefined without it
        gamer = Gamer.objects.get(user=request.auth.user)
        
        # Set the `joined` property on every event, loops through events list
        for event in events:
            # Check to see if the gamer is in the attendees list on the event, decides if it is true or false if gamer is on list
            event.joined = gamer in event.attendees.all()
                  
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

    # delete event
    def destroy(self, request, pk):
        event = Event.objects.get(pk=pk)
        event.delete()
        return Response(None, status=status.HTTP_204_NO_CONTENT)
    # Sign up for event - related to event manager fetch calls - use signup in the url to join event
    @action(methods=['post'], detail=True)
    #The new route is named after function below - add "signup" to fetch call in event manager
    def signup(self, request, pk):
        """Post request for a user to sign up for an event"""
   
        gamer = Gamer.objects.get(user=request.auth.user)
        event = Event.objects.get(pk=pk)
        event.attendees.add(gamer)
        return Response({'message': 'Gamer added'}, status=status.HTTP_201_CREATED)
    # Leave an event - related to event manager fetch calls - use leave in the url for leaving event
    # Action turns a method into a new route
    # Method is 'delete', detail=true returns url with a pk
    @action(methods=['delete'], detail=True)
    # The new route is named after function below - add "leave" to fetch call in event manager
    def leave(self, request, pk):
        """Delete request for a user to leave an event"""
   
        gamer = Gamer.objects.get(user=request.auth.user)
        event = Event.objects.get(pk=pk)
        # Removes gamer
        event.attendees.remove(gamer)
        # Message will show up in Postman
        return Response({'message': 'Gamer removed'}, status=status.HTTP_204_NO_CONTENT)
    
 
# Make sure it outside of the first class
class EventSerializer(serializers.ModelSerializer):
    """JSON serializer for events
    """
    class Meta:
        model = Event
        fields = ('id', 'description', 'date', 'time', 'organizer', 'attendees', 'joined')
        #depth = 2