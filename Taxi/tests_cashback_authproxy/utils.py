import json

REAL_IP = '1.2.3.4'


def assert_remote_headers(
        remote_request,
        expected_uid: str = None,
        expected_pass_flags: list = None,
):
    headers = remote_request.headers
    assert headers['X-Remote-IP'] == REAL_IP
    assert 'X-YaTaxi-API-Key' not in headers
    assert 'X-YaTaxi-External-Service' in headers

    if expected_uid is not None:
        assert headers['X-Yandex-UID'] == expected_uid
        assert headers['X-Yandex-Login'] == 'login'
    else:
        assert 'X-Yandex-UID' not in headers
        assert 'X-Yandex-Login' not in headers

    if expected_pass_flags is not None:
        _validate_flags(headers['X-YaTaxi-Pass-Flags'], expected_pass_flags)


def _validate_flags(pass_flags: str, expected: list):
    assert set(pass_flags.split(',')) == set(expected)


class BaseResponse:
    inner_dict = None
    http_status = 200

    def set_http_status(self, status_code):
        self.http_status = status_code
        return self

    def _to_json(self):
        return json.dumps(self.inner_dict)

    def make_response(self, mockserver):
        return mockserver.make_response(
            self._to_json(), status=self.http_status,
        )


class ApiKeyResponse(BaseResponse):
    def __init__(self, http_status=200):
        if http_status == 200:
            self.inner_dict = {'key_id': 'key_id'}
        elif http_status in [400, 403]:
            self.http_status = http_status
            self.inner_dict = {
                'message': 'some wrong',
                'code': 'consumer_not_found',
            }
        else:
            self.http_status = 500
