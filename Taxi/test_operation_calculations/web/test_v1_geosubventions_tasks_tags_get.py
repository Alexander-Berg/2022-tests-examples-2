import http

import pytest


@pytest.mark.parametrize(
    'params, expected',
    [
        [
            {},
            {
                'tags': [
                    '',
                    'bad_tag',
                    'geotool_empty',
                    'geotool_main',
                    'super_tag',
                    'test_exp_tag',
                ],
            },
        ],
        [{'creator': 'amneziya'}, {'tags': ['']}],
        [
            {'tariff': 'child'},
            {
                'tags': [
                    'bad_tag',
                    'geotool_empty',
                    'geotool_main',
                    'super_tag',
                    'test_exp_tag',
                ],
            },
        ],
        [{'tariff': 'very_unknown_tariff'}, {'tags': []}],
    ],
)
@pytest.mark.pgsql(
    'operation_calculations', files=['pg_subvention_task_status.sql'],
)
async def test_v1_geosubventions_tasks_tags_get(
        web_app_client, params, expected,
):
    response = await web_app_client.get(
        '/v1/geosubventions/tasks_tags/', params=params,
    )
    status = response.status
    result = await response.json()
    assert status == http.HTTPStatus.OK
    result['tags'] = sorted(result['tags'])
    assert result == expected
