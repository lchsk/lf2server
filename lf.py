from twisted.internet import reactor, protocol
from twisted.protocols import basic
import message
from twisted.internet.defer import Deferred


class LfProtocol(basic.LineReceiver):

    def connectionMade(self):
        print "Connection from ", self.transport.getPeer().host
    
    def dataReceived(self, data):
        print data
        d = Deferred()
        d.addCallback(interpreter.interpret)
        d.addErrback(interpreter.error)
        d.callback((data, self))

class LfServerFactory(protocol.ServerFactory):

    def __init__(self):
        self.protocol  = LfProtocol
        self.users = {}

if __name__ == "__main__":

    factory  = LfServerFactory()
    interpreter = message.MessageInterpreter(factory)
    
    port = 8000
    reactor.listenTCP(port, factory)
    print "Server running"
    reactor.run()