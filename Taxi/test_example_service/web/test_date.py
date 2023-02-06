import json

import pytest

from . import common


@pytest.mark.parametrize(
    'params',
    [
        common.Params({'now_date': '2019-01-01'}, 200, {}),
        common.Params(
            {'now_date': 1},
            400,
            common.make_request_error(
                'Invalid value for now_date: 1 is not instance of str',
            ),
        ),
        common.Params(
            {'now_date': 'asdf'},
            400,
            common.make_request_error(
                'Invalid value for now_date: failed to parse date from '
                '\'asdf\'',
            ),
        ),
        common.Params({'now_datetime': '2019-01-01'}, 200, {}),
        common.Params(
            {'now_datetime': 1},
            400,
            common.make_request_error(
                'Invalid value for now_datetime: 1 is not instance of str',
            ),
        ),
        common.Params(
            {'now_datetime': 'asdf'},
            400,
            common.make_request_error(
                'Invalid value for now_datetime: '
                'failed to parse datetime from \'asdf\'',
            ),
        ),
    ],
)
async def test_dates(web_app_client, params):
    response = await web_app_client.post('/set_date', json=params.request)
    assert response.status == params.status
    assert await response.json() == params.response


async def test_date_time_iso_basic(web_app_client):
    response = await web_app_client.post(
        '/iso-basic-date', data='2018-01-28T12:08:48+0300',
    )
    assert response.status == 200
    assert await response.text() == '2018-01-29T12:08:48+0300'


@pytest.mark.parametrize(
    'tst_request, expected_res',
    [
        pytest.param(
            {
                'date-time': '2000-01-01T00:00:00.000120+00:00',
                'date-time-fraction': '2000-01-01T00:00:00.1+00:00',
                'date-time-iso-basic': '2000-01-01T00:00:00.000120+0000',
                'date-time-iso-basic-fraction': '2000-01-01T00:00:00.1+0000',
            },
            {
                'date-time': '2000-01-01T00:00:00.000120+00:00',
                'date-time-fraction': '2000-01-01T00:00:00.100000+00:00',
                'date-time-iso-basic': '2000-01-01T00:00:00+0000',  # backward
                'date-time-iso-basic-fraction': (
                    '2000-01-01T00:00:00.100000+0000'
                ),
            },
            id='default',
        ),
    ],
)
async def test_server_datetime_formats(
        tst_request, expected_res, web_app_client,
):
    resp = await web_app_client.post(
        '/serialize-datetime', data=json.dumps(tst_request),
    )
    assert resp.status == 200
    assert await resp.json() == expected_res
