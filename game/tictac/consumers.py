# chat/consumers.py
import json

from channels.generic.websocket import WebsocketConsumer

from channels.generic.websocket import AsyncJsonWebsocketConsumer
import pprint
from django.core.cache import cache
import random
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from asgiref.sync import sync_to_async
from queue import Queue
from .models import Game
games = {}
channel_layer = get_channel_layer()
winningCombinations = [
    {'combo':[0,1,2], 'strikeClass': "strike-row-1"},
    {'combo':[3,4,5], 'strikeClass': "strike-row-2"},
    {'combo':[6,7,8], 'strikeClass': "strike-row-3"},
    {'combo':[0,3,6], 'strikeClass': "strike-column-1"},
    {'combo':[1,4,7], 'strikeClass': "strike-column-2"},
    {'combo':[2,5,8], 'strikeClass': "strike-column-3"},
    {'combo':[0,4,8], 'strikeClass': "strike-diagonal-1"},
    {'combo':[2,4,6], 'strikeClass': "strike-diagonal-2"},
]
# cache.set("tictac_table", [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '])


# class QueueConsumer1v1(AsyncJsonWebsocketConsumer):
#     count = 0
#     async def connect(self):
#         print("connect")
#         await self.accept()
#         QueueConsumer1v1.count += 1
#         if (QueueConsumer1v1.count == 2):
#             random_bool = bool(random.getrandbits(1))
#             await self.channel_layer.group_send("1v1", {"type": "start.game","turn" : random_bool,"table": tictac_table, "logo" : "X" if random_bool == 0 else "O"})
#             await self.channel_layer.group_add("1v1", self.channel_name)
#             await channel_layer.send(self.channel_name,{"type": "start.game","turn" : not random_bool,"table": tictac_table,  "logo" : "O" if random_bool == 0 else "X"})
#         else:
#             await self.channel_layer.group_add("1v1", self.channel_name)           
#         pass
    
#     async def disconnect(self, close_code):
#         print("disconnect")
#         FirstConsumer.count -= 1
#         await self.channel_layer.group_discard("1v1", self.channel_name)
            
#     async def start_game(self, event):
#         if hasattr(self,'turn'):
#             self.turn = not self.turn
#             event["turn"] = self.turn
#         else:
#             self.turn = event["turn"]
#             self.logo = event["logo"]

#         if ("type" in event):
#             event.pop('type', None) 
#         if ("logo" in event):
#             event.pop('logo', None)
#         event["table"] = cache.get("tictac_table")
#         await self.send_json(event)
    
    
class FirstConsumer(AsyncJsonWebsocketConsumer):
    qe = Queue()
    async def connect(self):
        await self.accept()
        print("connect")
        # join_game = self.scope['url_route']['kwargs']['join_game']
        await self.join_game()
        
    
    async def join_game(self):
        print("join_game")
        FirstConsumer.qe.put({"channel_name": self.channel_name})
        if (FirstConsumer.qe.qsize() == 2):
            # random_bool = bool(random.getrandbits(1))
            p1_channel = FirstConsumer.qe.get()["channel_name"]
            p2_channel = FirstConsumer.qe.get()["channel_name"] 
            game_id = str(random.getrandbits(14))
            print(game_id)
            await self.channel_layer.group_add(game_id, p1_channel)
            await self.channel_layer.group_add(game_id, p2_channel)
            await channel_layer.send(p1_channel, {"type": "start.game", "game": game_id, "turn" : True})
            await channel_layer.send(p2_channel, {"type": "start.game", "game": game_id, "turn" : False})
        
        
                
    async def start_game(self, event):
        self.game_id = event["game"]
        self.turn = event["turn"]
        self.logo = "X" if self.turn else "O"
        event["logo"] = self.logo
        event["table"] = [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']
        global games 
        games[self.game_id] = [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']
        await self.send_json(event)

    async def check_winner(self,table):
        x = 0
        for combination in winningCombinations:
            if table[combination['combo'][0]] == table[combination['combo'][1]] == table[combination['combo'][2]] != ' ':
                return combination['strikeClass']
        x = 0
        for tile in table:
                x += 1 if tile != ' ' else 0
        if x == 9:
            return "draw"
        return "inprogress"
            
    async def receive_json(self, text_data):
        if hasattr(text_data,"join_again"):
            join_game(self)
            return
        if not hasattr(self, 'game_id'):
            print("game not started")
            return
        if self.turn:
            global games
            if games[self.game_id][text_data["index"]] != ' ': 
                print("3AMRA")
                return
            games[self.game_id][text_data["index"]] = self.logo;
            e = await self.check_winner(games[self.game_id])
            if e == "inprogress":
                await self.channel_layer.group_send(self.game_id, {"type": "update.table","turn" : "none"})
            else:
                await self.channel_layer.group_send(self.game_id, {"type": "end.game", "winner": self.logo, "class" : e})
        else:
            print("not your turn")

    async def end_game(self, event):
        print("end_game")
        global games
        
        event["table"] = games[self.game_id]
        event["endgame"] = True
        event["turn"] = self.turn
        print(event["class"])
        if event["class"] == "draw":
            del event["class"]
        # await self.send_json(event)
        await self.clear_table(event)
        

    async def update_table(self, event):
        print("update_table")
        self.turn = not self.turn
        global games
        event["table"] = games[self.game_id]
        event["turn"] = self.turn
        await self.send_json(event)
        
        
    async def disconnect(self, close_code):
        print("disconnect")
        if hasattr(self, 'turn'):
            del self.turn
        if hasattr(self, 'logo'):
            del self.logo
        if hasattr(self, 'game_id'):
            await self.channel_layer.group_discard(self.game_id, self.channel_name)
            await self.channel_layer.group_send(self.game_id, {"type": "clear.table"})
            del self.game_id
    
    async def clear_table(self, event):
        print("clear_table")
        event["endgame"] = True
        print("event = " , event)
        # print("bye")
        if hasattr(self, 'turn'):
            del self.turn
        if hasattr(self, 'logo'):
            del self.logo
        if hasattr(self, 'game_id'):
        #         await self.channel_layer.group_discard(self.game_id, self.channel_name)
                global games
                # del games[self.game_id]
                del self.game_id
        await self.send_json(event)
        # # event["table"] = [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']
        # FirstConsumer.qe.get()
        