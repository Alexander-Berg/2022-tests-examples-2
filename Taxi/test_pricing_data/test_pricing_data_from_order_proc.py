import pytest

from pricing_data.models import order_proc


@pytest.mark.parametrize(
    'order_proc_filename',
    [
        'order_proc_current_prices_with_final_cost.json',
        'order_proc_current_prices_without_final_cost.json',
        'order_proc_pricing_data_with_paid_supply.json',
        'order_proc_pricing_data_without_paid_supply.json',
    ],
)
def test_pricing_data_from_order_proc(load_json, order_proc_filename):
    order_proc_doc = load_json(order_proc_filename)
    order = order_proc_doc.get('order')

    expected_pricing_data = order.get('pricing_data', {})
    expected_current_prices = order.get('current_prices', {})

    expected_pricing_data = order.get('pricing_data', {})
    expected_current_prices = order.get('current_prices', {})
    is_paid_supply = order.get('performer', {}).get('paid_supply', False)

    actual = order_proc.PricingData(order)

    if expected_current_prices:
        expected_driver_meta = expected_current_prices['final_cost_meta'][
            'driver'
        ]
        expected_user_meta = expected_current_prices['final_cost_meta']['user']
        if 'final_cost' in expected_current_prices:
            expected_driver_price = expected_current_prices['final_cost'][
                'driver'
            ]
            expected_user_price = expected_current_prices['final_cost']['user']
        else:
            if is_paid_supply and (
                    'paid_supply'
                    in expected_pricing_data['driver'].get(
                        'additional_prices', {},
                    )
            ):
                expected_driver_price = expected_pricing_data['driver'][
                    'additional_prices'
                ]['paid_supply']['price']
            else:
                expected_driver_price = expected_pricing_data['driver'][
                    'price'
                ]
            if is_paid_supply and (
                    'paid_supply'
                    in expected_pricing_data['user'].get(
                        'additional_prices', {},
                    )
            ):
                expected_user_price = expected_pricing_data['user'][
                    'additional_prices'
                ]['paid_supply']['price']
            else:
                expected_user_price = expected_pricing_data['user']['price']

        assert actual.driver_price().total == expected_driver_price['total']
        assert actual.user_price().total == expected_user_price['total']

        assert actual.driver_surge().multiplier == expected_driver_meta.get(
            'setcar.show_surge', None,
        )
        assert actual.driver_surge().surcharge == expected_driver_meta.get(
            'setcar.show_surcharge', None,
        )
        assert actual.user_surge().multiplier == expected_user_meta.get(
            'setcar.show_surge', None,
        )
        assert actual.user_surge().surcharge == expected_user_meta.get(
            'setcar.show_surcharge', None,
        )
    elif expected_pricing_data:
        expected_driver_meta = expected_pricing_data['driver']['meta']
        expected_user_meta = expected_pricing_data['user']['meta']
        if is_paid_supply and (
                'paid_supply'
                in expected_pricing_data['driver'].get('additional_prices', {})
        ):
            expected_driver_price = expected_pricing_data['driver'][
                'additional_prices'
            ]['paid_supply']['price']
        else:
            expected_driver_price = expected_pricing_data['driver']['price']
        if is_paid_supply and (
                'paid_supply'
                in expected_pricing_data['user'].get('additional_prices', {})
        ):
            expected_user_price = expected_pricing_data['user'][
                'additional_prices'
            ]['paid_supply']['price']
        else:
            expected_user_price = expected_pricing_data['user']['price']

        assert actual.driver_price().total == expected_driver_price['total']
        assert actual.user_price().total == expected_user_price['total']

        assert actual.driver_surge().multiplier == expected_driver_meta.get(
            'setcar.show_surge', None,
        )
        assert actual.driver_surge().surcharge == expected_driver_meta.get(
            'setcar.show_surcharge', None,
        )
        assert actual.user_surge().multiplier == expected_user_meta.get(
            'setcar.show_surge', None,
        )
        assert actual.user_surge().surcharge == expected_user_meta.get(
            'setcar.show_surcharge', None,
        )
