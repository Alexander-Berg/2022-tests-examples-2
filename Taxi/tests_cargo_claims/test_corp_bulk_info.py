async def test_empty_response(taxi_cargo_claims, get_default_headers):
    response = await taxi_cargo_claims.post(
        '/api/integration/v2/claims/bulk_info',
        headers=get_default_headers('other_corp_id0123456789012345678'),
        json={'claim_ids': ['12345']},
    )
    assert response.status_code == 200
    assert response.json() == {'claims': []}


async def test_success(
        taxi_cargo_claims, create_default_claim, get_default_headers,
):
    response = await taxi_cargo_claims.post(
        '/api/integration/v2/claims/bulk_info',
        headers=get_default_headers(),
        json={'claim_ids': [create_default_claim.claim_id]},
    )
    assert response.status_code == 200
    resp = response.json()
    assert len(resp['claims']) == 1


async def test_too_many_claims(
        taxi_cargo_claims, create_default_claim, get_default_headers,
):
    response = await taxi_cargo_claims.post(
        '/api/integration/v2/claims/bulk_info',
        headers=get_default_headers(),
        json={'claim_ids': ['123'] * 1001},
    )
    assert response.status_code == 400


async def test_replace_sdd_tariff(
        taxi_cargo_claims,
        mock_create_event,
        get_default_headers,
        get_default_corp_client_id,
        taxi_config,
        create_claim_segment_matched_car_taxi_class,
        taxi_tariff='night',
        display_tariff='same_day_delivery_1',
):
    taxi_config.set(
        CARGO_SDD_TAXI_TARIFF_SETTINGS={
            'remove_in_tariffs': True,
            'remove_in_admin_tariffs': False,
            'name': taxi_tariff,
            'display_in_corp_cabinet': display_tariff,
        },
    )

    mock_create_event()
    claim, _ = await create_claim_segment_matched_car_taxi_class(
        get_default_corp_client_id, taxi_class=taxi_tariff,
    )

    response = await taxi_cargo_claims.post(
        '/api/integration/v2/claims/bulk_info',
        headers=get_default_headers(),
        json={'claim_ids': [claim.claim_id]},
    )

    assert response.status_code == 200
    assert (
        response.json()['claims'][0]['matched_cars'][0]['taxi_class']
        == display_tariff
    )
