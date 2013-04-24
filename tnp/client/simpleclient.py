# coding=utf-8

from twisted.internet import stdio, reactor, protocol
from twisted.protocols import basic

import re

from tnp.shared.auth_pb2 import AuthenticationRequest, AuthenticationResponse

class TestCommandProtocol(basic.LineReceiver):
    delimiter = '\n'

    def __init__(self):
        self.server_transport = None

    def connectionMade(self):
        self.sendLine("Test command console.")

    def lineReceived(self, line):
        if not line: return

        commandParts = line.split()
        command = commandParts[0].lower()
        args = commandParts[1:]

        try:
            method = getattr(self, 'do_' + command)
        except AttributeError as e:
            self.sendLine("error: no such command")
        else:
            try:
                method(*args)
            except Exception as e:
                self.sendLine("Error: " + str(e))

    def do_auth(self):
        # create auth request
        request = AuthenticationRequest()
        request.username = "Me"
        request.password = "secret"

        # send to server
        if self.server_transport:
            self.server_transport.write(request.SerializeToString())

    def do_sendstring(self, *args):
        to_send = ' '.join(args)
        if self.server_transport:
            self.server_transport.write(to_send)

class ServerConnectionProtocol(protocol.Protocol):

    def connectionMade(self):
        testCommandProtocol = TestCommandProtocol()
        testCommandProtocol.server_transport = self.transport
        self.stdioWrapper = stdio.StandardIO(testCommandProtocol)

    def dataReceived(self, data):
        try:
            response = AuthenticationResponse()
            response.ParseFromString(data)
            self.stdioWrapper.write(str(response))
        except:
            self.stdioWrapper.write(data + "\n")

class StdioProxyFactory(protocol.ClientFactory):
    protocol = ServerConnectionProtocol

    def clientConnectionLost(self, transport, reason):
        reactor.stop()

    def clientConnectionFailed(self, transport, reason):
        reactor.stop()

if __name__ == "__main__":
    host = "localhost"
    port = 8080
    reactor.connectTCP(host, port, StdioProxyFactory())
    reactor.run()