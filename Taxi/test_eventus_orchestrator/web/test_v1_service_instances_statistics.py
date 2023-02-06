# pylint:disable=no-member
# type: ignore
import copy

import pytest

HANDLER_PATH = '/v1/eventus/instance/status/update'
GET_HANDLER_PATH = '/v1/service/instances/statistics'

FIRST_INSTANCE = {
    'host': {
        'instance': 'eventus',
        'name': 'karachaevo-cherkesiya.taxi.tst.yandex.net',
    },
    'pipelines': [
        {
            'name': 'simple_name',
            'statistic': {'dropped': 123, 'errors': 1, 'processed': 400},
            'status': 'running',
        },
        {
            'name': 'complicated_name',
            'statistic': {'dropped': 0, 'errors': 0, 'processed': 0},
            'status': 'idle',
        },
    ],
    'status': 'running',
}
SECOND_INSTANCE = {
    'host': {'instance': 'eventus', 'name': 'ulyalya.taxi.yandex.net'},
    'pipelines': [
        {
            'name': 'unique_name',
            'statistic': {'dropped': 123, 'errors': 1, 'processed': 400},
            'status': 'running',
        },
    ],
    'status': 'failed',
}
MODIFY_DATA = {
    'host': {
        'name': 'karachaevo-cherkesiya.taxi.tst.yandex.net',
        'instance': 'eventus',
    },
    'status': 'idle',
    'pipelines': [
        {
            'name': 'simple_name',
            'status': 'failed',
            'statistic': {'processed': 0, 'errors': 900000, 'dropped': 0},
        },
    ],
}


def _sort_by_host(hosts):
    return sorted(
        hosts, key=lambda x: (x['host']['instance'], x['host']['name']),
    )


@pytest.mark.filldb()
@pytest.mark.parametrize(
    'data, expected_status, expected_res',
    [
        ({'instances': ['eventus']}, 200, [FIRST_INSTANCE, SECOND_INSTANCE]),
        ({}, 200, [FIRST_INSTANCE, SECOND_INSTANCE]),
        (
            {
                'host_names': ['ulyalya.taxi.yandex.net'],
                'instances': ['eventus'],
            },
            200,
            [SECOND_INSTANCE],
        ),
        (
            {
                'instances': ['eventus'],
                'host_names': [
                    'ulyalya.taxi.yandex.net',
                    'karachaevo-cherkesiya.taxi.tst.yandex.net',
                ],
            },
            200,
            [FIRST_INSTANCE, SECOND_INSTANCE],
        ),
        ({'statuses': ['running']}, 200, [FIRST_INSTANCE]),
    ],
)
async def test_base(
        web_app_client, mongo, data, expected_status, expected_res,
):
    response = await web_app_client.post(GET_HANDLER_PATH, json=data)
    parsed = await response.json()
    assert response.status == expected_status
    if expected_status > 200:
        return
    assert _sort_by_host(parsed['items']) == _sort_by_host(expected_res)


@pytest.mark.filldb()
@pytest.mark.parametrize(
    'data, expected_status, expected_res',
    [
        (
            {'host_names': ['karachaevo-cherkesiya.taxi.tst.yandex.net']},
            200,
            [FIRST_INSTANCE],
        ),
        ({'instances': ['eventus']}, 200, [FIRST_INSTANCE, SECOND_INSTANCE]),
    ],
)
async def test_with_modification(
        web_app_client, mongo, data, expected_status, expected_res,
):
    response = await web_app_client.post(GET_HANDLER_PATH, json=data)
    parsed = await response.json()
    assert response.status == expected_status
    if expected_status > 200:
        return
    assert _sort_by_host(parsed['items']) == _sort_by_host(expected_res)

    response = await web_app_client.post(HANDLER_PATH, json=MODIFY_DATA)
    assert response.status == 200

    response = await web_app_client.post(GET_HANDLER_PATH, json=data)
    copy_expected_res = copy.deepcopy(expected_res)
    for host in copy_expected_res:
        new_pipelines = []
        if host['host'] == MODIFY_DATA['host']:
            for pipeline in host['pipelines']:
                for modified_pipeline in MODIFY_DATA['pipelines']:
                    if pipeline['name'] == modified_pipeline['name']:
                        pipeline.update(modified_pipeline)
                        new_pipelines.append(pipeline)
                        break
            host['pipelines'] = new_pipelines
            host['status'] = MODIFY_DATA['status']
            break

    parsed = await response.json()
    assert parsed['items'] == copy_expected_res
