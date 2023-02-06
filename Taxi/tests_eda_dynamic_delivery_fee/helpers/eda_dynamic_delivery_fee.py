async def calculate(
        taxi_eda_dynamic_delivery_fee,
        brand_id,
        region_id,
        device_id,
        zone_type,
        distance_to_customer,
        old_fees,
        expected_status,
        expected_response_json,
):
    headers = {'Content-Type': 'application/json; charset=UTF-8'}

    body = {
        'brand_id': brand_id,
        'region_id': region_id,
        'device_id': device_id,
        'zone_type': zone_type,
        'distance_to_customer': distance_to_customer,
    }

    if old_fees is not None:
        body['old_fees'] = old_fees

    response = await taxi_eda_dynamic_delivery_fee.post(
        '/v1/eda-dynamic-delivery-fee', body, headers=headers,
    )

    response_json = response.json()

    assert expected_status == response.status_code
    assert expected_response_json == response_json


async def update_cache(
        taxi_eda_dynamic_delivery_fee,
        brand_id,
        region_id,
        zone_type,
        commission,
        fixed_commission,
        mean_check,
        rpo_commission,
        expected_status,
):
    headers = {'Content-Type': 'application/json; charset=UTF-8'}

    response = await taxi_eda_dynamic_delivery_fee.post(
        '/v1/eda-dynamic-delivery-fee/cache',
        {
            'cache': [
                {
                    'brand_id': brand_id,
                    'region_id': region_id,
                    'zone_type': zone_type,
                    'commission': commission,
                    'fixed_commission': fixed_commission,
                    'mean_check': mean_check,
                    'rpo_commission': rpo_commission,
                },
            ],
        },
        headers=headers,
    )

    assert expected_status == response.status_code
