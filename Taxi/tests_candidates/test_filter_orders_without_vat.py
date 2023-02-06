import pytest


@pytest.mark.parametrize(
    'order_without_vat_contract,park_has_contract,setting_mode,matched,is_error',
    [
        (False, True, 'disabled', True, False),
        (True, True, 'disabled', False, True),
        (True, True, 'enabled', True, False),
        (True, False, 'enabled', False, False),
        (True, True, 'temporary', True, False),
        (True, False, 'temporary', True, False),
    ],
    ids=[
        'non_without_vat_order',
        'setting_disabled',
        'setting_enabled',
        'park_without_signed_contract',
        'temporary_mode',
        'temporary_mode_for_park_without_signed_contract',
    ],
)
async def test_filter_orders_without_vat(
        taxi_candidates,
        driver_positions,
        taxi_config,
        order_without_vat_contract,
        park_has_contract,
        setting_mode,
        matched,
        is_error,
):
    dbid_uuid = 'dbid0_uuid0' if park_has_contract else 'dbid1_uuid5'

    await driver_positions([{'dbid_uuid': dbid_uuid, 'position': [55, 35]}])

    taxi_config.set_values(
        {
            'CORP_ORDERS_WITHOUT_VAT_PAYMENT': {
                '__default__': 'disabled',
                'Москва': setting_mode,
            },
        },
    )

    request_body = {
        'geoindex': 'kdtree',
        'limit': 3,
        'filters': ['corp/orders_without_vat'],
        'point': [55, 35],
        'zone_id': 'moscow',
        'order': {
            'city': 'Москва',
            'request': {
                'corp': {'without_vat_contract': order_without_vat_contract},
            },
        },
    }

    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 400 if is_error else 200
    if not is_error:
        assert len(response.json()['drivers']) == int(matched)
