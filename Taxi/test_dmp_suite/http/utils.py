from dmp_suite.http.oauth_utils import Auth


class AuthProviderMock:

    def get_auth(self):  # type () -> Auth
        return Auth('test_token')


class ResponseMock:
    call_count = 0
    status_code = 401

    @classmethod
    def calc_response(cls):  # type() -> None
        if cls.call_count == 1 and cls.status_code == 401:
            cls.status_code = 200
        cls.call_count += 1

    @classmethod
    def reset(cls):  # type() -> None
        cls.status_code = 200
        cls.call_count = 0
