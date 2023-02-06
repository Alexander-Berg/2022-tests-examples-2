import datetime

import pytest

from .. import pipeline_tools


def get_expected_versions(index_range):
    res = [
        {
            'version': pipeline_tools.get_test_pipeline_to_put(i, '')[
                'new_value'
            ],
            'draft_id': f'draft_id_{i}',
            'for_prestable': False,
        }
        for i in index_range
    ]
    for version in res:
        pipeline_tools.add_thread_num(version['version'])
    return res


async def insert_pipelines(taxi_eventus_orchestrator_web, mocked_time):
    for i in range(1, 25):
        action = 'create' if i == 1 else 'update'
        await pipeline_tools.insert_new_version(
            i, action, taxi_eventus_orchestrator_web,
        )

        mocked_time.sleep(1)
        await taxi_eventus_orchestrator_web.invalidate_caches()


@pytest.mark.parametrize('limit', [1, 2, 5, 15, 24, 30])
@pytest.mark.now('2019-01-01T12:00:00+0000')
async def test_get_versions_without_cursor(
        taxi_eventus_orchestrator_web, mocked_time, limit,
):
    await insert_pipelines(taxi_eventus_orchestrator_web, mocked_time)

    response = await taxi_eventus_orchestrator_web.post(
        '/v1/admin/pipeline/versions/list',
        params={
            'instance_name': 'order-events-producer',
            'pipeline_name': 'test-pipeline',
        },
        json={'limit': limit},
    )

    assert response.status == 200

    body = await response.json()
    expected_len = min(limit, 24)
    assert len(body['versions']) == expected_len
    assert body['versions'] == get_expected_versions(
        range(24, 24 - expected_len, -1),
    )
    assert (
        body['cursor']
        == datetime.datetime(2019, 1, 1, 12, 0, 24 - expected_len).isoformat()
    )


@pytest.mark.parametrize(
    'cursor, limit, expected_indexes, expected_new_cursor',
    [
        ('2019-01-01T12:59:00', 1, [24], '2019-01-01T12:00:23'),
        ('2019-01-01T12:59:00', 3, [24, 23, 22], '2019-01-01T12:00:21'),
        (
            '2019-01-01T12:00:20',
            5,
            [20, 19, 18, 17, 16],
            '2019-01-01T12:00:15',
        ),
        ('2019-01-01T12:00:05', 2, [5, 4], '2019-01-01T12:00:03'),
        ('2019-01-01T11:00:05', 200, [], '2019-01-01T11:00:05'),
        ('2019-01-01T12:00:00', 200, [], '2019-01-01T12:00:00'),
        (
            '2019-01-01T12:00:09',
            10,
            [9, 8, 7, 6, 5, 4, 3, 2, 1],
            '2019-01-01T12:00:00',
        ),
    ],
)
@pytest.mark.now('2019-01-01T12:00:00+0000')
async def test_get_versions_with_cursor(
        taxi_eventus_orchestrator_web,
        mocked_time,
        cursor,
        limit,
        expected_indexes,
        expected_new_cursor,
):
    await insert_pipelines(taxi_eventus_orchestrator_web, mocked_time)

    response = await taxi_eventus_orchestrator_web.post(
        '/v1/admin/pipeline/versions/list',
        params={
            'instance_name': 'order-events-producer',
            'pipeline_name': 'test-pipeline',
        },
        json={'limit': limit, 'cursor': cursor},
    )

    assert response.status == 200

    body = await response.json()
    assert len(body['versions']) == len(expected_indexes)
    assert body['versions'] == get_expected_versions(expected_indexes)
    assert body['cursor'] == expected_new_cursor


@pytest.mark.parametrize('page_size', [1, 2, 10, 20, 23, 24, 30])
@pytest.mark.now('2019-01-01T12:00:00+0000')
async def test_get_all_versions(
        taxi_eventus_orchestrator_web, mocked_time, page_size,
):
    await insert_pipelines(taxi_eventus_orchestrator_web, mocked_time)

    result = []

    cursor = None
    while True:
        json_req = {'limit': page_size}
        if cursor is not None:
            json_req['cursor'] = cursor
        response = await taxi_eventus_orchestrator_web.post(
            '/v1/admin/pipeline/versions/list',
            params={
                'instance_name': 'order-events-producer',
                'pipeline_name': 'test-pipeline',
            },
            json=json_req,
        )

        assert response.status == 200
        body = await response.json()

        result.extend(body['versions'])

        if cursor == body['cursor']:
            break
        cursor = body['cursor']

    assert result == get_expected_versions(range(24, 0, -1))


async def test_no_instance(taxi_eventus_orchestrator_web):
    response = await taxi_eventus_orchestrator_web.post(
        '/v1/admin/pipeline/versions/list',
        params={
            'instance_name': 'no-instance-',
            'pipeline_name': 'test-pipeline',
        },
        json={'limit': 10},
    )

    assert response.status == 404


async def test_no_pipeline(taxi_eventus_orchestrator_web):
    response = await taxi_eventus_orchestrator_web.post(
        '/v1/admin/pipeline/versions/list',
        params={
            'instance_name': 'order-events-producer',
            'pipeline_name': 'no-pipeline-',
        },
        json={'limit': 10},
    )

    assert response.status == 200
    body = await response.json()
    assert body == {'versions': [], 'cursor': '9999-12-31T23:59:59.999999'}
