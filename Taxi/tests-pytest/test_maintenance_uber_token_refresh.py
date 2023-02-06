import datetime
import pytest

from taxi.core import async
from taxi.config import configs
from taxi_maintenance.stuff import uber_token_refresh


@pytest.mark.config(
    UBER_API_TOKEN='default_token',
    UBER_API_TOKEN_URL='https://login.uber.com/token',
)
@pytest.mark.parametrize(
    'test_token_status_code,token_status_code,test_called,token_called',
    [
        (200, 200, 1, 0),
        (401, 200, 1, 1),
        (401, 400, 1, 1),
    ])
@pytest.inline_callbacks
def test_do_stuff(patch, test_token_status_code, token_status_code,
                  test_called, token_called):
    arequest_called = {'token': 0,
                       'test_token': 0}

    @patch('taxi.core.arequests.post')
    @async.inline_callbacks
    def arequests_post(*args, **kwargs):
        class TokenResponse:
            def __init__(self, status_code=200, recv_token='token'):
                self.status_code = status_code
                self.token = recv_token

            def json(self):
                return {
                    'access_token': self.token,
                    'expires_in': 1000,
                }

        if (yield args[0]) == (yield configs.UBER_API_TOKEN_URL.get()):
            arequest_called['token'] += 1
            async.return_value(TokenResponse(token_status_code))
        else:
            assert False, "Unwanted request url: {}".format(args[0])

    @patch('taxi.core.arequests.get')
    @async.inline_callbacks
    def arequests_get(*args, **kwargs):
        yield  # because function must be a generator

        class TestTokenResponse:
            def __init__(self, status_code=200):
                self.status_code = status_code

        if args[0] == 'https://api.uber.com/v1.2/me':
            arequest_called['test_token'] += 1
            async.return_value(TestTokenResponse(test_token_status_code))
        else:
            assert False, "Unwanted request url: {}".format(args[0])

    yield uber_token_refresh.do_stuff(datetime.datetime.strptime(
        '2018-02-12 17:01:00',
        '%Y-%m-%d %H:%M:%S'))

    assert arequest_called['test_token'] == test_called
    assert arequest_called['token'] == token_called


@pytest.mark.config(
    UBER_API_TOKEN='default_token',
    UBER_API_TOKEN_URL='https://login.uber.com/token',
    UBER_API_TOKEN_NEXT_REFRESH_TIMESTAMP='2018-05-12 17:00:00')
@pytest.mark.parametrize(
    'test_token_status_code,token_status_code,test_called,token_called',
    [
        (200, 200, 1, 1),
    ])
@pytest.inline_callbacks
def test_do_stuff_timestamp_refresh(patch, test_token_status_code,
                                    token_status_code, test_called,
                                    token_called):
    arequest_called = {'token': 0,
                       'test_token': 0}

    @patch('taxi.core.arequests.post')
    @async.inline_callbacks
    def arequests_post(*args, **kwargs):
        class TokenResponse:
            def __init__(self, status_code=200, recv_token='token'):
                self.status_code = status_code
                self.token = recv_token

            def json(self):
                return {
                    'access_token': self.token,
                    'expires_in': 1000,
                }

        if (yield args[0]) == (yield configs.UBER_API_TOKEN_URL.get()):
            arequest_called['token'] += 1
            async.return_value(TokenResponse(token_status_code))
        else:
            assert False, "Unwanted request url: {}".format(args[0])

    @patch('taxi.core.arequests.get')
    @async.inline_callbacks
    def arequests_get(*args, **kwargs):
        yield  # because function must be a generator

        class TestTokenResponse:
            def __init__(self, status_code=200):
                self.status_code = status_code

        if args[0] == 'https://api.uber.com/v1.2/me':
            arequest_called['test_token'] += 1
            async.return_value(TestTokenResponse(test_token_status_code))
        else:
            assert False, "Unwanted request url: {}".format(args[0])

    yield uber_token_refresh.do_stuff(datetime.datetime.strptime(
        '2018-05-12 17:01:00',
        '%Y-%m-%d %H:%M:%S'))

    assert arequest_called['test_token'] == test_called
    assert arequest_called['token'] == token_called
