import pytest

from taxi.clients import mds


RESPONSE_TYPE_1 = b"""<?xml version="1.0" encoding="utf-8"?>
    <post>
    <key>3402/filename</key>
    </post>"""
RESPONSE_TYPE_2 = b"""<?xml version="1.0" encoding="utf-8"?>
    <post obj="obj" id="..." groups="2" size="226" key="3402/filename">
    <complete addr="..." path="path" group="4643" status="0"/>
    <complete addr="..." path="path" group="3402" status="0"/>
    <written>2</written>
    </post>"""
TO_UPLOAD = '{"key": "value"}'
REDIRECT_LINK = '//some.storage.net/namespace/0/data/data-0.0:348:4'


class _Response:
    xml_response = None

    def __init__(self, status_code, headers, data):
        self.status = status_code
        if 'Range' in headers:
            headers['content-range'] = True
        self.headers = headers
        self.data = data

    async def read(self):
        return self.data

    async def text(self):
        return self.xml_response

    def raise_for_status(self):
        if self.status >= 400:
            raise mds.MDSHTTPError(self.status)


class _MockSession:
    # pylint: disable=too-many-instance-attributes
    def __init__(
            self,
            method,
            expected_mds_method,
            expected_http_method,
            status_code,
            client_exception,
    ):
        self.method = method
        self.expected_mds_method = expected_mds_method
        self.expected_http_method = expected_http_method
        self.status_code = status_code
        self.client_exception = client_exception
        self.calls = 0
        self.redirects = 0
        self.last_response = None

    async def request(
            self,
            http_method,
            url,
            headers=None,
            data=None,
            params=None,
            allow_redirects=True,
    ):
        self.calls += 1
        assert isinstance(allow_redirects, bool)
        assert http_method == self.expected_http_method
        if self.method in ('upload', 'remove'):
            expected_host = 'upload_host'
        else:
            expected_host = 'get_host'
        if self.expected_http_method == 'GET':
            data = 'data file'
        if params:
            if 'expire' in params:
                assert params['expire'].endswith('s')
            if 'redirect' in params:
                assert params['redirect'] == 'yes'
        assert url.find(expected_host) == 7
        url_without_host = url.split('{}/'.format(expected_host))[1]
        assert url_without_host.find(self.expected_mds_method) == 0
        if self.method == 'redirect':
            headers = headers or {}
            headers.update({'Location': REDIRECT_LINK})
            data = None

        self.last_response = _Response(self.status_code, headers, data)
        if (
                self.last_response.status in (301, 302, 303, 307, 308)
                and allow_redirects
        ):
            self.redirects += 1
        if self.client_exception:
            if self.client_exception is mds.MDSRangeError:
                self.last_response.headers.pop('content-range')
            if self.client_exception is mds.MDSGetRedirectError:
                self.last_response.headers.pop('Location')

        return self.last_response


def _get_func_method(mds_client, method):
    if method == 'download':
        func_method = mds_client.download
    elif method == 'upload':
        func_method = mds_client.upload
    elif method == 'remove':
        func_method = mds_client.remove
    elif method == 'redirect':
        func_method = mds_client.redirect
    else:
        assert method == 'exists'
        func_method = mds_client.exists
    return func_method


@pytest.mark.parametrize(
    [
        'method',
        'expected_mds_method',
        'expected_http_method',
        'file_key_or_value',
        'status_code',
        'client_exception',
        'expected_result',
    ],
    [
        ('download', 'get', 'GET', '123/4567', 200, None, 'data file'),
        ('download', 'get', 'GET', '123/4567', 200, mds.MDSRangeError, None),
        ('download', 'get', 'GET', '123/4567', 500, mds.MDSHTTPError, None),
        ('upload', 'upload', 'POST', TO_UPLOAD, 200, None, '3402/filename'),
        ('upload', 'upload', 'POST', TO_UPLOAD, 500, mds.MDSHTTPError, None),
        ('remove', 'delete', 'POST', '567/1234', 200, None, None),
        ('remove', 'delete', 'POST', '567/1234', 500, mds.MDSHTTPError, None),
        ('exists', 'get', 'HEAD', '567/1234', 200, None, True),
        ('exists', 'get', 'HEAD', '567/1234', 404, None, False),
        ('exists', 'get', 'HEAD', '567/1234', 500, mds.MDSHTTPError, None),
        ('redirect', 'get', 'GET', '123/4567', 302, None, REDIRECT_LINK),
        (
            'redirect',
            'get',
            'GET',
            '123/4567',
            200,
            mds.MDSGetRedirectError,
            None,
        ),
        (
            'redirect',
            'get',
            'GET',
            '123/4567',
            302,
            mds.MDSGetRedirectError,
            None,
        ),
    ],
)
async def test_mds_client(
        method,
        expected_mds_method,
        expected_http_method,
        file_key_or_value,
        status_code,
        client_exception,
        expected_result,
):
    session = _MockSession(
        method,
        expected_mds_method,
        expected_http_method,
        status_code,
        client_exception,
    )
    mds_client = mds.MDSClient(
        session, 'token', 'namespace', 'http://upload_host', 'http://get_host',
    )
    func_method = _get_func_method(mds_client, method)

    if client_exception:
        if client_exception is mds.MDSRangeError:
            args_list = [
                (file_key_or_value, 1, 2),
                (file_key_or_value, None, 2),
                (file_key_or_value, 1, None),
            ]
        else:
            args_list = [(file_key_or_value,)]
        for args in args_list:
            with pytest.raises(client_exception):
                await func_method(*args)
        assert session.calls == len(args_list)
    else:
        if method == 'upload':
            for xml_response in (RESPONSE_TYPE_1, RESPONSE_TYPE_2):
                _Response.xml_response = xml_response
                for ttl in (None, 3):
                    assert expected_result == await func_method(
                        file_key_or_value, ttl=ttl,
                    )
            assert session.calls == 4
        elif method == 'redirect':
            redirect_link = await func_method(file_key_or_value)
            assert redirect_link == '%s:%s' % (
                mds.MDS_REDIRECT_SCHEME,
                expected_result,
            )
            assert session.calls == 1
            assert session.redirects == 0
        else:
            assert expected_result == await func_method(file_key_or_value)
            assert session.calls == 1

        if method == 'download':
            for args, expected_range in (
                    ((1, 2), 'bytes=1-2'),
                    ((None, 2), 'bytes=-2'),
                    ((1, None), 'bytes=1-'),
                    ((0, 2), 'bytes=0-2'),
            ):
                assert expected_result == await func_method(
                    file_key_or_value, *args,
                )
                assert session.last_response.headers['Range'] == expected_range
            assert session.calls == 5
