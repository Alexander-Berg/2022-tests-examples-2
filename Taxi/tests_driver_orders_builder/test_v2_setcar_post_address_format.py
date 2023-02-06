import pytest


@pytest.mark.parametrize(
    (
        'order_proc_file',
        'expected_address_from',
        'expected_address_to',
        'expected_ui_address_form',
        'expected_ui_address_to',
    ),
    [
        pytest.param(
            'order_core_response_duplication.json',
            'Рядом с: улица 26 Бакинских Комиссаров, 8к3, подъезд 1',
            'ТЦ ТЕСТ, улица 26 Бакинских Комиссаров, 8к3, подъезд 4',
            'Рядом с: улица 26 Бакинских Комиссаров, 8к3',
            'ТЦ ТЕСТ, улица 26 Бакинских Комиссаров, 8к3',
            id='duplication_title',
        ),
        pytest.param(
            'order_core_response_long_title.json',
            'Рядом с: улица 26 Бакинских Комиссаров, 8к3, подъезд 1',
            'улица 26 Бакинских Комиссаров, 8к3, подъезд 4',
            'Рядом с: улица 26 Бакинских Комиссаров, 8к3',
            'улица 26 Бакинских Комиссаров, 8к3',
            id='too_long_title',
        ),
        pytest.param(
            'order_core_response_whitelist.json',
            'Рядом с: улица 26 Бакинских Комиссаров, 8к3, подъезд 1',
            'улица 26 Бакинских Комиссаров, 8к3, магазин, подъезд 4, тест fullname whitelist',
            'Рядом с: улица 26 Бакинских Комиссаров, 8к3',
            'улица 26 Бакинских Комиссаров, 8к3, магазин',
            id='fullname_in_whitelist',
        ),
        pytest.param(
            'order_core_response_to_village.json',
            'Рядом с: улица 26 Бакинских Комиссаров, 8к3, подъезд 1',
            'улица 26 Бакинских Комиссаров, 8к3, подъезд 4',
            'Рядом с: улица 26 Бакинских Комиссаров, 8к3',
            'посёлок Комиссаров, улица 26 Бакинских Комиссаров, 8к3',
            id='district_contains_in_whitelist',
        ),
        pytest.param(
            'order_core_response_normal.json',
            'Рядом с: улица 26 Бакинских Комиссаров, 8к3, подъезд 1',
            'улица 26 Бакинских Комиссаров, 8к3, магазин, подъезд 4',
            'Рядом с: улица 26 Бакинских Комиссаров, 8к3',
            'улица 26 Бакинских Комиссаров, 8к3, магазин',
            id='normal_response',
        ),
    ],
)
@pytest.mark.experiments3(filename='exp3_config_address_format.json')
async def test_address_builder(
        taxi_driver_orders_builder,
        load_json,
        experiments3,
        mockserver,
        params_wo_original_setcar,
        expected_address_from,
        expected_address_to,
        expected_ui_address_form,
        expected_ui_address_to,
        order_proc_file,
        order_proc,
):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='driver_orders_builder_show_destination_by_activity_and_tags',
        consumers=['driver-orders-builder/setcar'],
        default_value={'show': True},
        clauses=[],
    )
    await taxi_driver_orders_builder.invalidate_caches()

    order_proc.set_file(load_json, order_proc_file)

    response = await taxi_driver_orders_builder.post(
        **params_wo_original_setcar,
    )

    assert response.status_code == 200, response.text
    response_json = response.json()['setcar']
    assert 'acceptance_items' in response_json['ui']
    assert response_json['address_from']['Street'] == expected_address_from
    assert response_json['address_to']['Street'] == expected_address_to
    assert len(response_json['ui']['acceptance_items']) == 3
    ui_acceptance_items = response_json['ui']['acceptance_items']
    assert ui_acceptance_items[1]['subtitle'] == expected_ui_address_form
    assert ui_acceptance_items[-1]['subtitle'] == expected_ui_address_to
