import aiohttp.web


async def test_success(
        web_app_client, headers, mock_fleet_drivers_scoring, load_json,
):
    stub = load_json('success.json')

    @mock_fleet_drivers_scoring(
        '/v1/paid/drivers/scoring/car-orders-history/retrieve',
    )
    async def _quality_metrics_retrieve(request):
        assert request.json == stub['scoring_request']
        return aiohttp.web.json_response(stub['scoring_response'])

    response = await web_app_client.post(
        '/drivers-scoring-api/v1/paid/scoring/car-orders-history/retrieve',
        headers=headers,
        json={'request_id': 'request_id'},
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service_response']


async def test_success_no_history(
        web_app_client, headers, mock_fleet_drivers_scoring, load_json,
):
    stub = load_json('success_no_history.json')

    @mock_fleet_drivers_scoring(
        '/v1/paid/drivers/scoring/car-orders-history/retrieve',
    )
    async def _quality_metrics_retrieve(request):
        assert request.json == stub['scoring_request']
        return aiohttp.web.json_response(stub['scoring_response'])

    response = await web_app_client.post(
        '/drivers-scoring-api/v1/paid/scoring/car-orders-history/retrieve',
        headers=headers,
        json={'request_id': 'request_id'},
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service_response']


async def test_success_not_verified_car_certificate(
        web_app_client, headers, mock_fleet_drivers_scoring, load_json,
):
    stub = load_json('success_not_verified_car_certificate.json')

    @mock_fleet_drivers_scoring(
        '/v1/paid/drivers/scoring/car-orders-history/retrieve',
    )
    async def _quality_metrics_retrieve(request):
        assert request.json == stub['scoring_request']
        return aiohttp.web.json_response(stub['scoring_response'])

    response = await web_app_client.post(
        '/drivers-scoring-api/v1/paid/scoring/car-orders-history/retrieve',
        headers=headers,
        json={'request_id': 'request_id'},
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service_response']


async def test_success_without_car(
        web_app_client, headers, mock_fleet_drivers_scoring, load_json,
):
    stub = load_json('success_without_car.json')

    @mock_fleet_drivers_scoring(
        '/v1/paid/drivers/scoring/car-orders-history/retrieve',
    )
    async def _quality_metrics_retrieve(request):
        assert request.json == stub['scoring_request']
        return aiohttp.web.json_response(stub['scoring_response'])

    response = await web_app_client.post(
        '/drivers-scoring-api/v1/paid/scoring/car-orders-history/retrieve',
        headers=headers,
        json={'request_id': 'request_id'},
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service_response']


async def test_success_not_in_fleet(
        web_app_client, headers, mock_fleet_drivers_scoring, load_json,
):
    stub = load_json('success_not_in_fleet.json')

    @mock_fleet_drivers_scoring(
        '/v1/paid/drivers/scoring/car-orders-history/retrieve',
    )
    async def _quality_metrics_retrieve(request):
        assert request.json == stub['scoring_request']
        return aiohttp.web.json_response(stub['scoring_response'])

    response = await web_app_client.post(
        '/drivers-scoring-api/v1/paid/scoring/car-orders-history/retrieve',
        headers=headers,
        json={'request_id': 'request_id'},
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service_response']
