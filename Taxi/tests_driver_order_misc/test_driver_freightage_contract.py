import pytest


@pytest.mark.yt(
    schemas=['yt_freightage_contracts_dyn_schema.yaml'],
    dyn_table_data=['yt_freightage_contracts_dyn_data.yaml'],
)
@pytest.mark.parametrize(
    'alias_id,expected_code,expected_json',
    [
        pytest.param(
            'order_with_document',
            200,
            {
                'payload': {
                    'title': 'Freightage contract for order',
                    'contract_data': [
                        {
                            'item_type': 'string',
                            'name': 'Date',
                            'value': '01.01.2021',
                        },
                        {
                            'item_type': 'cost_string',
                            'name': 'Cost',
                            'value': r'654\u2006$SIGN$$CURRENCY$',
                        },
                        {
                            'item_type': 'string',
                            'name': 'Passenger access',
                            'value': 'Via code',
                        },
                    ],
                },
            },
        ),
        pytest.param('order_wo_document', 404, {}),
    ],
)
async def test_load_freightage_contract(
        alias_id,
        expected_code,
        expected_json,
        load_json,
        taxi_driver_order_misc,
        yt_apply_force,
        taxi_config,
):
    taxi_config.set_values(
        {
            'DRIVER_ORDER_MISC_FREIGHTAGE_YT': {
                'cluster': 'hahn',
                'table_prefix': (
                    '//home/testsuite/taximeter_freightage_contracts'
                ),
            },
        },
    )
    response = await taxi_driver_order_misc.post(
        '/driver/v1/order-misc/v1/freightage_contract',
        params={'alias_id': alias_id},
        headers=load_json('auth.json'),
    )
    assert response.status_code == expected_code
    assert response.json() == expected_json
