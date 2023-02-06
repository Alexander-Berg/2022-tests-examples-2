from aiohttp import web
import asyncpg
import pytest

from taxi_antifraud.crontasks import ban_drivers
from taxi_antifraud.generated.cron import run_cron
from taxi_antifraud.generated.cron.yt_wrapper import plugin as yt_plugin
from test_taxi_antifraud.cron.utils import mock
from test_taxi_antifraud.cron.utils import state

YT_DIRECTORY_PATH = '//home/taxi-fraud/unittests/kopatel'
YT_TABLE_PATH_BLOCKLIST = YT_DIRECTORY_PATH + '/to_ban_blocklist'

CURSOR_BLOCKLIST_STATE_NAME = ban_drivers.CURSOR_BLOCKLIST_STATE_NAME


async def _prepare_data(
        taximeter_data: dict,
        blocklist_data: dict,
        yt_client: yt_plugin.AsyncYTClient,
        master_pool: asyncpg.Pool,
):
    await state.initialize_state_table(
        master_pool, CURSOR_BLOCKLIST_STATE_NAME,
    )
    yt_client.create(
        'map_node',
        path=YT_DIRECTORY_PATH,
        recursive=True,
        ignore_existing=True,
    )
    yt_client.write_table(YT_TABLE_PATH_BLOCKLIST, blocklist_data)


def _mock_ban_drivers_blocklist(mock_blocklist):
    @mock_blocklist('/internal/blocklist/v1/add')
    def _ban_drivers_blocklist(request):
        return web.json_response(data=dict(block_id='block_id'))

    return _ban_drivers_blocklist


@pytest.mark.config(
    AFS_CRON_BAN_DRIVERS_ENABLED=True,
    AFS_CRON_BAN_DRIVERS_USING_BLOCKLIST_INPUT_SUFFIX='kopatel/to_ban_blocklist',  # noqa: E501 pylint: disable=line-too-long
    AFS_CRON_BAN_DRIVERS_SLEEP_TIME_SECONDS=0.01,
)
@pytest.mark.now('2020-08-05T00:58:04')
@pytest.mark.parametrize(
    'blocklist_data,expected_blocklist_requests',
    [
        (
            [
                {
                    'driver_license_personal_id': (
                        '06e273a2f46a4f8ca5068ed1ad0b73a0'
                    ),
                    'reason': 'Нарушение сервисных стандартов.',
                    'mechanics': 'taximeter',
                    'park_id': None,
                    'comment': 'Забанил ради ржаки',
                    'expires': '2030-01-01T23:00:10+03:00',
                },
                {
                    'driver_license_personal_id': (
                        '4897b74ae86649018ab2b71e56595d73'
                    ),
                    'reason': 'very bad',
                    'mechanics': 'antifraud_face_id',
                    'park_id': 'Sea_bream',
                    'comment': 'Забанил фаната Спартака',
                    'expires': '2030-01-01T23:20:40',
                },
                {
                    'driver_license_personal_id': (
                        'ca44836f7dd64edb9c43f0408dea4eaf'
                    ),
                    'reason': 'too bad',
                    'mechanics': 'taximeter',
                    'park_id': 'Switzerland_park',
                    'comment': 'Забанил за несмешную шутку',
                    'expires': '2030-12-12',
                },
                {
                    'driver_license_personal_id': (
                        'e434e5d8405845bfbe25cd420e52fd76'
                    ),
                    'reason': 'so bad',
                    'mechanics': 'antifraud_face_id',
                    'park_id': 'Sokolniki',
                    'comment': 'Забанил, чтобы почувствовать превосходство',
                    'expires': None,
                },
            ],
            [
                {
                    'block': {
                        'predicate_id': '33333333-3333-3333-3333-333333333333',
                        'kwargs': {
                            'license_id': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                        },
                        'reason': {'key': 'Нарушение сервисных стандартов.'},
                        'comment': 'Забанил ради ржаки',
                        'mechanics': 'taximeter',
                        'expires': '2030-01-01T23:00:10+03:00',
                    },
                    'identity': {
                        'name': 'robot-taxi-afs-tools',
                        'type': 'service',
                    },
                },
                {
                    'block': {
                        'predicate_id': '44444444-4444-4444-4444-444444444444',
                        'kwargs': {
                            'license_id': '4897b74ae86649018ab2b71e56595d73',
                            'park_id': 'Sea_bream',
                        },
                        'reason': {'key': 'very bad'},
                        'comment': 'Забанил фаната Спартака',
                        'mechanics': 'antifraud_face_id',
                        'expires': '2030-01-02T02:20:40+03:00',
                    },
                    'identity': {
                        'name': 'robot-taxi-afs-tools',
                        'type': 'service',
                    },
                },
                {
                    'block': {
                        'predicate_id': '44444444-4444-4444-4444-444444444444',
                        'kwargs': {
                            'license_id': 'ca44836f7dd64edb9c43f0408dea4eaf',
                            'park_id': 'Switzerland_park',
                        },
                        'reason': {'key': 'too bad'},
                        'comment': 'Забанил за несмешную шутку',
                        'mechanics': 'taximeter',
                        'expires': '2030-12-12T03:00:00+03:00',
                    },
                    'identity': {
                        'name': 'robot-taxi-afs-tools',
                        'type': 'service',
                    },
                },
                {
                    'block': {
                        'predicate_id': '44444444-4444-4444-4444-444444444444',
                        'kwargs': {
                            'license_id': 'e434e5d8405845bfbe25cd420e52fd76',
                            'park_id': 'Sokolniki',
                        },
                        'reason': {'key': 'so bad'},
                        'comment': (
                            'Забанил, чтобы почувствовать превосходство'
                        ),
                        'mechanics': 'antifraud_face_id',
                    },
                    'identity': {
                        'name': 'robot-taxi-afs-tools',
                        'type': 'service',
                    },
                },
            ],
        ),
    ],
)
async def test_blocklist_cron(
        mock_blocklist,
        yt_apply,
        yt_client,
        db,
        cron_context,
        blocklist_data,
        expected_blocklist_requests,
):
    _ban_drivers_blocklist = _mock_ban_drivers_blocklist(mock_blocklist)

    master_pool = cron_context.pg.master_pool
    await _prepare_data([], blocklist_data, yt_client, master_pool)

    await run_cron.main(['taxi_antifraud.crontasks.ban_drivers', '-t', '0'])

    assert (
        mock.get_requests(_ban_drivers_blocklist)
        == expected_blocklist_requests
    )

    assert await state.get_all_cron_state(master_pool) == {
        CURSOR_BLOCKLIST_STATE_NAME: str(len(blocklist_data)),
    }
