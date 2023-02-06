from aiohttp import web
import pytest

from taxi_antifraud.crontasks import ban_cars
from taxi_antifraud.generated.cron import run_cron
from test_taxi_antifraud.cron.utils import data as data_module
from test_taxi_antifraud.cron.utils import state

CURSOR_STATE_NAME = ban_cars.CURSOR_STATE_NAME

YT_DIRECTORY_PATH = '//home/taxi-fraud/unittests/kopatel'
YT_TABLE_PATH = YT_DIRECTORY_PATH + '/to_ban'


@pytest.mark.config(
    AFS_CRON_BAN_CARS_ENABLED=True,
    AFS_CRON_BAN_CARS_INPUT_TABLE_SUFFIX='kopatel/to_ban',
    AFS_CRON_BAN_CARS_SLEEP_TIME_SECONDS=0.01,
    AFS_CRON_CURSOR_USE_PGSQL='enabled',
)
@pytest.mark.now('2020-08-05T00:58:04')
async def test_cron(mock_blocklist, yt_apply, yt_client, cron_context, db):
    data = [
        {
            'car_number': '7ad36bc7560449998acbe2c57a75c293',
            'park_id': None,
            'reason_tanker_key': 'key1',
            'ban_duration_in_seconds': None,
            'inner_comment': 'antifraud_kopatel_TAXIFRAUD-1918',
            'mechanics': 'antifraud',
        },
        {
            'car_number': '7ad36bc7560449998acbe2c57a75c596',
            'park_id': '000002',
            'reason_tanker_key': 'key2',
            'ban_duration_in_seconds': 10,
            'inner_comment': 'antifraud_kopatel_TAXIFRAUD-1919',
            'mechanics': 'antifraud',
        },
        {
            'car_number': '7ad36bc7560449998acbe2c57a75c147',
            'park_id': '000002',
            'reason_tanker_key': 'key3',
            'ban_duration_in_seconds': 3600,
            'inner_comment': 'antifraud_kopatel_TAXIFRAUD-1920',
            'mechanics': 'antifraud',
        },
        {
            'car_number': '7ad36bc7560449998acbe2c57a75c752',
            'park_id': '000003',
            'reason_tanker_key': 'key4',
            'ban_duration_in_seconds': 86400,
            'inner_comment': 'antifraud_kopatel_TAXIFRAUD-1921',
            'mechanics': 'some_mechanics',
            'reason_parameters': {
                'car_number': 'some_number',
                'date': 'some_date',
            },
        },
    ]

    requests = {
        ('7ad36bc7560449998acbe2c57a75c293', None): {
            'block': {
                'predicate_id': '11111111-1111-1111-1111-111111111111',
                'kwargs': {'car_number': '7ad36bc7560449998acbe2c57a75c293'},
                'reason': {'key': 'key1'},
                'comment': 'antifraud_kopatel_TAXIFRAUD-1918',
                'mechanics': 'antifraud',
                'meta': {},
            },
            'identity': {'name': 'kopatel', 'type': 'service'},
        },
        ('7ad36bc7560449998acbe2c57a75c596', '000002'): {
            'block': {
                'predicate_id': '22222222-2222-2222-2222-222222222222',
                'kwargs': {
                    'car_number': '7ad36bc7560449998acbe2c57a75c596',
                    'park_id': '000002',
                },
                'reason': {'key': 'key2'},
                'comment': 'antifraud_kopatel_TAXIFRAUD-1919',
                'expires': '2020-08-05T03:58:14+03:00',
                'mechanics': 'antifraud',
                'meta': {},
            },
            'identity': {'name': 'kopatel', 'type': 'service'},
        },
        ('7ad36bc7560449998acbe2c57a75c147', '000002'): {
            'block': {
                'predicate_id': '22222222-2222-2222-2222-222222222222',
                'kwargs': {
                    'car_number': '7ad36bc7560449998acbe2c57a75c147',
                    'park_id': '000002',
                },
                'reason': {'key': 'key3'},
                'comment': 'antifraud_kopatel_TAXIFRAUD-1920',
                'expires': '2020-08-05T04:58:04+03:00',
                'mechanics': 'antifraud',
                'meta': {},
            },
            'identity': {'name': 'kopatel', 'type': 'service'},
        },
        ('7ad36bc7560449998acbe2c57a75c752', '000003'): {
            'block': {
                'predicate_id': '22222222-2222-2222-2222-222222222222',
                'kwargs': {
                    'car_number': '7ad36bc7560449998acbe2c57a75c752',
                    'park_id': '000003',
                },
                'reason': {'key': 'key4'},
                'comment': 'antifraud_kopatel_TAXIFRAUD-1921',
                'expires': '2020-08-06T03:58:04+03:00',
                'mechanics': 'some_mechanics',
                'meta': {'car_number': 'some_number', 'date': 'some_date'},
            },
            'identity': {'name': 'kopatel', 'type': 'service'},
        },
    }

    @mock_blocklist('/internal/blocklist/v1/add')
    def _ban_cars(request):
        assert request.method == 'POST'

        kwargs = request.json['block']['kwargs']
        car_number = kwargs['car_number']
        park_id = kwargs['park_id'] if 'park_id' in kwargs else None

        assert request.json == requests.pop((car_number, park_id), None)

        return web.json_response(data=dict(block_id='block_id'))

    master_pool = cron_context.pg.master_pool
    await data_module.prepare_data(
        data,
        yt_client,
        master_pool,
        CURSOR_STATE_NAME,
        YT_DIRECTORY_PATH,
        YT_TABLE_PATH,
    )

    await run_cron.main(['taxi_antifraud.crontasks.ban_cars', '-t', '0'])

    assert _ban_cars.times_called == 4

    assert await state.get_all_cron_state(master_pool) == {
        CURSOR_STATE_NAME: str(len(data)),
    }
