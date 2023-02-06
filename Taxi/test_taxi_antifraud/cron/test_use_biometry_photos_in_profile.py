import datetime

from aiohttp import web
import asyncpg
import pytest

from taxi_antifraud.crontasks import use_biometry_photos_in_profile
from taxi_antifraud.generated.cron import run_cron
from test_taxi_antifraud.cron.utils import state as state_module


async def _get_all_drivers_with_confirmation(pool: asyncpg.Pool) -> list:
    query = """
        select
            *
        from
            driver_confirmations.drivers_with_confirmation
        """
    async with pool.acquire() as connection:
        return list(map(dict, await connection.fetch(query)))


@pytest.mark.config(
    AFS_CRON_BIOMETRY_PHOTOS_ENABLED=True,
    AFS_CRON_BIOMETRY_PHOTOS_SEND_ENABLE=True,
)
@pytest.mark.now('2021-09-21T00:15:15.677Z+03:00')
async def test_cron(
        cron_context,
        patch_aiohttp_session,
        mock_quality_control_py3,
        mock_udriver_photos,
        mock_parks,
        response_mock,
):
    @mock_quality_control_py3('/api/v1/pass/list')
    async def _api_v1_pass_list(request):
        assert request.method == 'GET'
        if request.query.get('cursor') == 'end':
            return web.json_response(
                data=dict(
                    modified='2020-01-01T00:00:00', cursor='end', items=[],
                ),
            )
        return web.json_response(
            data=dict(
                modified='2020-01-01T00:00:00',
                cursor='end',
                items=[
                    {
                        'id': 'some_pass_id',
                        'status': 'NEW',
                        'entity_id': 'somepark_somedriver',
                        'exam': 'biometry',
                        'entity_type': 'driver',
                        'modified': '2020-01-01T00:00:00',
                        'media': [{'url': '', 'code': '', 'required': True}],
                        'data': [
                            {
                                'field': 'agree_to_use_for_profile_photo',
                                'required': False,
                            },
                        ],
                    },
                ],
            ),
        )

    @mock_quality_control_py3('/api/v1/pass/media')
    async def _api_v1_pass_media(request):
        return web.Response(text='I am JPEG')

    @mock_udriver_photos('/driver-photos/v1/photos/status')
    async def _api_v1_check_qc_pass(request):
        assert request.method == 'GET'
        return web.json_response(
            data={
                'action_key': '',
                'description_key': '',
                'text_key': '',
                'title_key': '',
                'status': 'no_photo',
            },
        )

    @mock_parks('/driver-profiles/photo')
    async def _parks_driver_profiles_photo(request):
        return web.json_response(data={})

    await state_module.initialize_state_table(
        cron_context.pg.master_pool,
        use_biometry_photos_in_profile.CURSOR_STATE_NAME,
    )

    await run_cron.main(
        ['taxi_antifraud.crontasks.use_biometry_photos_in_profile', '-t', '0'],
    )

    assert [
        list(_parks_driver_profiles_photo.next_call()['request'].query.items())
        for _ in range(_parks_driver_profiles_photo.times_called)
    ] == [[('park_id', 'somepark'), ('driver_profile_id', 'somedriver')]]

    assert await state_module.get_all_cron_state(
        cron_context.pg.master_pool,
    ) == {'use_biometry_photos_in_profile_cursor': 'end'}

    assert (
        await _get_all_drivers_with_confirmation(cron_context.pg.master_pool)
        == [
            {
                'db_id': 'somepark',
                'driver_uuid': 'somedriver',
                'last_sent_to_moderation': datetime.datetime(
                    2021,
                    9,
                    21,
                    21,
                    15,
                    15,
                    677000,
                    tzinfo=datetime.timezone.utc,
                ),
            },
        ]
    )
