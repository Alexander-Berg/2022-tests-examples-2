import pytest


async def test_simple_view(taxi_virtual_tariffs):
    body = {
        'corp_client_id': 'b04a64bb1d0147258337412c01176fa1',
        'zone_id': 'moscow',
        'classes': [{'id': 'econom'}, {'id': 'comfort'}],
    }
    response = await taxi_virtual_tariffs.post('/v1/match', json=body)
    assert response.status_code == 200
    assert response.json() == {
        'virtual_tariffs': [
            {
                'class': 'comfort',
                'special_requirements': [{'id': 'food_delivery'}],
            },
            {
                'class': 'econom',
                'special_requirements': [{'id': 'food_delivery'}],
            },
        ],
    }


async def test_view_with_null(taxi_virtual_tariffs):
    body = {
        'corp_client_id': '01234567890123456789012345678912',
        'zone_id': 'moscow',
        'classes': [{'id': 'econom'}, {'id': 'comfort'}, {'id': 'business'}],
    }
    response = await taxi_virtual_tariffs.post('/v1/match', json=body)
    assert response.status_code == 200
    assert response.json() == {
        'virtual_tariffs': [
            # special requirement for all business clients in moscow
            {
                'class': 'business',
                'special_requirements': [{'id': 'good_driver'}],
            },
            # no virtual tariffs for econom -> missing in response
            # special requirement by corp_client_id for comfort
            {
                'class': 'comfort',
                'special_requirements': [{'id': 'food_delivery'}],
            },
        ],
    }


@pytest.fixture(name='mock_claims_requirements')
def _mock_claims(mockserver):
    @mockserver.json_handler('/cargo-claims/v2/claims/special-requirements')
    def _mock_cargo_ref_id(request):
        request_json = request.json
        assert request_json.get('cargo_ref_id') == 'some_cargo_ref_id'
        return {
            'virtual_tariffs': [
                {
                    'class': 'econom',
                    'special_requirements': [{'id': 'cargo_etn'}],
                },
            ],
        }


async def test_cargo_ref_id(taxi_virtual_tariffs, mock_claims_requirements):
    body = {
        'corp_client_id': 'b04a64bb1d0147258337412c01176fa1',
        'zone_id': 'moscow',
        'classes': [{'id': 'econom'}, {'id': 'comfort'}],
        'cargo_ref_id': 'some_cargo_ref_id',
    }
    response = await taxi_virtual_tariffs.post('/v1/match', json=body)
    assert response.status_code == 200
    response_json = response.json()

    # Сортировка, чтобы тест не флапал из-за параллельной обработки в ручке
    for vtariff in response_json['virtual_tariffs']:
        vtariff['special_requirements'].sort(key=lambda x: x['id'])

    assert response_json == {
        'virtual_tariffs': [
            {
                'class': 'comfort',
                'special_requirements': [{'id': 'food_delivery'}],
            },
            {
                'class': 'econom',
                'special_requirements': [
                    {'id': 'cargo_etn'},
                    {'id': 'food_delivery'},
                ],
            },
        ],
    }


async def test_cargo_claims_unavailable(taxi_virtual_tariffs, mockserver):
    @mockserver.json_handler('/cargo-claims/v2/claims/special-requirements')
    def _mock_cargo_ref_id(request):
        return mockserver.make_response(
            json={'code': 'internal_server_error', 'message': 'error'},
            status=500,
        )

    body = {
        'corp_client_id': 'b04a64bb1d0147258337412c01176fa1',
        'zone_id': 'moscow',
        'classes': [{'id': 'econom'}, {'id': 'comfort'}],
        'cargo_ref_id': 'some_cargo_ref_id',
    }
    response = await taxi_virtual_tariffs.post('/v1/match', json=body)
    assert response.status_code == 500


@pytest.mark.config(
    REQUIREMENTS_TO_SPECIAL_REQUIREMENTS_MAP={
        'thermobag': 'thermobag_requirement',
    },
)
async def test_requirements_map(taxi_virtual_tariffs):
    body = {
        'corp_client_id': 'b04a64bb1d0147258337412c01176fa1',
        'zone_id': 'moscow',
        'classes': [
            {'id': 'econom', 'requirements': {'thermobag': True}},
            {'id': 'comfort'},
        ],
    }
    response = await taxi_virtual_tariffs.post('/v1/match', json=body)
    assert response.status_code == 200
    assert response.json() == {
        'virtual_tariffs': [
            {
                'class': 'comfort',
                'special_requirements': [{'id': 'food_delivery'}],
            },
            {
                'class': 'econom',
                'special_requirements': [
                    {'id': 'food_delivery'},
                    {'id': 'thermobag_requirement'},
                ],
            },
        ],
    }


async def test_no_corp_client_id(
        taxi_virtual_tariffs, mock_claims_requirements,
):
    response = await taxi_virtual_tariffs.post(
        '/v1/match',
        json={
            'zone_id': 'moscow',
            'classes': [{'id': 'econom'}, {'id': 'comfort'}],
            'cargo_ref_id': 'some_cargo_ref_id',
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'virtual_tariffs': [
            {'class': 'econom', 'special_requirements': [{'id': 'cargo_etn'}]},
        ],
    }
