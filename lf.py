# -*- coding: utf-8 -*-
from twisted.internet import reactor, protocol
from twisted.protocols import basic
import message
from twisted.internet.defer import Deferred
import time

class LfProtocol(basic.LineReceiver):

    def connectionMade(self):
        print "\n\nNew connection from", self.transport.getPeer().host
    
    def dataReceived(self, data):
        #print "ASCII value: ", ', '.join(str(ord(c)) for c in data)
        d = Deferred()
        d.addCallback(interpreter.interpret)
        d.addErrback(interpreter.error)
        d.callback((data, self))

class LfServerFactory(protocol.ServerFactory):

    def __init__(self):
        self.protocol  = LfProtocol
        self.users = {} # holding username, platforms
        self.games = {} # list of currently played games

if __name__ == "__main__":

    factory  = LfServerFactory()
    interpreter = message.MessageInterpreter(factory)
    
    port = 8000
    reactor.listenTCP(port, factory)
    print "Server running since " + time.strftime("%m/%d/%Y %H:%M:%S") + '...'
    reactor.run()