# -*- coding: utf-8 -*-

import json
import traceback, sys
import datetime
import time
import random

class MessageInterpreter(object):
    def __init__(self, factory):
        
        # Incoming string
        self.raw_message = ''
        
        # Incoming message in json format
        self.message = {}
         
        self.factory = factory
        
        # Ending added to every outgoing string
        self.ending = '\r\n'
        
        self.default_char = 'luke'
        
        self.user_admin_pair = {}

    def interpret(self, pack):
        
        # Load stuff
        
        self.raw_message = pack[0]
        self.protocol = pack[1]
           
        magic_char = '*'
        jsons = self.raw_message.split(magic_char)
        
        for msg in jsons:
            #self.message = json.loads(self.raw_message)
            if msg != '':
                self.message = json.loads(msg)
        
            ############
            # Messages
            ############
            
            # 10 NewConnection
            if self.message['id'] == 10:
                self._data = {}
                self._data['platform'] = self.message['platform']
                self._data['client'] = pack[1]
                self._data['pos'] = { 'x': 0, 'y': 0 }
                
                # Player's character (string)
                self._data['char'] = None
                self.factory.users[self.message['username']] = self._data
                
                # 13 ConnectionEstablished
                return_msg = {'id' : 13 }
                
                self.factory.users[self.message['username']]['client'].transport.write(json.dumps(return_msg) + self.ending)   
    
            # 1 CreateGame
            elif self.message['id'] == 1:
                admin = self.message['admin']
                self.user_admin_pair[admin] = admin
                character = self.message['character']
                dat = datetime.datetime.now()
                self.factory.games[admin] = { 'open' : True, 'date' : dat.strftime('%m/%d/%Y %H:%M:%S'), 'players': [admin] }
    
                # Save character
                self.factory.users[admin]['char'] = character
                
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
                character = self.message['character']
                
                self.factory.users[user]['char'] = character
                
                if user not in self.factory.games[admin]['players']:
                    self.factory.games[admin]['players'].append(user)
                    self.user_admin_pair[user] = admin
                
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
                    
            # 14 UpdatePosition
            elif self.message['id'] == 14:
                user = self.message['user']
                admin = self.user_admin_pair[user]
                x = self.message['x']
                y = self.message['y']
                
                # Update positions
                self.factory.users[user]['pos']['x'] = x
                self.factory.users[user]['pos']['y'] = y
                
                # 15 PositionUpdated
                return_msg = {'id' : 15}
                
                # Add positions of every player
                for u in self.factory.games[admin]['players']:
                    return_msg[u] = []
                    return_msg[u].append(self.factory.users[u]['pos']['x'])
                    return_msg[u].append(self.factory.users[u]['pos']['y'])
                
                for u in self.factory.users:
                    if u != user:
                        self.factory.users[u]['client'].transport.write(json.dumps(return_msg) + self.ending)

            # 16 ChangeState
            elif self.message['id'] == 16:
                user = self.message['user']
                state = self.message['state']
                
                return_msg = {'id' : 17, 'user' : user, 'state' : state}
                
                for u in self.factory.users:
                    #if u != user:
                        self.factory.users[u]['client'].transport.write(json.dumps(return_msg) + self.ending)

    def error(self, pack):
        print 'Error...'
        #self.factory.logfile.write(time.strftime("%m/%d/%Y %H:%M:%S") + '\t' + traceback.print_exc(file=sys.stdout) + '\n')
        traceback.print_exc(file=sys.stdout)
        
    # 6 CreateHeroes
    def create_heroes(self, admin):
        
        char_list = []
        posx = []
        posy = []
        
        # set up players starting positions
        players_len = len(self.factory.games[admin]['players'])
        step = 1.0 / players_len
        current_step = step / 2.0
        
        for i in xrange(0, players_len):
            posx.append(current_step)
            posy.append(0.19 / random.randint(1, 10))
            current_step += step
        
        for p in self.factory.games[admin]['players']:
            c = self.factory.users[p]['char']
            
            if c == None:
                c = default_char
            char_list.append(c)
           
        return_msg = {'id' : 6, 'players' : self.factory.games[admin]['players'], 'characters' : char_list, 'posx' : posx, 'posy' : posy}
        
        for user in self.factory.users:
            self.factory.users[user]['client'].transport.write(json.dumps(return_msg) + self.ending)
            