import pytest

from taxi.core import arequests


LINK = 'ceb7854c394e434c8767cb45e69e3f4a'
NOT_SET_KWARG = object()


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize('method', ['get', 'post', 'delete', 'head', 'request'])
@pytest.mark.parametrize('headers,log_extra,expected', [
    ({'other-header': 'test_header'}, {'_link': LINK}, True),
    (None, {'_link': LINK}, True),
    (NOT_SET_KWARG, {'_link': LINK}, True),
    ({'other-header': 'foobar'}, None, False),
    (None, NOT_SET_KWARG, False),
    (NOT_SET_KWARG, {'other-extra': 'bar'}, False),
    ({'X-YaRequestId': LINK}, NOT_SET_KWARG, True)
])
@pytest.mark.asyncenv('blocking')
def test_ya_request_id_header(areq_request, method,
                              headers, log_extra, expected):
    @areq_request
    def req(*args, **kwargs):
        if expected:
            assert kwargs['headers']['X-YaRequestId'] == LINK
        else:
            assert (kwargs.get('headers') or {}).get('X-YaRequestId') is None

        return areq_request.response(200, body=None)

    kwargs = {}
    if headers != NOT_SET_KWARG:
        kwargs['headers'] = headers
    if log_extra != NOT_SET_KWARG:
        kwargs['log_extra'] = log_extra

    if method == 'request':
        getattr(arequests, method)(arequests.METHOD_GET, 'url', **kwargs)
    else:
        getattr(arequests, method)('url', **kwargs)
