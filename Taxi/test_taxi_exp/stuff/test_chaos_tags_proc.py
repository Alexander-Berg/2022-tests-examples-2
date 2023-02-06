import pytest

from taxi_exp import settings
from taxi_exp.generated.cron import run_cron as cron_run


@pytest.mark.config(
    TAXI_EXP_CHAOS_ENGINEERING_TAGS={
        'fallback_routestats': {
            'rotate_hours': 2,
            'percent': 5,
            'salt': 'salt1',
            'arg_name': 'phone_id',
            'base_tag': 'taxi_phone_id',
        },
        'fallback_totw': {
            'rotate_hours': 5,
            'percent': 10,
            'salt': 'salt2',
            'arg_name': 'phone_id',
            'base_tag': 'taxi_phone_id',
        },
    },
    EXP3_ADMIN_CONFIG={
        'features': {'backend': {'chaos_tags_enabled': True}},
        'settings': {
            'backend': {
                'trusted_file_lines_count_change_threshold': {
                    'absolute': 10,
                    'percentage': 20,
                },
            },
        },
    },
)
async def test_update_chaos_tag(taxi_exp_client, mockserver):
    # running cron
    @mockserver.json_handler('/taxi-exp/v1/files/')
    async def _trusted_file(request):
        return {}

    await cron_run.main(
        ['taxi_exp.stuff.update_tags.chaos_tags_proc', '-t', '0'],
    )

    assert _trusted_file.times_called == 2


@pytest.mark.config(
    TAXI_EXP_CHAOS_ENGINEERING_TAGS={
        'fallback_routestats': {
            'rotate_hours': 2,
            'percent': 5,
            'salt': 'salt1',
            'arg_name': 'phone_id',
            'base_tag': 'taxi_phone_id',
        },
        'fallback_totw': {
            'rotate_hours': 5,
            'percent': 10,
            'salt': 'salt2',
            'arg_name': 'phone_id',
            'base_tag': 'taxi_phone_id',
        },
    },
    EXP3_ADMIN_CONFIG={
        'features': {
            'backend': {
                'chaos_tags_enabled': True,
                'chaos_tags_extra_teams_upload': True,
            },
        },
        'settings': {
            'backend': {
                'tags_staff_departments': {
                    'client_product_team': {
                        'department_ids': [1111],
                        'is_chaos_team': True,
                    },
                    'efficiency_team': {
                        'department_ids': [2222],
                        'is_chaos_team': True,
                    },
                },
            },
        },
    },
)
async def test_update_chaos_tag_extra_teams(
        taxi_exp_client, mockserver, patch_aiohttp_session, response_mock,
):
    @patch_aiohttp_session('{}/v3/persons'.format(settings.STAFF_API_URL))
    def _phones_from_staff(method, url, json, headers, params):
        return response_mock(
            json={
                'result': [{'phones': [{'number': '777'}], 'id': 0}],
                'pages': 1,
                'page': 1,
            },
        )

    @mockserver.json_handler('/taxi-exp/v1/files/')
    async def _trusted_files(request):
        return {}

    @mockserver.json_handler('/taxi-exp/v1/trusted-files/metadata/')
    async def _trusted_file_metadata(request):
        return {}

    # running cron
    await cron_run.main(
        ['taxi_exp.stuff.update_tags.chaos_tags_proc', '-t', '0'],
    )

    assert _trusted_files.times_called == 4
