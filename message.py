# -*- coding: utf-8 -*-

import json
import traceback, sys
import datetime

class MessageInterpreter(object):
    def __init__(self, factory):
        
        # Incoming string
        self.raw_message = ''
        
        # Incoming message in json format
        self.message = {}
         
        self.factory = factory
        
        # Ending added to every outgoing string
        self.ending = ''

    def interpret(self, pack):
        
        # Load stuff
        
        self.raw_message = pack[0]
        self.protocol = pack[1]
        self.message = json.loads(self.raw_message)
        
        ############
        # Messages
        ############
        
        # 10 NewConnection
        if self.message['id'] == 10:
            self._data = {}
            self._data['platform'] = self.message['platform']
            self._data['client'] = pack[1]
            self.factory.users[self.message['username']] = self._data
            
            # 13 ConnectionEstablished
            return_msg = {'id' : 13 }
            
            self.factory.users[self.message['username']]['client'].transport.write(json.dumps(return_msg) + self.ending)

        # Message
        #{"id":"M", "username": "lchsk", "x": "12", "y": "100", "anim": "1"}
        elif self.message['id'] == 'M':
            for user in self.factory.users:
                if user != self.message['username']:
                    self.factory.users[user]['client'].transport.write(self.raw_message)    

        # 1 CreateGame
        elif self.message['id'] == 1:
            admin = self.message['admin']
            dat = datetime.datetime.now()
            self.factory.games[admin] = { 'open' : True, 'date' : dat.strftime('%m/%d/%Y %H:%M:%S'), 'players': [admin] }
            
            # 2 GameCreated
            return_msg = {'id' : 2, 'date' : dat.strftime('%m/%d/%Y %H:%M:%S') }
            
            self.factory.users[admin]['client'].transport.write(json.dumps(return_msg) + self.ending)  
            
        # 3 GetOpenGames
        elif self.message['id'] == 3:
            open_games = [ (admin, items) for admin, items in self.factory.games.iteritems() if items['open'] == True]
            
            ret_games = {}
            for index, game in enumerate(open_games):
                ret_games[index] = {}
                ret_games[index]['admin'] = game[0]
                ret_games[index]['date'] = game[1]['date']
            
            # 4 OpenGamesList
            return_msg = {'id' : 4}
            return_msg = dict(return_msg.items() + ret_games.items())
            
            self.protocol.transport.write(json.dumps(return_msg) + self.ending)
        
        # 5 SignIn
        elif self.message['id'] == 5:
            admin = self.message['admin']
            user = self.message['user']
            
            self.factory.games[admin]['players'].append(user)
            
        # 7 GetSignedInPlayers
        elif self.message['id'] == 7:
            admin = self.message['admin']
            
            # 8 SignedInPlayers
            return_msg = {'id' : 8, 'players' : self.factory.games[admin]['players']}

            self.factory.users[admin]['client'].transport.write(json.dumps(return_msg) + self.ending)
            
        # 9 StartGame
        elif self.message['id'] == 9:
            admin = self.message['admin']
            
            self.factory.games[admin]['open'] = False
            
            self.create_heroes(admin)
        
        # 11 IsGameStarted
        elif self.message['id'] == 11:
            admin = self.message['admin']
            
            if self.factory.games[admin]['open']:
                # 12 GameNotStarted
                return_msg = {'id' : 12}
                self.protocol.transport.write(json.dumps(return_msg) + self.ending)
            else:
                # game is on
                self.create_heroes(admin)

    def error(self, pack):
        print 'Error...'
        traceback.print_exc(file=sys.stdout)
        
    # 6 CreateHeroes
    def create_heroes(self, admin):
           
        return_msg = {'id' : 6, 'players' : self.factory.games[admin]['players']}
        
        for user in self.factory.users:
            self.factory.users[user]['client'].transport.write(json.dumps(return_msg) + self.ending)
            