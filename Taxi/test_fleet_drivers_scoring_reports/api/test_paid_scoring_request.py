import aiohttp.web


OFFER = {
    'decision': {'can_buy': True},
    'price': {
        'amount': '60',
        'amount_without_discount': '100',
        'currency': 'RUB',
    },
}


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

    @mock_fleet_drivers_scoring('/v1/paid/drivers/scoring/request')
    async def _scoring_request(request):
        assert request.json == stub['scoring_request']
        return aiohttp.web.json_response(data=stub['scoring_response'])

    response = await web_app_client.post(
        '/drivers-scoring-api/v1/paid/scoring/request',
        headers={**headers, 'X-Idempotency-Token': '1'},
        json={'license': driver_license, 'offer': OFFER},
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service_response']
