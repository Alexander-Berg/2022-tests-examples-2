# pylint: disable=redefined-outer-name
import asyncio

import pytest

from taxi.clients import async_icap

DEFAULT_RESPONSE = (
    b'ICAP/1.0 200 OK\r\n'
    b'Connection: close\r\n'
    b'Server: C-ICAP/1.0\r\n'
    b'Encapsulated: res-body=0, res-hdr=18, '
    b'req-hdr=154, req-body=219, opt-hdr=243, opt-body=288\r\n'
    b'\r\n'
    b'8\r\n'
    b'infected\r\n'
    b'0\r\n'
    b'\r\n'
    b'HTTP/1.0 403 Forbidden\r\n'
    b'Content-type: text/html\r\n'
    b'Content-length: 8\r\n'
    b'Date: Thu Aug 12 2021 15:57:27 GMT\r\n'
    b'X-Infection-Found: WIN95.CIH\r\n'
    b'\r\n'
    b'HTTP/1.0 200 OK\r\n'
    b'Content-type: text/plain\r\n'
    b'Content-length: 14\r\n'
    b'\r\n'
    b'e\r\n'
    b'some_test_data\r\n'
    b'0\r\n'
    b'\r\n'
    b'HTTP/1.0 404 NOT FOUND\r\n'
    b'Content-length: 9\r\n'
    b'\r\n'
    b'9\r\n'
    b'Not found\r\n'
    b'0\r\n'
    b'\r\n'
)

DEFAULT_EXPECTED_REQUEST = (
    b'REQMOD icap://some_remote_host/yavs ICAP/1.0\r\n'
    b'Host: some_remote_host\r\n'
    b'Encapsulated: req-body=0\r\n'
    b'\r\n'
    b'e\r\n'
    b'some_test_data\r\n'
    b'0\r\n'
    b'\r\n'
)


