# -*- coding: utf-8 -*-

import json
import md5

class MessageInterpreter(object):
    def __init__(self, factory):
        self.raw_message = ''
        self.message = {}
        self.factory = factory

    def interpret(self, pack):
        self.raw_message = pack[0]
        self.message = json.loads(self.raw_message)
        print self.message
        print 'type: ' + self.message['type'] 

        # Welcome 
        #{"type": "W", "username": "lchsk", "platform":"A"}
        if self.message['type'] == 'W':
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
        #{"type":"M", "username": "lchsk", "x": "12", "y": "100", "anim": "1"}
        elif self.message['type'] == 'M':
            for user in self.factory.users:
                if user != self.message['username']:
                    self.factory.users[user]['client'].transport.write(self.raw_message)    


    def error(self, pack):
        print 'Error while interpreting'

    def test(self):
        print 'test'