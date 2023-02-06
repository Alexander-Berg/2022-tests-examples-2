import pytest


@pytest.fixture(name='create_payment_ids')
def _create_payment_ids(
        create_segment_with_payment,
        get_claim_v2,
        mock_payment_validate,
        mock_payment_create,
):
    async def wrapper():
        claim_info = await create_segment_with_payment(payment_method='card')
        claim = await get_claim_v2(claim_info.claim_id)
        payment_ids = [
            route_point['payment_on_delivery']['payment_ref_id']
            for route_point in claim['route_points']
            if 'payment_on_delivery' in route_point
        ]
        assert payment_ids
        return payment_ids

    return wrapper


@pytest.mark.skip('search by payment id is not implemented')
async def test_payment_id_search_hit(taxi_cargo_claims, create_payment_ids):
    """
      Test that search by payment id works for UUIDs and string without dashes.
    """
    payment_ids = await create_payment_ids()
    for payment_id in payment_ids:

        # payment id in UUID4 format (with dashes)
        response = await taxi_cargo_claims.post(
            'v2/admin/claims/search',
            json={
                'offset': 0,
                'limit': 5,
                'criterias': {'payment_id': payment_id},
            },
        )
        response_content = response.json()
        assert len(response_content['claims']) == 1

        # should work the same after removing dashes
        response = await taxi_cargo_claims.post(
            'v2/admin/claims/search',
            json={
                'offset': 0,
                'limit': 5,
                'criterias': {'payment_id': payment_id.replace('-', '')},
            },
        )
        response_content = response.json()
        assert len(response_content['claims']) == 1


@pytest.mark.skip('search by payment id is not implemented')
async def test_payment_id_search_no_hit(taxi_cargo_claims, create_payment_ids):
    """
      Test that search by payment_id does not return any records
      for non-existing payment_id.
    """
    await create_payment_ids()  # fill DB with claim and post payment records
    non_existing_id = '6' * 32

    response = await taxi_cargo_claims.post(
        'v2/admin/claims/search',
        json={
            'offset': 0,
            'limit': 5,
            'criterias': {'payment_id': non_existing_id},
        },
    )
    response_content = response.json()
    assert response.status_code == 200
    assert not response_content['claims']


@pytest.mark.skip('search by payment id is not implemented')
async def test_payment_id_search_invalid(
        taxi_cargo_claims, create_payment_ids,
):
    """
      Test that search by payment_id successfully returns nothing when
      payment_id is invalid.
    """
    await create_payment_ids()  # fill DB with claim and post payment records
    invalid_payment_ids = ['INVALID', 'a' * 31, '-', '-' * 32]
    for invalid_payment_id in invalid_payment_ids:
        response = await taxi_cargo_claims.post(
            'v2/admin/claims/search',
            json={
                'offset': 0,
                'limit': 5,
                'criterias': {'payment_id': invalid_payment_id},
            },
        )
        assert response.status_code == 200
        response_content = response.json()
        assert not response_content['claims']