@pytest.mark.parametrize(
    'remote_host, remote_port, data, response_data, expected_request_data, '
    'expected_icap_status, expected_icap_reason, expected_icap_headers, '
    'expected_http_status, expected_http_reason, expected_http_headers, '
    'expected_http_body',
    [
        (
            'some_remote_host',
            1234,
            b'some_test_data',
            (
                b'ICAP/1.0 200 OK\r\n'
                b'Encapsulated: res-hdr=0, res-body=74\r\n'
                b'\r\n'
                b'HTTP/1.0 200 OK\r\n'
                b'Content-type: text/html\r\n'
                b'X-Infection-Found: WIN95.CIH\r\n'
                b'\r\n'
                b'8\r\n'
                b'infected\r\n'
                b'0\r\n'
                b'\r\n'
            ),
            DEFAULT_EXPECTED_REQUEST,
            200,
            'OK',
            {'encapsulated': 'res-hdr=0, res-body=74'},
            200,
            'OK',
            {'content-type': 'text/html', 'x-infection-found': 'WIN95.CIH'},
            b'infected',
        ),
        (
            'some_remote_host',
            1234,
            b'some_test_data',
            (
                b'ICAP/1.0 200 OK\r\n'
                b'Encapsulated: res-hdr=0\r\n'
                b'\r\n'
                b'HTTP/1.0 200 OK\r\n'
                b'Content-type: text/html\r\n'
                b'X-Infection-Found: WIN95.CIH\r\n'
                b'\r\n'
            ),
            DEFAULT_EXPECTED_REQUEST,
            200,
            'OK',
            {'encapsulated': 'res-hdr=0'},
            200,
            'OK',
            {'content-type': 'text/html', 'x-infection-found': 'WIN95.CIH'},
            None,
        ),
        (
            'some_remote_host',
            1234,
            b'some_test_data',
            (
                b'ICAP/1.0 200 OK\r\n'
                b'Encapsulated: res-hdr=0, null-body=74\r\n'
                b'\r\n'
                b'HTTP/1.0 200 OK\r\n'
                b'Content-type: text/html\r\n'
                b'X-Infection-Found: WIN95.CIH\r\n'
                b'\r\n'
            ),
            DEFAULT_EXPECTED_REQUEST,
            200,
            'OK',
            {'encapsulated': 'res-hdr=0, null-body=74'},
            200,
            'OK',
            {'content-type': 'text/html', 'x-infection-found': 'WIN95.CIH'},
            None,
        ),
        (
            'some_remote_host',
            1234,
            b'some_test_data',
            (
                b'ICAP/1.0 200 OK\r\n'
                b'Encapsulated: res-body=0\r\n'
                b'\r\n'
                b'8\r\n'
                b'infected\r\n'
                b'0\r\n'
                b'\r\n'
            ),
            DEFAULT_EXPECTED_REQUEST,
            200,
            'OK',
            {'encapsulated': 'res-body=0'},
            None,
            None,
            None,
            b'infected',
        ),
        (
            'some_remote_host',
            1234,
            b'some_test_data',
            (
                b'ICAP/1.0 200 OK\r\n'
                b'Connection: close\r\n'
                b'Server: C-ICAP/1.0\r\n'
                b'Encapsulated: res-body=0, res-hdr=18\r\n'
                b'\r\n'
                b'8\r\n'
                b'infected\r\n'
                b'0\r\n'
                b'\r\n'
                b'HTTP/1.0 403 Forbidden\r\n'
                b'Content-type: text/html\r\n'
                b'Content-length: 8\r\n'
                b'Date: Thu Aug 12 2021 15:57:27 GMT\r\n'
                b'X-Infection-Found: WIN95.CIH\r\n'
                b'\r\n'
            ),
            DEFAULT_EXPECTED_REQUEST,
            200,
            'OK',
            {
                'encapsulated': 'res-body=0, res-hdr=18',
                'server': 'C-ICAP/1.0',
                'connection': 'close',
            },
            403,
            'Forbidden',
            {
                'content-type': 'text/html',
                'x-infection-found': 'WIN95.CIH',
                'content-length': '8',
                'date': 'Thu Aug 12 2021 15:57:27 GMT',
            },
            b'infected',
        ),
        (
            'some_remote_host',
            1234,
            b'some_test_data',
            DEFAULT_RESPONSE,
            DEFAULT_EXPECTED_REQUEST,
            200,
            'OK',
            {
                'encapsulated': (
                    'res-body=0, res-hdr=18, req-hdr=154, req-body=219, '
                    'opt-hdr=243, opt-body=288'
                ),
                'server': 'C-ICAP/1.0',
                'connection': 'close',
            },
            200,
            'OK',
            {'content-type': 'text/plain', 'content-length': '14'},
            b'some_test_data',
        ),
    ],
)
async def test_reqmod(
        mock_asyncio_connection,
        remote_host,
        remote_port,
        data,
        response_data,
        expected_request_data,
        expected_icap_status,
        expected_icap_reason,
        expected_icap_headers,
        expected_http_status,
        expected_http_reason,
        expected_http_headers,
        expected_http_body,
):
    mocked_connection, _, mocked_writer = mock_asyncio_connection(
        mocked_host=remote_host, data_to_read=response_data,
    )
    conn = async_icap.Connection(
        remote_host=remote_host, remote_port=remote_port,
    )
    response = await conn.reqmod(data)

    (connect_call,) = mocked_connection.calls
    assert connect_call['host'] == remote_host
    assert connect_call['port'] == remote_port

    assert mocked_writer.data_written == expected_request_data

    assert response.icap_status == expected_icap_status
    assert response.icap_reason == expected_icap_reason
    assert response.icap_headers == expected_icap_headers
    assert response.http_status == expected_http_status
    assert response.http_reason == expected_http_reason
    assert response.http_headers == expected_http_headers
    assert response.http_body == expected_http_body


