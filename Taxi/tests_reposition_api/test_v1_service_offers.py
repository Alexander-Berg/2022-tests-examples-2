# pylint: disable=C5521, C0103
import datetime

import pytest
import pytz

from .fbs import ServiceOffersFbs

fbs_handler = ServiceOffersFbs()


@pytest.mark.now('2017-11-19T16:47:54.721+00:00')
async def test_empty(taxi_reposition_api):
    response = await taxi_reposition_api.post('/v1/service/offers', params={})

    assert response.status_code == 200
    assert fbs_handler.parse_response(response.content) == {'offers': []}


@pytest.mark.now('2018-11-26T11:00:00.721+00:00')
@pytest.mark.pgsql(
    'reposition', files=['mode_poi.sql', 'drivers.sql', 'offers.sql'],
)
async def test_simple(taxi_reposition_api):
    response = await taxi_reposition_api.post('/v1/service/offers', params={})

    assert response.status_code == 200
    assert fbs_handler.parse_response(response.content) == {
        'offers': [
            {
                'park_id': 'dbid777',
                'driver_profile_id': 'uuid',
                'mode_name': 'poi',
                'valid_until': datetime.datetime(
                    2018, 11, 26, 12, 45, tzinfo=pytz.timezone('UTC'),
                ),
                'created': datetime.datetime(
                    2018, 11, 26, 12, 30, tzinfo=pytz.timezone('UTC'),
                ),
                'used': True,
                'point': [30.15629768371582, 59.895389556884766],
            },
            {
                'park_id': 'dbid777',
                'driver_profile_id': 'uuid1',
                'mode_name': 'poi',
                'valid_until': datetime.datetime(
                    2018, 11, 26, 12, 0, tzinfo=pytz.timezone('UTC'),
                ),
                'created': datetime.datetime(
                    2018, 11, 26, 11, 45, tzinfo=pytz.timezone('UTC'),
                ),
                'used': True,
                'point': [37.19464111328125, 55.47898483276367],
            },
            {
                'park_id': 'dbid777',
                'driver_profile_id': 'uuid2',
                'mode_name': 'poi',
                'valid_until': datetime.datetime(
                    2018, 11, 26, 14, 0, tzinfo=pytz.timezone('UTC'),
                ),
                'created': datetime.datetime(
                    2018, 11, 26, 13, 45, tzinfo=pytz.timezone('UTC'),
                ),
                'used': False,
                'point': [37.19464111328125, 55.47898483276367],
            },
            {
                'park_id': 'dbid777',
                'driver_profile_id': 'uuid2',
                'mode_name': 'poi',
                'valid_until': datetime.datetime(
                    2018, 11, 26, 11, 59, 59, tzinfo=pytz.timezone('UTC'),
                ),
                'created': datetime.datetime(
                    2018, 11, 26, 11, 43, 59, tzinfo=pytz.timezone('UTC'),
                ),
                'used': False,
                'point': [3.0, 4.0],
            },
            {
                'park_id': 'dbid777',
                'driver_profile_id': 'uuid3',
                'mode_name': 'poi',
                'valid_until': datetime.datetime(
                    2018, 11, 26, 13, 0, tzinfo=pytz.timezone('UTC'),
                ),
                'created': datetime.datetime(
                    2018, 11, 26, 12, 45, tzinfo=pytz.timezone('UTC'),
                ),
                'used': False,
                'point': [37.19464111328125, 55.47898483276367],
            },
        ],
    }


@pytest.mark.now('2018-11-26T12:00:00.721+00:00')
@pytest.mark.parametrize('time', [None, 60 * 60])
@pytest.mark.pgsql(
    'reposition', files=['mode_poi.sql', 'drivers.sql', 'offers.sql'],
)
async def test_created(taxi_reposition_api, time):
    expected_offers = [
        {
            'park_id': 'dbid777',
            'driver_profile_id': 'uuid',
            'mode_name': 'poi',
            'valid_until': datetime.datetime(
                2018, 11, 26, 12, 45, tzinfo=pytz.timezone('UTC'),
            ),
            'created': datetime.datetime(
                2018, 11, 26, 12, 30, tzinfo=pytz.timezone('UTC'),
            ),
            'used': True,
            'point': [30.15629768371582, 59.895389556884766],
        },
        {
            'park_id': 'dbid777',
            'driver_profile_id': 'uuid2',
            'mode_name': 'poi',
            'valid_until': datetime.datetime(
                2018, 11, 26, 14, 0, tzinfo=pytz.timezone('UTC'),
            ),
            'created': datetime.datetime(
                2018, 11, 26, 13, 45, tzinfo=pytz.timezone('UTC'),
            ),
            'used': False,
            'point': [37.19464111328125, 55.47898483276367],
        },
        {
            'park_id': 'dbid777',
            'driver_profile_id': 'uuid3',
            'mode_name': 'poi',
            'valid_until': datetime.datetime(
                2018, 11, 26, 13, 0, tzinfo=pytz.timezone('UTC'),
            ),
            'created': datetime.datetime(
                2018, 11, 26, 12, 45, tzinfo=pytz.timezone('UTC'),
            ),
            'used': False,
            'point': [37.19464111328125, 55.47898483276367],
        },
    ]

    if time:
        expected_offers.append(
            {
                'park_id': 'dbid777',
                'driver_profile_id': 'uuid2',
                'mode_name': 'poi',
                'valid_until': datetime.datetime(
                    2018, 11, 26, 11, 59, 59, tzinfo=pytz.timezone('UTC'),
                ),
                'created': datetime.datetime(
                    2018, 11, 26, 11, 43, 59, tzinfo=pytz.timezone('UTC'),
                ),
                'used': False,
                'point': [3.0, 4.0],
            },
        )
        expected_offers.append(
            {
                'park_id': 'dbid777',
                'driver_profile_id': 'uuid1',
                'mode_name': 'poi',
                'valid_until': datetime.datetime(
                    2018, 11, 26, 12, 0, tzinfo=pytz.timezone('UTC'),
                ),
                'created': datetime.datetime(
                    2018, 11, 26, 11, 45, tzinfo=pytz.timezone('UTC'),
                ),
                'used': True,
                'point': [37.19464111328125, 55.47898483276367],
            },
        )

    expected_offers = sorted(expected_offers, key=lambda i: i['created'])

    params = {'time_since_creation': time} if time else None
    response = await taxi_reposition_api.post(
        '/v1/service/offers', params=params,
    )

    assert response.status_code == 200

    actual_offers = fbs_handler.parse_response(response.content)['offers']
    actual_offers = sorted(actual_offers, key=lambda i: i['created'])

    assert actual_offers == expected_offers
