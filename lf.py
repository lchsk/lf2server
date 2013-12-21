# -*- coding: utf-8 -*-
from twisted.internet import reactor, protocol
from twisted.protocols import basic
import message
from twisted.internet.defer import Deferred
import time

'''
1. Ustanowienie połączenia między klientem a serwerem
2. Serwer wysyła SignInRequest
3. Klient odsyła pakiet SignInResponse. W tym pakiecie znajduje się nazwa postaci jaką wybrał gracz (a postać wybiera się przed dołączeniem do gry).
4. Jeśli serwer otrzymał SignInResponse od każdego klienta to wysyła pakiet CreateHeroes z informacjami na temat nazw postaci, ich peerID i pozycji.
5. Klient tworzy graczy zgodnie z otrzymanym pakietem i odysła HeroesCreated.
'''

class LfProtocol(basic.LineReceiver):

    def connectionMade(self):
        print "\n\nConnection from ", self.transport.getPeer().host
    
    def dataReceived(self, data):
        print data
        print time.strftime("%H:%M:%S")
        #print "ASCII value: ", ', '.join(str(ord(c)) for c in data)
        d = Deferred()
        d.addCallback(interpreter.interpret)
        d.addErrback(interpreter.error)
        d.callback((data, self))

class LfServerFactory(protocol.ServerFactory):

    def __init__(self):
        self.protocol  = LfProtocol
        self.users = {}
        self.games = {} # list of currently played games

if __name__ == "__main__":

    factory  = LfServerFactory()
    interpreter = message.MessageInterpreter(factory)
    
    port = 8000
    reactor.listenTCP(port, factory)
    print "Server running since " + time.strftime("%m/%d/%Y %H:%M:%S") + '...'
    reactor.run()