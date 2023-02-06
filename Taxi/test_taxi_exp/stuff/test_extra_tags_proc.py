import pytest

from taxi_exp import settings
from taxi_exp.generated.cron import run_cron as cron_run


@pytest.mark.config(
    EXP3_ADMIN_CONFIG={
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
@pytest.mark.parametrize(
    'yandex_affiliation',
    [
        pytest.param(
            False,
            marks=[
                pytest.mark.config(
                    EXP3_ADMIN_CONFIG={
                        'settings': {
                            'backend': {
                                'tags_staff_departments': {
                                    'some_outstaff_team': {
                                        'allow_outstaff': True,
                                        'department_ids': [0],
                                    },
                                },
                            },
                        },
                    },
                ),
            ],
        ),
        pytest.param(
            True,
            marks=[
                pytest.mark.config(
                    EXP3_ADMIN_CONFIG={
                        'settings': {
                            'backend': {
                                'tags_staff_departments': {
                                    'some_yandex_team': {
                                        'department_ids': [1],
                                    },
                                },
                            },
                        },
                    },
                ),
            ],
        ),
    ],
)
async def test_update_extra_teams(
        mockserver,
        patch_aiohttp_session,
        response_mock,
        yandex_affiliation,
        taxi_exp_client,
):
    @patch_aiohttp_session('{}/v3/persons'.format(settings.STAFF_API_URL))
    def _phones_from_staff(method, url, json, headers, params):
        if any(param.startswith('department_group.') for param in params):
            if not yandex_affiliation:
                assert 'official.affiliation' not in params
            else:
                assert params.get('official.affiliation') == 'yandex'
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
        ['taxi_exp.stuff.update_tags.extra_tags_proc', '-t', '0'],
    )

    assert _trusted_files.times_called == 1
