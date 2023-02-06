# pylint: disable=import-error,too-many-lines
# flake8: noqa: E501

# All these tests must go once we switch from yagr to FTS

import datetime

from dap_tools.dap import dap_fixture  # noqa: F401 C5521
import pytest


def check_polling_header(header):
    parts = header.split(', ')
    parts.sort()
    assert parts == [
        'background=1200s',
        'full=600s',
        'idle=1800s',
        'powersaving=1200s',
    ]


@pytest.mark.now('2019-09-11T13:42:15+0300')
@pytest.mark.config(
    YAGR_DISCARD_POINTS_WITH_BAD_TIMESTAMP={
        'enabled': False,
        'future_boundary': 60,
        'past_boundary': 7200,
    },
    CONTRACTOR_TRANSPORT_CACHE_SETTINGS={
        'contractor-fts-receiver': {
            'cache_enabled': True,
            'batch_size': 1,
            'only_active_contractors': True,
        },
    },
    CONTRACTOR_FTS_USE_FTS={'common_position_store': 0},
)
@pytest.mark.parametrize(
    'user_agent,app_family',
    [
        ('Taximeter 9.1 (1234)', 'taximeter'),
        ('Taximeter-Uber 9.1 (1234)', 'uberdriver'),
    ],
)
async def test_driver_position_store_basic_check(
        taxi_contractor_fts_receiver,
        dap,
        testpoint,
        user_agent,
        app_family,
        contractor_transport_request,
        mockserver,
):
    unix_ts = int(
        datetime.datetime(
            2019,
            9,
            11,
            13,
            42,
            15,
            tzinfo=datetime.timezone(datetime.timedelta(hours=3)),
        ).timestamp()
        * 1000,
    )

    @mockserver.json_handler('/yagr/service/v2/position/store')
    def mock_yagr(request):
        assert request.json == {
            'contractor_id': {'dbid': 'berty', 'uuid': 'qwerty1'},
            'positions': [
                {
                    'accuracy': 5.0,
                    'altitude': 9.0,
                    'direction': 23,
                    'lat': 57.4,
                    'lon': 30.2,
                    'source': 'Verified',
                    'speed': 10.0,
                    'unix_timestamp': unix_ts,
                },
                {
                    'accuracy': 3.0,
                    'altitude': 15.0,
                    'direction': 25,
                    'lat': 58.0,
                    'lon': 31.0,
                    'source': 'AndroidNetwork',
                    'speed': 11.0,
                    'unix_timestamp': unix_ts,
                },
                {
                    'accuracy': 1.0,
                    'altitude': 20.0,
                    'direction': 20,
                    'lat': 59.0,
                    'lon': 29.0,
                    'source': 'YandexLbsIp',
                    'speed': 20.0,
                    'unix_timestamp': unix_ts,
                },
            ],
        }
        return mockserver.make_response(
            status=200, headers={'X-Polling-Power-Policy': 'none'},
        )

    park_id = 'berty'
    driver_id = 'qwerty1'
    taxi_contractor_fts_receiver = dap.create_driver_wrapper(
        taxi_contractor_fts_receiver,
        driver_uuid=driver_id,
        driver_dbid=park_id,
        user_agent=user_agent,
    )

    data_args = {'positions': []}

    # 1st pos
    first_position = {
        'lon': 30.20,
        'lat': 57.40,
        'source': 'Verified',
        'direction': 23,
        'speed': 10.0,
        'accuracy': 5,
        'altitude': 9,
        'unix_timestamp': unix_ts,
    }
    data_args['positions'].append(first_position)

    # 2nd pos
    second_position = {
        'lon': 31.0,
        'lat': 58.0,
        'source': 'AndroidNetwork',
        'direction': 25,
        'speed': 11.0,
        'accuracy': 3,
        'altitude': 15,
        'unix_timestamp': unix_ts,
    }
    data_args['positions'].append(second_position)

    # 3rd pos
    third_position = {
        'lon': 29.0,
        'lat': 59.0,
        'source': 'YandexLbsIp',
        'direction': 20,
        'speed': 20.0,
        'accuracy': 1,
        'altitude': 20,
        'unix_timestamp': unix_ts,
    }
    data_args['positions'].append(third_position)

    headers = {'Accept-Language': 'ru'}
    response = await taxi_contractor_fts_receiver.post(
        '/driver/v1/position/store', json=data_args, headers=headers,
    )
    assert response.status_code == 200
    check_polling_header(response.headers['X-Polling-Power-Policy'])
    assert response.json() == {}

    assert mock_yagr.times_called == 1
