# coding=utf-8

from tnp.shared.auth_pb2 import AuthenticationRequest, AuthenticationResponse

class AuthService(object):

    user_id = 0

    def authenticate(self, auth_request):
        parsed_request = AuthenticationRequest()
        parsed_request.ParseFromString(auth_request)
        print parsed_request.username
        print parsed_request.password

        response = AuthenticationResponse()
        response.status = AuthenticationResponse.OK
        response.user_id = AuthService.user_id
        AuthService.user_id += 1
        return response

