# encoding=utf-8
import pytest


@pytest.fixture(name='salesforce')
def _mock_salesforce(mockserver):
    class SalesforceContext:
        def __init__(self):
            self.query_response = {}
            self.query_expected_q = ''
            self.query_expected_auth = 'Bearer ACCESS_TOKEN_2'
            self.is_first_query_response_401 = False

        def set_query_expected_q(self, q):  # pylint: disable=invalid-name
            self.query_expected_q = q

        def set_query_expected_auth(self, auth_token):
            self.query_expected_auth = auth_token

        def set_query_response(self, response):
            self.query_response = response

        def set_first_query_response_401(self):
            self.is_first_query_response_401 = True

    context = SalesforceContext()

    @mockserver.json_handler('/services/oauth2/token')
    def _mock_oauth(request):
        return {
            'access_token': 'ACCESS_TOKEN_2',
            'instance_url': 'some_instance_url',
            'id': 'some_id',
            'token_type': 'some_token_type',
            'issued_at': 'asdf',
            'signature': 'asdfsdf',
        }

    @mockserver.json_handler('/salesforce/services/data/v50.0/query/')
    def _mock_query(request):
        if context.is_first_query_response_401:
            context.is_first_query_response_401 = False
            return mockserver.make_response(
                json=[
                    {
                        'message': 'Session expired or invalid',
                        'errorCode': 'INVALID_SESSION_ID',
                    },
                ],
                status=401,
            )

        assert request.headers['Authorization'] == context.query_expected_auth

        return context.query_response

    return context
