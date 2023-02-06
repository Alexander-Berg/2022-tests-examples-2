# pylint:disable=no-member
# type: ignore
import pytest

HANDLER_PATH = '/v1/eventus/instance/status/update'
GET_HANDLER_PATH = '/v1/service/instances/statistics'


@pytest.mark.parametrize(
    'data, expected_status',
    [
        ({'host': {}, 'status': 'starting'}, 400),
        (
            {
                'status': 'starting',
                'pipelines': [{'name': 'pipeline_1', 'status': 'dead'}],
            },
            400,
        ),
        (
            {
                'host': {
                    'name': 'ulyalya.taxi.yandex.net',
                    'instance': 'eventus',
                },
                'status': 'starting',
                'pipelines': [
                    {
                        'name': 'pipeline_1',
                        'status': 'failed',
                        'statistic': {
                            'processed': 12,
                            'errors': 0,
                            'dropped': 999,
                        },
                    },
                ],
            },
            200,
        ),
    ],
)
async def test_base(web_app_client, mongo, data, expected_status):
    response = await web_app_client.post(HANDLER_PATH, json=data)
    assert response.status == expected_status

    if expected_status > 200:
        return

    assert await response.json() == {}

    response = await web_app_client.post(
        GET_HANDLER_PATH, json={'host_names': [data['host']['name']]},
    )
    parsed = await response.json()
    assert len(parsed['items']) == 1
    assert parsed['items'][0] == data


@pytest.mark.parametrize(
    'req_data',
    [
        {
            'host': {'name': '123.yandex.net', 'instance': 'test-instance'},
            'pipelines': [],
            'status': 'running',
        },
        {
            'host': {
                'name': '123.yandex.net',
                'instance': 'test-instance',
                'nanny_service_id': 'taxi_order-events-producer_testing',
            },
            'pipelines': [],
            'status': 'idle',
        },
    ],
)
async def test_nanny_service_id(
        taxi_eventus_orchestrator_web, mongodb, req_data, load_json,
):
    response = await taxi_eventus_orchestrator_web.post(
        HANDLER_PATH, json=req_data,
    )
    assert response.status == 200

    expected = load_json('db_eventus_instances.json')
    to_append = {
        'host': req_data['host']['name'],
        'instance': req_data['host']['instance'],
        'statistic': req_data['pipelines'],
        'status': req_data['status'],
    }
    if 'nanny_service_id' in req_data['host']:
        to_append['nanny_service_id'] = req_data['host']['nanny_service_id']
    expected.append(to_append)
    assert list(mongodb.eventus_instances.find({}, {'_id': 0})) == expected
