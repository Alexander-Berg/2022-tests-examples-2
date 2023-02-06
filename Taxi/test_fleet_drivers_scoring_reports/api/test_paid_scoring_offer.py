import aiohttp.web


async def test_success(
        web_app_client,
        headers,
        mock_fleet_drivers_scoring,
        mock_personal_single_license,
        load_json,
):
    stub = load_json('success.json')

    driver_license = '86ЕК868672'
    expected_driver_license = stub['scoring_request']['query']['driver'][
        'license_pd_id'
    ]

    mock_personal_single_license(driver_license, expected_driver_license)

    @mock_fleet_drivers_scoring('/v1/paid/drivers/scoring/offer')
    async def _scoring_request(request):
        assert request.json == stub['scoring_request']
        return aiohttp.web.json_response(stub['scoring_response'])

    response = await web_app_client.post(
        '/drivers-scoring-api/v1/paid/scoring/offer',
        headers={**headers, 'X-Idempotency-Token': '1'},
        json={'license': driver_license},
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service_response']


async def test_success_discounts(
        web_app_client,
        headers,
        mock_fleet_drivers_scoring,
        mock_personal_single_license,
        load_json,
):
    stub = load_json('success.json')

    driver_license = '86ЕК868672'
    expected_driver_license = stub['scoring_request']['query']['driver'][
        'license_pd_id'
    ]

    mock_personal_single_license(driver_license, expected_driver_license)

    @mock_fleet_drivers_scoring('/v1/paid/drivers/scoring/offer')
    async def _scoring_request(request):
        assert request.json == stub['scoring_request']
        return aiohttp.web.json_response(stub['scoring_response_discounts'])

    response = await web_app_client.post(
        '/drivers-scoring-api/v1/paid/scoring/offer',
        headers={**headers, 'X-Idempotency-Token': '1'},
        json={'license': driver_license},
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service_response_discounts']


async def test_forbidden(
        web_app_client,
        headers,
        mock_fleet_drivers_scoring,
        mock_personal_single_license,
        load_json,
):
    stub = load_json('forbidden.json')

    driver_license = '86ЕК868672'
    expected_driver_license = stub['scoring_request']['query']['driver'][
        'license_pd_id'
    ]

    mock_personal_single_license(driver_license, expected_driver_license)

    @mock_fleet_drivers_scoring('/v1/paid/drivers/scoring/offer')
    async def _scoring_request(request):
        return aiohttp.web.json_response(
            status=400, data={'code': 'code', 'message': 'message'},
        )

    response = await web_app_client.post(
        '/drivers-scoring-api/v1/paid/scoring/offer',
        headers={**headers, 'X-Idempotency-Token': '1'},
        json={'license': driver_license},
    )

    assert response.status == 403

    data = await response.json()
    data_keys = data.keys()
    assert 'code' in data_keys
    assert 'message' in data_keys
