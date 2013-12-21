# -*- coding: utf-8 -*-

import json
import traceback, sys
import datetime

class MessageInterpreter(object):
    def __init__(self, factory):
        self.raw_message = ''
        self.message = {}
        self.factory = factory

    def interpret(self, pack):
        self.raw_message = pack[0]
        self.protocol = pack[1]
        self.message = json.loads(self.raw_message)
        print self.message
        print 'id: ' + str(self.message['id'])

        # Welcome 
        #{"id": "W", "username": "lchsk", "platform":"A"}
        if self.message['id'] == 'W':
            print self.message['username']
            #print self.factory.users
            
            self._data = {}
            self._data['platform'] = self.message['platform']
            self._data['client'] = pack[1]
            self.factory.users[self.message['username']] = self._data
            #print self.factory.users
            print 'Player ' + str(self.message['username']) + ' added...'
            self.factory.users[self.message['username']]['client'].transport.write(
                'You (' + str(self.message['username']) + ') joined the game.')

        # Message
        #{"id":"M", "username": "lchsk", "x": "12", "y": "100", "anim": "1"}
        elif self.message['id'] == 'M':
            for user in self.factory.users:
                if user != self.message['username']:
                    self.factory.users[user]['client'].transport.write(self.raw_message)    

        # CreateGame Packet
        #{\"id\": \"1\", \"admin\": \"admin\"}
        elif self.message['id'] == 1:
            admin = self.message['admin']
            dat = datetime.datetime.now()
            self.factory.games[admin] = { 'open' : True, 'date' : dat.strftime('%m/%d/%Y %H:%M:%S'), 'players': [admin] }
            
            # GameCreated Packet
            return_msg = {'id' : 2, 'date' : dat.strftime('%m/%d/%Y %H:%M:%S') }
            print return_msg

            # send back to the admin
            #for user in self.factory.users:
            #    if user == self.message['admin']:
            self.factory.users[admin]['client'].transport.write(json.dumps(return_msg))  
            
        # GetOpenGames
        elif self.message['id'] == 3:
            #print self.factory.games
            open_games = [ (admin, items) for admin, items in self.factory.games.iteritems() if items['open'] == True]
            print open_games
            print self.factory.games
            print len(self.factory.games)
            
            ret_games = {}
            for index, game in enumerate(open_games):
                ret_games[index] = {}
                ret_games[index]['admin'] = game[0]
                ret_games[index]['date'] = game[1]['date']
            
            # OpenGameList
            return_msg = {'id' : 4}
            return_msg = dict(return_msg.items() + ret_games.items())
            print json.dumps(return_msg)
            
            print self.protocol.transport.write(json.dumps(return_msg))
        
        # Signin
        elif self.message['id'] == 5:
            admin = self.message['admin']
            user = self.message['user']
            
            self.factory.games[admin]['players'].append(user)
            
            print self.factory.games
            
        # GetSignedInPlayers
        elif self.message['id'] == 7:
            admin = self.message['admin']
            
            return_msg = {'id' : 8, 'players' : self.factory.games[admin]['players']}
            
            print return_msg

            self.factory.users[admin]['client'].transport.write(json.dumps(return_msg))
            
        elif self.message['id'] == 9:
            admin = self.message['admin']
            
            self.factory.games[admin]['open'] = False
            
            # send 6 to everyone

    def error(self, pack):
        print 'Error while interpreting'
        traceback.print_exc(file=sys.stdout)

    def test(self):
        print 'test'