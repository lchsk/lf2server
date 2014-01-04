# -*- coding: utf-8 -*-
from twisted.internet import reactor, protocol
from twisted.protocols import basic
import message
from twisted.internet.defer import Deferred
import time

class LfProtocol(basic.LineReceiver):

    def connectionMade(self):
        print "\n\nNew connection from", self.transport.getPeer().host
        factory.logfile.write(time.strftime("%m/%d/%Y %H:%M:%S") + '\t' + 'New connection from ' + str(self.transport.getPeer().host) + '\n')
        
    
    def dataReceived(self, data):
        #print "ASCII value: ", ', '.join(str(ord(c)) for c in data)
        #print repr(data)
        factory.logfile.write(time.strftime("%m/%d/%Y %H:%M:%S") + '\t' + repr(data) + '\n')
        
        self.d = Deferred()
        self.d.addCallback(interpreter.interpret)
        self.d.addErrback(interpreter.error)
        self.d.callback((data, self))

class LfServerFactory(protocol.ServerFactory):

    def __init__(self):
        self.protocol  = LfProtocol
        self.users = {} # holding username, platforms
        self.games = {} # list of currently played games
        self.logfile = open(time.strftime("%m_%d_%Y_%H_%M_%S") + '.txt', 'w+')

if __name__ == "__main__":

    factory  = LfServerFactory()
    interpreter = message.MessageInterpreter(factory)
    
    port = 8000
    reactor.listenTCP(port, factory)
    print "Server running since " + time.strftime("%m/%d/%Y %H:%M:%S") + '...'
    reactor.run()
    
    factory.logfile.close()