# pylint: disable=redefined-outer-name
import datetime
import json
import logging

from aiohttp import web
import pytest

from driver_event_detector.generated.cron import run_cron

UNIQUE_DRIVER_ID = 'test_unique_driver_id'


@pytest.mark.now('2020-03-21 10:00:00')
@pytest.mark.pgsql(
    'driver_event_detector',
    files=['fill_pg_matched_drivers.sql', 'pg_tokens_insert.sql'],
)
@pytest.mark.config(
    DRIVER_EVENT_DETECTOR_KD_POST_PARAMS={'radius': 5},
    DRIVER_EVENT_DETECTOR_KD_HEADER={'Host': 'example.com'},
    DRIVER_EVENT_DETECTOR_COORDS={'city': [[55.683201, 37.6076357]]},
    DRIVER_EVENT_DETECTOR_KD_URL='example.com/get',
    DRIVER_EVENT_DETECTOR_CONFIGS={
        'num_workers': 2,
        'batch_size': 2,
        'is_kd_parser_running': True,
    },
)
async def test_detect_driver_events_parse_events(
        patch, caplog, response_mock, mock_unique_drivers, pgsql,
):
    @patch('aiohttp.ClientSession.post')
    async def _post(*args, **kwargs):
        return response_mock(
            json={
                'drivers': [
                    # this driver is too far
                    {
                        'pk_id': 13865466,
                        'id': '13cd49ec8f5e07b00ee18',
                        'lt': '55.6814775',
                        'ln': '38.6582085',
                        'direction': '0',
                        'CarColorCode': '000000',
                        'CarTitleColorCode': 'ffffff',
                    },
                    # this driver is fake
                    {
                        'pk_id': 13865466,
                        'id': '13cd49ec8f5e07b00ee1fa',
                        'lt': 55.6814775,
                        'ln': 38.6582085,
                        'direction': 0,
                        'CarColorCode': '000000',
                        'CarTitleColorCode': 'ffffff',
                    },
                    {
                        'pk_id': 12254650,
                        'id': 'non_matched_id',
                        'lt': '55.6822812',
                        'ln': '37.6652931',
                        'direction': '5',
                        'CarColorCode': '000000',
                        'CarTitleColorCode': 'ffffff',
                    },
                    {
                        'pk_id': 12254650,
                        'id': '0000ab732bcee0b3b6fa6977e45fdd79',
                        'lt': '55.6821812',
                        'ln': '37.6652931',
                        'direction': '5',
                        'CarColorCode': '000000',
                        'CarTitleColorCode': 'ffffff',
                    },
                    {
                        'pk_id': 12254652,
                        'id': '0000ab732bcee0b3b6fa6977e45fdd70',
                        'lt': '55.6821812',
                        'ln': '37.6652931',
                        'direction': '5',
                        'CarColorCode': '000000',
                        'CarTitleColorCode': 'ffffff',
                    },
                ],
            },
        )

    @mock_unique_drivers('/v1/driver/uniques/retrieve_by_profiles')
    async def handler(request):  # pylint: disable=W0612
        profile_ids = request.json['profile_id_in_set']
        return web.json_response(
            {
                'uniques': [
                    {
                        'park_driver_profile_id': profile_ids[0],
                        'data': {'unique_driver_id': UNIQUE_DRIVER_ID},
                    },
                    {'park_driver_profile_id': profile_ids[1], 'data': None},
                ],
            },
        )

    caplog.set_level(logging.INFO, logger='taxi.opentracing.reporter')

    await run_cron.main(
        ['driver_event_detector.crontasks.detect_driver_events', '-t', '0'],
    )

    records = [
        json.loads(x.message)
        for x in caplog.records
        if 'timestamp' in getattr(x, 'message', '{}')
    ]

    assert records == [
        {
            'car_class': 'any',
            'city': 'city',
            'cnt': 1,
            'driver_ids': None,
            'dt': '2020-03-21',
            'dttm_utc_1_min': '2020-03-21 10:00:00',
            'id': 'non_matched_id',
            'lat': 55.6822812,
            'lon': 37.6652931,
            'quadkey': '120310101302300',
            'timestamp': 1584784800,
            'ts_1_min': 1584784800,
            'udid': None,
            'dbid_uuids': [],
        },
        {
            'car_class': 'any',
            'city': 'city',
            'cnt': 1,
            'driver_ids': ['52b1fd1415a72575a42dbe599'],
            'dt': '2020-03-21',
            'dttm_utc_1_min': '2020-03-21 10:00:00',
            'id': '0000ab732bcee0b3b6fa6977e45fdd79',
            'lat': 55.6821812,
            'lon': 37.6652931,
            'quadkey': '120310101302300',
            'timestamp': 1584784800,
            'ts_1_min': 1584784800,
            'udid': UNIQUE_DRIVER_ID,
            'dbid_uuids': ['test_dbid_uuid'],
        },
        {
            'car_class': 'any',
            'city': 'city',
            'cnt': 1,
            'driver_ids': ['52b1fd1415a72575a42dbe590'],
            'dt': '2020-03-21',
            'dttm_utc_1_min': '2020-03-21 10:00:00',
            'id': '0000ab732bcee0b3b6fa6977e45fdd70',
            'lat': 55.6821812,
            'lon': 37.6652931,
            'quadkey': '120310101302300',
            'timestamp': 1584784800,
            'ts_1_min': 1584784800,
            'udid': None,
            'dbid_uuids': [],
        },
    ]

    cursor = pgsql['driver_event_detector'].cursor()
    cursor.execute('SELECT * FROM driver_event_detector.tokens ')
    num_rows = 0
    for row in cursor:
        assert row[1] == datetime.datetime(
            year=2020, month=3, day=20, minute=1,
        )
        assert row[2] == 'kd'
        assert row[3] == datetime.datetime(year=2020, month=3, day=20)
        num_rows += 1

    assert num_rows == 2
