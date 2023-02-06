from aiohttp import web
import pytest

from taxi_antifraud.generated.cron import run_cron
from test_taxi_antifraud.cron.utils import mock


YT_DIRECTORY_PATH = '//home/taxi-fraud/unittests/kopatel'
YT_PHONES_TABLE_PATH = YT_DIRECTORY_PATH + '/phones_to_ban'
YT_DEVICES_TABLE_PATH = YT_DIRECTORY_PATH + '/devices_to_ban'


async def _initialize_cron_state(pool) -> None:
    query = """
        insert into
            crontasks_common.cronstate
        values
            ('ban_users_phones_cursor', 0),
            ('ban_users_devices_cursor', 0);
        """
    async with pool.acquire() as connection:
        await connection.execute(query)


async def _get_all_cron_state(pool):
    query = """
        select
            *
        from
            crontasks_common.cronstate
        """
    async with pool.acquire() as connection:
        return [dict(x) for x in await connection.fetch(query)]


@pytest.fixture
def mock_personal(patch):
    @patch('taxi.clients.personal.PersonalApiClient.retrieve')
    async def _retrieve(data_type, request_id, *args, **kwargs):
        assert request_id.endswith('_pd_id')
        return {'phone': request_id[:-6]}


@pytest.mark.config(
    AFS_CRON_BAN_USERS_ENABLED=True,
    AFS_CRON_BAN_USERS_INPUT_DEVICES_TABLE_SUFFIX='kopatel/devices_to_ban',
    AFS_CRON_BAN_USERS_INPUT_PHONES_TABLE_SUFFIX='kopatel/phones_to_ban',
    AFS_CRON_BAN_USERS_SLEEP_TIME_SECONDS=0.01,
)
@pytest.mark.now('2021-08-04T13:06:04')
@pytest.mark.parametrize(
    'phones_data,devices_data,expected_requests',
    [
        (
            [
                {
                    'personal_phone_id': '+79000000000_pd_id',
                    'reason': 'Нарушение сервисных стандартов.',
                    'till': '2022-01-01T00:00:00+03:00',
                    'ban_related_ids': False,
                },
                {
                    'personal_phone_id': '+79001110000_pd_id',
                    'reason': 'very bad',
                    'till': '2030-01-01T00:00:00',
                    'ban_related_ids': False,
                },
                {
                    'personal_phone_id': '+79002220000_pd_id',
                    'reason': 'too bad',
                    'till': '2030-01-01T23:20:40',
                    'ban_related_ids': True,
                },
                {
                    'personal_phone_id': '+79003330000_pd_id',
                    'reason': 'so bad',
                    'till': '2030-01-01T23:00:10Z+03:00',
                    'ban_related_ids': True,
                },
            ],
            [
                {
                    'device_id': 'some_device_id',
                    'reason': 'bad device',
                    'till': '2020-01-01Z00:00:00',
                },
            ],
            [
                {
                    'phone_type': 'all',
                    'reason': 'Нарушение сервисных стандартов.',
                    'till': '2022-01-01T00:00:00+03:00',
                    'type': 'phone',
                    'value': '+79000000000',
                },
                {
                    'phone_type': 'all',
                    'reason': 'very bad',
                    'till': '2030-01-01T03:00:00+03:00',
                    'type': 'phone',
                    'value': '+79001110000',
                },
                {
                    'phone_type': 'all',
                    'reason': 'too bad',
                    'till': '2030-01-02T02:20:40+03:00',
                    'type': 'all',
                    'value': '+79002220000',
                },
                {
                    'phone_type': 'all',
                    'reason': 'so bad',
                    'till': '2030-01-01T23:00:10+03:00',
                    'type': 'all',
                    'value': '+79003330000',
                },
                {
                    'reason': 'bad device',
                    'till': '2020-01-01T03:00:00+03:00',
                    'type': 'device',
                    'value': 'some_device_id',
                },
            ],
        ),
    ],
)
async def test_cron(
        mock_antifraud_py,
        mock_personal,  # pylint: disable=redefined-outer-name
        yt_apply,
        yt_client,
        cron_context,
        phones_data,
        devices_data,
        expected_requests,
):
    @mock_antifraud_py('/bad_users/v1/admin/user/ban')
    def _ban_drivers(request):
        assert request.method == 'POST'

        return web.json_response(data=dict())

    yt_client.create(
        'table',
        path=YT_PHONES_TABLE_PATH,
        recursive=True,
        ignore_existing=True,
    )
    yt_client.write_table(YT_PHONES_TABLE_PATH, phones_data)
    yt_client.create(
        'table',
        path=YT_DEVICES_TABLE_PATH,
        recursive=True,
        ignore_existing=True,
    )
    yt_client.write_table(YT_DEVICES_TABLE_PATH, devices_data)
    await _initialize_cron_state(cron_context.pg.master_pool)

    await run_cron.main(['taxi_antifraud.crontasks.ban_users', '-t', '0'])

    assert mock.get_requests(_ban_drivers) == expected_requests

    assert await _get_all_cron_state(cron_context.pg.master_pool) == [
        {
            'cursor_value': str(len(phones_data)),
            'state_name': 'ban_users_phones_cursor',
        },
        {
            'cursor_value': str(len(devices_data)),
            'state_name': 'ban_users_devices_cursor',
        },
    ]
