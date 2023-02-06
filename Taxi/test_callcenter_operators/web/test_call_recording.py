import collections
import io
import wave

import aiohttp
import aiohttp.web
import pytest


# Content length will be set automatically
WAV_RESPONSE_HEADERS = {
    'Server': 'nginx',
    'Date': 'Thu, 19 Mar 2020 09:17:59 GMT',
    'Content-Range': 'bytes 0-12/13',
    'Content-Type': 'application/octet-stream',
    'Connection': 'keep-alive',
    'Keep-Alive': 'timeout=60',
    'Accept-Ranges': 'bytes',
    'Etag': '"548d3168e33741aa613690f03e913fd2"',
    'Last-Modified': 'Sat, 14 Mar 2020 00:00:08 GMT',
    'X-Amz-Request-Id': '48200b23a416b1bc',
    'Access-Control-Allow-Origin': '*',
    'X-Robots-Tag': 'noindex, noarchive, nofollow',
}

WAV_REQUEST_HEADERS = {
    'Accept-Encoding': 'identity;q=1, *;q=0',
    'Range': 'bytes=0-',
    'User-Agent': 'user_agent',
    'Referer': 'tariff_editor_ref',
    'Host': 'taxi_callcenter_operators_web_upstream',
    'Accept': '*/*',
    'Accept-Language': 'ru,en;q=0.9',
    'Cache-Control': 'no-cache',
    'X-Forwarded-For': 'some_info',
    'X-Forwarded-Proto': 'https',
    'X-Real-IP': 'real_ip',
    'X-Ya-Service-Ticket': 'service_ticket',
    'X-YaRequestId': 'request_id',
    'X-Yandex-Login': 'login',
    'X-Yandex-Uid': 'uid',
    'sec-fetch-mode': 'no-cors',
    'sec-fetch-site': 'same-origin',
}


def _clear_ya_headers(headers):
    headers.pop('X-YaRequestId')
    headers.pop('X-YaSpanId')
    headers.pop('X-YaTraceId')
    return headers


WaveParams = collections.namedtuple(
    'wave_params', 'nchannels sampwidth framerate nframes comptype',
)


@pytest.mark.config(
    S3_CALLCENTER_CLIENT_QOS={
        '__default__': {
            'attempts': 2,
            'timeout-ms': 1000,
            'sleep-delay-ms': 10,
        },
    },
)
@pytest.mark.parametrize('s3_response_status', (200, 400, 404, 429, 500))
async def test_calls_recordings_v2(
        taxi_callcenter_operators_web, mockserver, s3_response_status,
):
    @mockserver.handler('/callcenter-s3', prefix=True)
    def _request(request, *args, **kwargs):

        if s3_response_status == 200:
            return aiohttp.web.Response(
                status=s3_response_status,
                body=b'some_wav_data',
                headers=WAV_RESPONSE_HEADERS,
            )
        return aiohttp.web.Response(status=s3_response_status)

    response = await taxi_callcenter_operators_web.get(
        '/cc/v1/callcenter-operators/v1/calls/recording'
        '?id=taxi-m9-qproc1.yndx.net-1584098667.3431&type=out',
        headers=WAV_REQUEST_HEADERS,
    )

    assert response.status == s3_response_status
    if response.status == 200:
        expected_headers = {}
        expected_headers.update(WAV_RESPONSE_HEADERS)
        expected_headers.update({'Content-Length': '13'})
        assert _clear_ya_headers(dict(response.headers)) == expected_headers
        assert await response.read() == b'some_wav_data'
    elif response.status == 400:
        assert response.headers['Content-Type'] == 'application/json'
        assert await response.json() == {
            'code': 'bad_request',
            'message': 'S3 bad request',
        }
    elif response.status == 404:
        assert response.headers['Content-Type'] == 'application/json'
        assert await response.json() == {
            'code': 'not_found',
            'message': (
                'Audio with id=taxi-m9-qproc1.yndx.net-1584098667.3431 '
                'and type=out not found'
            ),
        }
    elif response.status == 429:
        assert response.headers['Content-Type'] == 'application/json'
        assert await response.json() == {
            'code': 'too_many_requests',
            'message': 'S3 too many requests',
        }
    elif response.status == 500:
        assert response.headers['Content-Type'] == 'application/json'
        assert await response.json() == {
            'code': 'server_error',
            'message': 'Error on s3 server',
        }