@pytest.mark.parametrize(
    'response_data, connect_exception, read_exceptions, write_exceptions, '
    'expected_exception',
    [
        (DEFAULT_RESPONSE, OSError, None, None, async_icap.NetworkError),
        (
            DEFAULT_RESPONSE,
            None,
            [None, None, asyncio.IncompleteReadError(b'123', 10)],
            None,
            async_icap.NetworkError,
        ),
        (
            DEFAULT_RESPONSE,
            None,
            [None, ConnectionError],
            None,
            async_icap.NetworkError,
        ),
        (
            DEFAULT_RESPONSE,
            None,
            None,
            [ConnectionError],
            async_icap.NetworkError,
        ),
        (
            DEFAULT_RESPONSE,
            None,
            None,
            [None, None, ConnectionError],
            async_icap.NetworkError,
        ),
        # Wrong ICAP header
        (
            (
                b'ICAP/1.0 200 OK\r\n'
                b'Encapsulatedres-hdr=0, res-body=74\r\n'
                b'\r\n'
                b'HTTP/1.0 200 OK\r\n'
                b'Content-type: text/html\r\n'
                b'X-Infection-Found: WIN95.CIH\r\n'
                b'\r\n'
                b'8\r\n'
                b'infected\r\n'
                b'0\r\n'
                b'\r\n'
            ),
            None,
            None,
            None,
            async_icap.InvalidResponseError,
        ),
        # Wrong ICAP message
        (
            (
                b'ICAP/1.0 200OK\r\n'
                b'Encapsulated: res-hdr=0, res-body=74\r\n'
                b'\r\n'
                b'HTTP/1.0 200 OK\r\n'
                b'Content-type: text/html\r\n'
                b'X-Infection-Found: WIN95.CIH\r\n'
                b'\r\n'
                b'8\r\n'
                b'infected\r\n'
                b'0\r\n'
                b'\r\n'
            ),
            None,
            None,
            None,
            async_icap.InvalidResponseError,
        ),
        # Invalid Encapsulated header
        (
            (
                b'ICAP/1.0 200 OK\r\n'
                b'Encapsulated: hfsjkhdesjhgjlk\r\n'
                b'\r\n'
                b'HTTP/1.0 200 OK\r\n'
                b'Content-type: text/html\r\n'
                b'X-Infection-Found: WIN95.CIH\r\n'
                b'\r\n'
                b'8\r\n'
                b'infected\r\n'
                b'0\r\n'
                b'\r\n'
            ),
            None,
            None,
            None,
            async_icap.InvalidResponseError,
        ),
        # Wrong res-body offset in Encapsulated header
        (
            (
                b'ICAP/1.0 200 OK\r\n'
                b'Encapsulated: res-hdr=0, res-body=10\r\n'
                b'\r\n'
                b'HTTP/1.0 200 OK\r\n'
                b'Content-type: text/html\r\n'
                b'X-Infection-Found: WIN95.CIH\r\n'
                b'\r\n'
                b'8\r\n'
                b'infected\r\n'
                b'0\r\n'
                b'\r\n'
            ),
            None,
            None,
            None,
            async_icap.InvalidResponseError,
        ),
        # Wrong HTTP header
        (
            (
                b'ICAP/1.0 200 OK\r\n'
                b'Encapsulated: res-hdr=0, res-body=74\r\n'
                b'\r\n'
                b'HTTP/1.0 200 OK\r\n'
                b'Content-typetext/html\r\n'
                b'X-Infection-Found: WIN95.CIH\r\n'
                b'\r\n'
                b'8\r\n'
                b'infected\r\n'
                b'0\r\n'
                b'\r\n'
            ),
            None,
            None,
            None,
            async_icap.InvalidResponseError,
        ),
        # Wrong HTTP message
        (
            (
                b'ICAP/1.0 200 OK\r\n'
                b'Encapsulated: res-hdr=0, res-body=74\r\n'
                b'\r\n'
                b'HTTP/1.0200 OK\r\n'
                b'Content-type: text/html\r\n'
                b'X-Infection-Found: WIN95.CIH\r\n'
                b'\r\n'
                b'8\r\n'
                b'infected\r\n'
                b'0\r\n'
                b'\r\n'
            ),
            None,
            None,
            None,
            async_icap.InvalidResponseError,
        ),
        # Wrong body chunk length
        (
            (
                b'ICAP/1.0 200 OK\r\n'
                b'Encapsulated: res-hdr=0, res-body=74\r\n'
                b'\r\n'
                b'HTTP/1.0 200 OK\r\n'
                b'Content-type: text/html\r\n'
                b'X-Infection-Found: WIN95.CIH\r\n'
                b'\r\n'
                b'5\r\n'
                b'infected\r\n'
                b'0\r\n'
                b'\r\n'
            ),
            None,
            None,
            None,
            async_icap.InvalidResponseError,
        ),
    ],
)
async def test_reqmod_error(
        mock_asyncio_connection,
        response_data,
        connect_exception,
        read_exceptions,
        write_exceptions,
        expected_exception,
):
    mock_asyncio_connection(
        mocked_host='some_remote_host',
        connect_exception=connect_exception,
        read_exceptions=read_exceptions,
        write_exceptions=write_exceptions,
        data_to_read=response_data,
    )
    conn = async_icap.Connection(
        remote_host='some_remote_host', remote_port=1234,
    )
    with pytest.raises(expected_exception):
        await conn.reqmod(b'some_test_data')
