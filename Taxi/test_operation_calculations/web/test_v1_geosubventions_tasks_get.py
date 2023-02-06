import http

import pytest

MOSCOW_TAG = [
    {
        'creator': 'dpano',
        'experiment_tags': [],
        'message': '',
        'stage': ['Unknown'],
        'status': 'MISSING',
        'tags': ['bad_tag'],
        'tariff_zones': ['moscow'],
        'tariffs': ['child'],
        'task_id': '7f9b08b19da21d53ed964476',
    },
    {
        'creator': 'dpano',
        'experiment_tags': [],
        'message': '',
        'stage': ['Unknown'],
        'status': 'MISSING',
        'tags': ['super_tag'],
        'tariff_zones': ['moscow'],
        'tariffs': ['child'],
        'task_id': '7f9b08b19da21d53ed964475',
    },
]
MISSING = [
    {
        'creator': 'test_robot',
        'experiment_tags': ['geotool_main', 'test_exp_tag', 'geotool_empty'],
        'message': '',
        'stage': ['Unknown'],
        'status': 'MISSING',
        'tags': ['super_tag'],
        'tariff_zones': ['spb', 'lomonosov'],
        'tariffs': ['child'],
        'task_id': '7f9b08b19da21d53ed964474',
    },
]
MOSCOW = [
    {
        'creator': 'afushta',
        'experiment_tags': [],
        'message': 'some_message',
        'stage': ['some_stage'],
        'status': 'COMPLETED',
        'tariff_zones': ['moscow'],
        'tariffs': ['econom'],
        'task_id': '5f9b08b19da21d52ed964479',
        'updated': '2003-01-08 14:15:06',
    },
    {
        'task_id': '5f9b08b19da21d52ed964473',
        'tariff_zones': ['moscow'],
        'tariffs': ['econom'],
        'creator': 'amneziya',
        'status': 'COMPLETED',
        'stage': ['some_stage'],
        'updated': '1999-01-08 04:05:06',
        'message': 'some_message',
        'experiment_tags': [],
    },
    {
        'creator': 'amneziya',
        'experiment_tags': [],
        'message': '',
        'stage': ['other_stage'],
        'status': 'COMPLETED',
        'tariff_zones': ['moscow', 'dolgoprudny', 'himki'],
        'tariffs': ['econom'],
        'task_id': '5f9b08b19da21d52ed964470',
        'updated': '1999-01-08 04:05:05',
    },
]

SPB = [
    {
        'task_id': '5f9b08b19da21d53ed964473',
        'tariff_zones': ['spb', 'lomonosov'],
        'tariffs': ['business', 'uberx'],
        'creator': 'test_robot',
        'status': 'STARTED',
        'stage': ['some_stage'],
        'updated': '2003-01-08 14:15:06',
        'message': 'some_message',
        'experiment_tags': [],
    },
]
TAGGED = [
    {
        'task_id': '7f9b08b19da21d53ed964473',
        'tariff_zones': ['spb', 'lomonosov'],
        'tariffs': ['child'],
        'creator': 'test_robot',
        'status': 'COMPLETED',
        'stage': ['other_stage'],
        'updated': '2003-01-09 14:05:06',
        'message': '',
        'tags': ['super_tag'],
        'experiment_tags': ['geotool_main', 'test_exp_tag', 'geotool_empty'],
    },
]


@pytest.mark.parametrize(
    'params, expected_status, expected_content',
    (
        pytest.param(
            {},
            http.HTTPStatus.OK,
            {
                'total': 8,
                'items': MOSCOW_TAG + MISSING + TAGGED + SPB + MOSCOW,
            },
        ),
        pytest.param(
            {'creator': 'test_robot'},
            http.HTTPStatus.OK,
            {'total': 8, 'items': MISSING + TAGGED + SPB},
        ),
        pytest.param(
            {'creator': 'test_robot', 'filter_tags': 'true'},
            http.HTTPStatus.OK,
            {'total': 8, 'items': SPB},
        ),
        pytest.param(
            {
                'creator': 'test_robot',
                'filter_tags': 'true',
                'tag': 'super_tag',
            },
            http.HTTPStatus.OK,
            {'total': 8, 'items': MISSING + TAGGED},
        ),
        pytest.param(
            {'tariff': 'business'},
            http.HTTPStatus.OK,
            {'total': 8, 'items': SPB},
        ),
        pytest.param(
            {'tariff_zone': 'moscow'},
            http.HTTPStatus.OK,
            {'total': 8, 'items': MOSCOW_TAG + MOSCOW},
        ),
        pytest.param(
            {'tariff_zone': 'moscow', 'tariff': 'uberx'},
            http.HTTPStatus.OK,
            {'total': 8, 'items': []},
        ),
    ),
)
@pytest.mark.pgsql(
    'operation_calculations', files=['pg_subvention_task_status.sql'],
)
async def test_v1_geosubventions_tasks_get(
        web_app_client, params, expected_status, expected_content, caplog,
):
    response = await web_app_client.get(
        f'/v1/geosubventions/tasks/', params=params,
    )
    assert response.status == expected_status, await response.text()
    results = await response.json()
    for result in results['items']:
        if result['status'] == 'MISSING':
            # cannot mock now inside pg
            result.pop('updated')
    assert results == expected_content
