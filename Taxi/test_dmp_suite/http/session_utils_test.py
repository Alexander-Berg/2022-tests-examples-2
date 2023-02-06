import mock

from dmp_suite.http.session_utils import SessionWithRetries, SessionShortLivedToken

from .utils import ResponseMock, AuthProviderMock


def _session_with_retry_request_mock(_self):  # type(SessionShortLivedToken) -> ResponseMock
    response = ResponseMock()
    response.calc_response()
    return response


def test_session_short_live_token():
    with mock.patch.object(SessionWithRetries, 'request', new=_session_with_retry_request_mock):
        session = SessionShortLivedToken(
            auth_provider=AuthProviderMock(),
            read_timeout=1.0,
        )
        # check if first request return 401 and count requests
        assert session.request().status_code == 200
        assert ResponseMock.call_count == 2

        ResponseMock.reset()
        # check if first request return 200 and count requests
        assert session.request().status_code == 200
        assert ResponseMock.call_count == 1
