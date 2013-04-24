# coding=utf-8

from twisted.internet import reactor, protocol, defer

from tnp.server.authentication import AuthService
from tnp.shared.auth_pb2 import AuthenticationResponse
class TNPProtocol(protocol.Protocol):
    AUTHENTICATE = 0
    CONNECTED = 1
    DISCONNECTED = 2

    def connectionMade(self):
        self.state = TNPProtocol.AUTHENTICATE

    def dataReceived(self, data):
        if self.state == TNPProtocol.AUTHENTICATE:
            response = self.factory.authenticate(data)
            if response.status == AuthenticationResponse.OK:
                self.user_id = response.user_id
                self.state = TNPProtocol.CONNECTED

            self.transport.write(response.SerializeToString())

        elif self.state == TNPProtocol.CONNECTED:
            self.transport.write(data)

    def connectionLost(self, reason):
        self.state = TNPProtocol.DISCONNECTED

class TNPFactory(protocol.ServerFactory):

    protocol = TNPProtocol

    def __init__(self):
        self.auth_service = AuthService()

    def authenticate(self, data):
        return self.auth_service.authenticate(data)

def run_server():
    factory = TNPFactory()
    reactor.listenTCP(8080, factory)
    reactor.run()

if __name__ == "__main__":
    run_server()