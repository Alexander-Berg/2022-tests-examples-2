import pytest

EXPECTED_HOST_1 = {
    'name': 'host_name_1',
    'status': 'critical',
    'reasons': [
        {
            'description': 'oplog query test description',
            'detector': 'mongo_oplog_query',
            'status': 'critical',
        },
        {
            'description': 'slow queries test description',
            'detector': 'mongo_slow_queries_sigma',
            'status': 'warning',
        },
    ],
}
EXPECTED_LINK_1 = {
    'name': 'Juggler check - slow queries',
    'url': (
        'https://juggler.yandex-team.ru/check_details/?host=test_mongo_shard'
        '&service=hejmdal-mongo-slow-queries'
    ),
}
EXPECTED_LINK_2 = {'name': 'Grafana dashboard', 'url': 'my_grafana_url'}
EXPECTED_RESPONSE = {
    'databases': [
        {
            'name': 'test_mongo',
            'status': 'critical',
            'shards': [
                {
                    'name': 'test_mongo_shard',
                    'status': 'critical',
                    'hosts': [EXPECTED_HOST_1],
                    'links': [EXPECTED_LINK_1, EXPECTED_LINK_2],
                },
            ],
        },
    ],
}


@pytest.mark.now('2019-10-09T17:56:40+0000')
async def test_mongodb_instances(taxi_hejmdal):
    await taxi_hejmdal.run_task('services_component/invalidate')
    await taxi_hejmdal.run_task('circuit_states_cache/invalidate')
    response = await taxi_hejmdal.get('v1/mongodb/instances')
    assert response.status_code == 200
    assert response.json() == EXPECTED_RESPONSE
