"""Module for generating games by user report"""
from tkinter.tix import Select
from django.shortcuts import render
from django.db import connection
from django.views import View

from levelupreports.views.helpers import dict_fetch_all

class UserEventList(View):
    def get(self, request):
        with connection.cursor() as db_cursor:

            # TODO: Write a query to get all games along with the gamer first name, last name, and id
            db_cursor.execute("""
            SELECT 
                u.first_name ||' '|| u.last_name AS full_name,
                e.id,
                ga.title,
                e.description,
                e.date,
                e.time,
                e.game_id,
                e.organizer_id
            
            FROM levelupapi_event e
            JOIN levelupapi_gamer gr
                ON e.organizer_id = gr.id
            JOIN auth_user u
                ON u.id = gr.user_id
            JOIN levelupapi_game ga 
                ON ga.id = e.game_id
            """)
            # Pass the db_cursor to the dict_fetch_all function to turn the fetch_all() response into a dictionary
            dataset = dict_fetch_all(db_cursor)

            # Take the flat data from the dataset, and build the
            # following data structure for each gamer.
            # This will be the structure of the games_by_user list:
            #
            #             [
            #   {
            #     "gamer_id": 1,
            #     "full_name": "Molly Ringwald",
            #     "events": [
            #       {
            #         "id": 5,
            #         "date": "2020-12-23",
            #         "time": "19:00",
            #         "game_name": "Fortress America"
            #       }
            #     ]
            #   }
            # ]
            
            events_by_user = []

            for row in dataset:
                # TODO: Create a dictionary called game that includes 
                # the name, description, number_of_players, maker,
                # game_type_id, and skill_level from the row dictionary
                # since we joined tables, we have access to game's properties, for ex, title
                # this is connected to html template
                event = {
                   "id": row['id'],
                   "description": row['description'],
                   "title": row['title'],
                   "date": row['date'],
                   "time": row['time'],
                   "game_id": row['game_id'],
                   "organizer_id": row['organizer_id']
                }
                
                # See if the gamer has been added to the events_by_user list already
                user_dict = None
                for user_event in events_by_user:
                     if user_event['organizer_id'] == row['organizer_id']:
                         user_dict = user_event
                
                if user_dict:
                    # If the user_dict is already in the events_by_user list, append the game to the event list
                    user_dict['events'].append(event)
                else:
                    # If the user is not on the games_by_user list, create and add the user to the list
                    events_by_user.append({
                        "organizer_id": row['organizer_id'],
                        "full_name": row['full_name'],
                        "events": [event]
                    })
        
        # The template string must match the file name of the html template
        template = 'users/list_with_events.html'
        
        # The context will be a dictionary that the template can access to show data
        context = {
            "userevent_list": events_by_user
        }

        return render(request, template, context)