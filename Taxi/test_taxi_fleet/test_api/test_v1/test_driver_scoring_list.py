import aiohttp.web


async def test_success(
        web_app_client,
        headers,
        load_json,
        mock_api7,
        mock_personal_single_license,
):
    stub = load_json('success.json')
    driver_license = '86ЕК868672'
    expected_driver_license = stub['scoring_request']['query']['driver'][
        'license_pd_id'
    ]

    mock_personal_single_license(driver_license, expected_driver_license)

    @mock_api7('/v1/drivers/scoring/retrieve')
    async def _drivers_scoring(request):
        assert request.json == stub['scoring_request']
        return aiohttp.web.json_response(stub['scoring_response'])

    response = await web_app_client.post(
        '/api/v1/driver-scoring/list',
        headers={**headers, 'X-Idempotency-Token': 'a1-b2-c3-d4'},
        json={'license': driver_license},
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service_response']


async def test_too_many_requests(
        web_app_client,
        headers,
        mock_api7,
        load_json,
        mock_personal_single_license,
):
    stub = load_json('success.json')
    driver_license = '86ЕК868672'
    expected_dl = stub['scoring_request']['query']['driver']['license_pd_id']

    mock_personal_single_license(driver_license, expected_dl)

    @mock_api7('/v1/drivers/scoring/retrieve')
    async def _status_driver_scoring(request):
        return aiohttp.web.json_response(
            status=429, data={'code': 'code', 'message': 'message'},
        )

    response = await web_app_client.post(
        '/api/v1/driver-scoring/list',
        headers={**headers, 'X-Idempotency-Token': 'a1-b2-c3-d4'},
        json={'license': driver_license},
    )

    assert response.status == 429

    data = await response.json()
    data_keys = data.keys()
    assert 'code' in data_keys
    assert 'message' in data_keys
