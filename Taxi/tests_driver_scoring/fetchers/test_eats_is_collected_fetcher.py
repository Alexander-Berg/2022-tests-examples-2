import pytest

import tests_driver_scoring.tvm_tickets as tvm_tickets


@pytest.mark.experiments3(filename='js_bonuses.json')
@pytest.mark.experiments3(filename='default_postprocessors.json')
@pytest.mark.pgsql('driver_scoring', files=['js_scripts.sql'])
@pytest.mark.config(DRIVER_SCORING_EATS_TAGS_FETCHERS_ENABLED=True)
@pytest.mark.parametrize(
    'order_status,bonus',
    [
        pytest.param('confirmed', 0, id='status_confirmed'),
        pytest.param('picked_up', 100, id='status_picked_up'),
        pytest.param(
            'receipt_processing', 100, id='status_receipt_processing',
        ),
    ],
)
async def test_driver_scoring_is_collected_fetcher(
        taxi_driver_scoring,
        mockserver,
        load_json,
        eats_tags,
        order_status,
        bonus,
):
    status_calls = 0

    @mockserver.json_handler('/eats-picker-orders/api/v1/order/status')
    def _profiles(request):
        nonlocal status_calls
        status_calls += 1
        return mockserver.make_response(
            status=200, json={'status': order_status},
        )

    cache_reads = 0
    cache_writes = 0
    cache_storage = {}

    @mockserver.json_handler('/api-cache/v1/cached-value/picked-order')
    def _api_cache_mock(request):
        nonlocal cache_reads, cache_writes, cache_storage
        key = request.query['key']
        if request.method == 'PUT':
            assert request.headers.get('Cache-Control').startswith('max-age=')
            data = request.get_data()
            cache_storage[key] = data
            cache_writes += 1
            return {}
        if request.method == 'GET':
            data = cache_storage.get(key)
            if not data:
                return mockserver.make_response(status=404)
            cache_reads += 1
            return mockserver.make_response(
                data,
                headers={'Content-Type': 'application/octet-stream'},
                status=200,
            )
        raise RuntimeError(f'Unsupported method {request.method}')

    async def make_request():
        response = await taxi_driver_scoring.post(
            'v2/score-candidates-bulk',
            headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
            json=load_json('request_body_full_with_eats.json'),
        )

        undefined_picked_bonus = 50

        assert response.status_code == 200
        assert response.json()['responses'] == [
            {
                'search': {'order_id': '16e83c16beb74880b819d2a7b1c06d93'},
                'candidates': [
                    {'id': 'dbid1_uuid1', 'score': 124.0 - bonus},
                    {'id': 'dbid0_uuid0', 'score': 650.0 - bonus},
                ],
            },
            {
                'search': {},
                'candidates': [
                    {
                        'id': 'dbid1_uuid1',
                        'score': 124.0 - undefined_picked_bonus,
                    },
                    {
                        'id': 'dbid0_uuid0',
                        'score': 650.0 - undefined_picked_bonus,
                    },
                ],
            },
        ]

    status_calls = cache_reads = cache_writes = 0
    await make_request()
    assert status_calls == 1
    assert cache_writes == 1
    assert cache_reads == 0

    status_calls = cache_reads = cache_writes = 0
    await make_request()
    assert status_calls == 0
    assert cache_writes == 0
    assert cache_reads == 1


@pytest.mark.experiments3(filename='js_bonuses.json')
@pytest.mark.experiments3(filename='default_postprocessors.json')
@pytest.mark.pgsql('driver_scoring', files=['js_scripts.sql'])
@pytest.mark.config(DRIVER_SCORING_EATS_TAGS_FETCHERS_ENABLED=True)
@pytest.mark.parametrize(
    'order_status,bonus',
    [
        pytest.param('confirmed', 0, id='status_confirmed'),
        pytest.param('picked_up', 100, id='status_picked_up'),
        pytest.param(
            'receipt_processing', 100, id='status_receipt_processing',
        ),
    ],
)
async def test_driver_scoring_is_collected_fetcher_cache_error(
        taxi_driver_scoring,
        mockserver,
        load_json,
        eats_tags,
        order_status,
        bonus,
):
    status_calls = 0

    @mockserver.json_handler('/eats-picker-orders/api/v1/order/status')
    def _profiles(request):
        nonlocal status_calls
        status_calls += 1
        return mockserver.make_response(
            status=200, json={'status': order_status},
        )

    @mockserver.json_handler('/api-cache/v1/cached-value/picked-order')
    def _api_cache_mock(request):
        return mockserver.make_response(status=500)

    async def make_request():
        response = await taxi_driver_scoring.post(
            'v2/score-candidates-bulk',
            headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
            json=load_json('request_body_full_with_eats.json'),
        )

        undefined_picked_bonus = 50

        assert response.status_code == 200
        assert response.json()['responses'] == [
            {
                'search': {'order_id': '16e83c16beb74880b819d2a7b1c06d93'},
                'candidates': [
                    {'id': 'dbid1_uuid1', 'score': 124.0 - bonus},
                    {'id': 'dbid0_uuid0', 'score': 650.0 - bonus},
                ],
            },
            {
                'search': {},
                'candidates': [
                    {
                        'id': 'dbid1_uuid1',
                        'score': 124.0 - undefined_picked_bonus,
                    },
                    {
                        'id': 'dbid0_uuid0',
                        'score': 650.0 - undefined_picked_bonus,
                    },
                ],
            },
        ]

    status_calls = 0
    await make_request()
    assert status_calls == 1

    status_calls = 0
    await make_request()
    assert status_calls == 1


@pytest.mark.experiments3(filename='js_bonuses.json')
@pytest.mark.experiments3(filename='default_postprocessors.json')
@pytest.mark.pgsql('driver_scoring', files=['js_scripts.sql'])
@pytest.mark.config(DRIVER_SCORING_EATS_TAGS_FETCHERS_ENABLED=True)
async def test_driver_scoring_is_collected_fetcher_api_error(
        taxi_driver_scoring, mockserver, load_json, eats_tags,
):
    status_calls = 0

    @mockserver.json_handler('/eats-picker-orders/api/v1/order/status')
    def _profiles(request):
        nonlocal status_calls
        status_calls += 1
        return mockserver.make_response(status=500)

    @mockserver.json_handler('/api-cache/v1/cached-value/picked-order')
    def _api_cache_mock(request):
        return mockserver.make_response(status=500)

    async def make_request():
        response = await taxi_driver_scoring.post(
            'v2/score-candidates-bulk',
            headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
            json=load_json('request_body_full_with_eats.json'),
        )

        undefined_picked_bonus = 50
        picked_bonus = 100

        assert response.status_code == 200
        assert response.json()['responses'] == [
            {
                'search': {'order_id': '16e83c16beb74880b819d2a7b1c06d93'},
                'candidates': [
                    {'id': 'dbid1_uuid1', 'score': 124.0 - picked_bonus},
                    {'id': 'dbid0_uuid0', 'score': 650.0 - picked_bonus},
                ],
            },
            {
                'search': {},
                'candidates': [
                    {
                        'id': 'dbid1_uuid1',
                        'score': 124.0 - undefined_picked_bonus,
                    },
                    {
                        'id': 'dbid0_uuid0',
                        'score': 650.0 - undefined_picked_bonus,
                    },
                ],
            },
        ]

    status_calls = 0
    await make_request()
    assert status_calls == 1