@pytest.mark.config(
    S3_CALLCENTER_CLIENT_QOS={
        '__default__': {
            'attempts': 2,
            'timeout-ms': 1000,
            'sleep-delay-ms': 10,
        },
    },
)
@pytest.mark.parametrize(
    (
        'rec_id',
        'rec_type',
        'expected_response_status',
        'expected_response_length',
        'expected_response_headers',
        'expected_wav_params',
    ),
    [
        pytest.param(
            'nonexistent',
            'in',
            404,
            None,
            None,
            None,
            id='nonexistent call_id - 404',
        ),
        pytest.param(
            'dtmf',
            'nonexistent',
            404,
            None,
            None,
            None,
            id='nonexistent rec_type - 404',
        ),
        pytest.param(
            'dtmf',
            'in',
            200,
            2448,
            {
                'Content-Type': 'application/octet-stream',
                'Content-Length': '2448',
                # Content-Range is hardcoded in WAV_RESPONSE_HEADERS
                'Content-Range': 'bytes 0-12/13',
                'Accept-Ranges': 'bytes',
                'Content-Disposition': None,
            },
            WaveParams(
                nchannels=1,  # mono
                sampwidth=2,  # 16bit
                framerate=8000,
                nframes=1202,
                comptype='NONE',
            ),
            id='request in only',
        ),
        pytest.param(
            'dtmf',
            'out',
            200,
            6444,
            {
                'Content-Type': 'application/octet-stream',
                'Content-Length': '6444',
                # Content-Range is hardcoded in WAV_RESPONSE_HEADERS
                'Content-Range': 'bytes 0-12/13',
                'Accept-Ranges': 'bytes',
                'Content-Disposition': None,
            },
            WaveParams(
                nchannels=1,  # mono
                sampwidth=2,  # 16bit
                framerate=8000,
                nframes=3200,
                comptype='NONE',
            ),
            id='request out only',
        ),
        pytest.param(
            'dtmf',
            'mixed',
            200,
            12844,
            {
                'Content-Type': 'application/octet-stream',
                'Content-Length': '12844',
                'Content-Range': None,
                'Accept-Ranges': None,
                'Content-Disposition': 'attachment; filename="dtmf.wav"',
            },
            WaveParams(
                nchannels=2,  # stereo
                sampwidth=2,  # 16bit
                framerate=8000,
                nframes=3200,  # max of channels
                comptype='NONE',
            ),
            id='mixed',
        ),
        pytest.param(
            'dtmf2',
            'mixed',
            200,
            2448,
            {
                'Content-Type': 'application/octet-stream',
                'Content-Length': '2448',
                # Content-Range is hardcoded in WAV_RESPONSE_HEADERS
                'Content-Range': None,
                'Accept-Ranges': None,
                'Content-Disposition': 'attachment; filename="dtmf2.wav"',
            },
            WaveParams(
                nchannels=1,
                sampwidth=2,
                framerate=8000,
                nframes=1202,
                comptype='NONE',
            ),
            id='mixed - one channel absence',
        ),
    ],
)
async def test_calls_recordings_mixed_v2(
        taxi_callcenter_operators_web,
        mockserver,
        load_binary,
        rec_id,
        rec_type,
        expected_response_status,
        expected_response_length,
        expected_response_headers,
        expected_wav_params,
):
    @mockserver.handler('/callcenter-s3', prefix=True)
    def _request(request, *args, **kwargs):
        try:
            return aiohttp.web.Response(
                status=200,
                body=load_binary(request.url.split('/')[-1]),
                headers=WAV_RESPONSE_HEADERS,
            )
        except FileNotFoundError:
            return aiohttp.web.Response(status=404)

    def get_wave_params(wav_bytes):
        with wave.Wave_read(io.BytesIO(wav_bytes)) as wav:
            return WaveParams(
                nchannels=wav.getnchannels(),
                sampwidth=wav.getsampwidth(),
                framerate=wav.getframerate(),
                nframes=wav.getnframes(),
                comptype=wav.getcomptype(),
            )

    response = await taxi_callcenter_operators_web.get(
        '/cc/v1/callcenter-operators/v1/calls/recording'
        f'?id={rec_id}&type={rec_type}',
        headers=WAV_REQUEST_HEADERS,
    )
    assert response.status == expected_response_status
    response_bytes = await response.read()

    if expected_response_length is not None:
        assert len(response_bytes) == expected_response_length
    if expected_response_headers is not None:
        for key in expected_response_headers:
            header = response.headers.get(key, None)
            assert header == expected_response_headers[key]
    if expected_wav_params is not None:
        assert get_wave_params(response_bytes) == expected_wav_params
