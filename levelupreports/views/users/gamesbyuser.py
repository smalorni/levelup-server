"""Module for generating games by user report"""
from tkinter.tix import Select
from django.shortcuts import render
from django.db import connection
from django.views import View

from levelupreports.views.helpers import dict_fetch_all

class UserGameList(View):
    def get(self, request):
        with connection.cursor() as db_cursor:

            # TODO: Write a query to get all games along with the gamer first name, last name, and id
            db_cursor.execute("""
            SELECT 
                gr.id,
                u.first_name ||' '|| u.last_name AS full_name,
                ga.id,
                ga.gamer_id,
                ga.title,
                ga.maker,
                ga.skill_level,
                ga.number_of_players,
                ga.game_type_id
            
            FROM levelupapi_gamer gr
            JOIN levelupapi_game ga
                ON gr.id = ga.gamer_id
            JOIN auth_user u
                ON u.id = gr.user_id
            """)
            # Pass the db_cursor to the dict_fetch_all function to turn the fetch_all() response into a dictionary
            dataset = dict_fetch_all(db_cursor)

            # Take the flat data from the dataset, and build the
            # following data structure for each gamer.
            # This will be the structure of the games_by_user list:
            #
            # [
            #   {
            #     "id": 1,
            #     "full_name": "Admina Straytor",
            #     "games": [
            #       {
            #         "id": 1,
            #         "title": "Foo",
            #         "maker": "Bar Games",
            #         "skill_level": 3,
            #         "number_of_players": 4,
            #         "game_type_id": 2
            #       },
            #       {
            #         "id": 2,
            #         "title": "Foo 2",
            #         "maker": "Bar Games 2",
            #         "skill_level": 3,
            #         "number_of_players": 4,
            #         "game_type_id": 2
            #       }
            #     ]
            #   },
            # ] 
            
            games_by_user = []

            for row in dataset:
                # TODO: Create a dictionary called game that includes 
                # the name, description, number_of_players, maker,
                # game_type_id, and skill_level from the row dictionary
                game = {
                   "id": row['id'],
                   "title": row['title'],
                   "maker": row['maker'],
                   "gamer_id": row['gamer_id'],
                   "number_of_players": row['number_of_players'],
                   "skill_level": row['skill_level']
                }
                
                # See if the gamer has been added to the games_by_user list already
                user_dict = None
                for user_game in games_by_user:
                     if user_game['gamer_id'] == row['gamer_id']:
                         user_dict = user_game
                
                
                if user_dict:
                    # If the user_dict is already in the games_by_user list, append the game to the games list
                    user_dict['games'].append(game)
                else:
                    # If the user is not on the games_by_user list, create and add the user to the list
                    games_by_user.append({
                        "gamer_id": row['gamer_id'],
                        "full_name": row['full_name'],
                        "games": [game]
                    })
        
        # The template string must match the file name of the html template
        template = 'users/list_with_games.html'
        
        # The context will be a dictionary that the template can access to show data
        context = {
            "usergame_list": games_by_user
        }

        return render(request, template, context)
