import pytest


@pytest.mark.parametrize(
    'query_parameters, status_code, response_json',
    [
        (
            {
                'last_known_revision': '11111_0',
                'consumer': 'testsuite',
                'limit': 2,
            },
            200,
            {
                'last_revision': '11111_2',
                'drivers': [
                    {
                        'id': '000000000000000000000001',
                        'source': 'new_license_id',
                    },
                    {'id': '000000000000000000000002', 'source': 'decoupled'},
                ],
            },
        ),
        (
            {'last_known_revision': '11111_3', 'consumer': 'testsuite'},
            200,
            {
                'last_revision': '11112_2',
                'drivers': [
                    {
                        'id': '000000000000000000000005',
                        'source': 'new_license_id',
                    },
                    {
                        'id': '000000000000000000000004',
                        'source': 'new_license_id',
                    },
                ],
            },
        ),
        (
            {'last_known_date': '11111', 'consumer': 'testsuite', 'limit': 2},
            200,
            {
                'last_revision': '11111_2',
                'drivers': [
                    {
                        'id': '000000000000000000000001',
                        'source': 'new_license_id',
                    },
                    {'id': '000000000000000000000002', 'source': 'decoupled'},
                ],
            },
        ),
        (
            {'consumer': 'testsuite', 'limit': 2},
            200,
            {
                'last_revision': '11111_2',
                'drivers': [
                    {
                        'id': '000000000000000000000001',
                        'source': 'new_license_id',
                    },
                    {'id': '000000000000000000000002', 'source': 'decoupled'},
                ],
            },
        ),
        (
            {'last_known_time': '1546300100', 'consumer': 'testsuite'},
            200,
            {'last_revision': '11112_2', 'drivers': []},
        ),
        (
            {
                # '2019-01-01T00:00:00' + 1s
                'last_known_time': '1546300801',
                'consumer': 'testsuite',
            },
            400,
            {
                'code': 'BAD_REQUEST',
                'message': (
                    'last_known_time should be less than current '
                    'time: 1546300801'
                ),
            },
        ),
        (
            {
                # '2019-01-01T00:00:00' - 30s (lag 120s)
                'last_known_time': '1546300770',
                'consumer': 'testsuite',
            },
            200,
            {'last_revision': '1546300750_0', 'drivers': []},
        ),
        (
            {
                # '2019-01-01T00:00:00' - 70s (lag 120s)
                'last_known_time': '1546300730',
                'consumer': 'testsuite',
            },
            200,
            {'last_revision': '11112_2', 'drivers': []},
        ),
        (
            {'last_known_revision': '11111_1'},
            400,
            {'code': '400', 'message': 'Missing consumer in query'},
        ),
        (
            {
                'last_known_revision': '4294967297_99999',  # 2^32 + 1
                'consumer': 'testsuite',
            },
            400,
            {
                'code': 'BAD_REQUEST',
                'message': 'invalid last know revision: 4294967297_99999',
            },
        ),
        (
            {
                'last_known_revision': '11111_1',
                'last_known_time': '11111',
                'consumer': 'testsuite',
            },
            400,
            {
                'code': 'BAD_REQUEST',
                'message': (
                    'Parameter last_known_time is redundant, '
                    'pass only last_known_revision instead'
                ),
            },
        ),
    ],
)
@pytest.mark.now('2019-01-01T00:00:00+0000')
async def test_drivers_new(
        query_parameters, status_code, response_json, taxi_unique_drivers,
):
    response = await taxi_unique_drivers.get(
        'v1/driver/new', params=query_parameters,
    )

    assert response.status_code == status_code
    assert response.json() == response_json
    if response.status_code == 200:
        assert 'application/json' in response.headers['Content-Type']
