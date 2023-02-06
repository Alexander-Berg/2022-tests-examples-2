import pytest

from tests_cargo_pricing import utils

# pylint: disable=invalid-name
pytestmark = [
    pytest.mark.config(
        CARGO_PRICING_DB_SOURCES_FOR_READ={
            'v1/taxi/calc/retrieve': ['pg', 'yt'],
            'v2/taxi/calc/retrieve': ['pg', 'yt'],
        },
    ),
]


async def test_retrieve_calc(v1_calc_creator, v1_retrieve_calc):
    create_resp = await v1_calc_creator.execute()
    assert create_resp.status_code == 200
    calc = create_resp.json()
    calc_id = calc['calc_id']
    response = await v1_retrieve_calc(calc_id)

    assert response.status_code == 200
    resp = response.json()
    assert (
        resp['details'].pop('total_distance')[:6]
        == calc['details'].pop('total_distance')[:6]
    )
    assert resp['calc_id'] == calc_id
    assert resp['details'] == calc['details']
    assert resp['price'] == calc['price']
    assert resp['request'] == v1_calc_creator.payload
    assert resp['taxi_pricing_response'] == calc['taxi_pricing_response']
    assert (
        resp['taxi_pricing_response_parts']
        == calc['taxi_pricing_response_parts']
    )
    assert resp.get('recalc_taxi_pricing_response', None) == calc.get(
        'recalc_taxi_pricing_response', None,
    )
    assert resp['units'] == {
        'currency': 'RUB',
        'distance': 'kilometer',
        'time': 'second',
    }
    assert resp['services'] == calc['services']
    assert resp['pricing_case'] == calc['details']['pricing_case']
    assert resp['waypoints'] == calc['details']['waypoints']


async def test_retrieve_calc_with_coupon_and_discounts(
        v1_calc_creator, v1_retrieve_calc, load_json,
):
    utils.enable_coupon_and_discounts(v1_calc_creator, load_json)
    create_resp = await v1_calc_creator.execute()
    assert create_resp.status_code == 200
    calc = create_resp.json()
    calc_id = calc['calc_id']
    response = await v1_retrieve_calc(calc_id)

    assert response.status_code == 200
    resp = response.json()
    assert (
        resp['details'].pop('total_distance')[:6]
        == calc['details'].pop('total_distance')[:6]
    )
    assert resp['calc_id'] == calc_id
    assert resp['details'] == calc['details']
    assert resp['price'] == calc['price']
    assert resp['strikeout_price'] == calc['strikeout_price']
    assert resp['request'] == v1_calc_creator.payload
    assert resp['taxi_pricing_response'] == calc['taxi_pricing_response']
    assert resp['units'] == {
        'currency': 'RUB',
        'distance': 'kilometer',
        'time': 'second',
    }
    assert resp['services'] == calc['services']
    assert resp['pricing_case'] == calc['details']['pricing_case']
    assert resp['waypoints'] == calc['details']['waypoints']
    assert resp['price_extra_info'] == calc['price_extra_info']


async def test_retrieve_calc_with_combo(
        taxi_cargo_pricing,
        v2_calc_creator,
        pgsql,
        load_json,
        v1_retrieve_calc,
):
    request = v2_calc_creator.payload['calc_requests'][0]
    request['calculate_combo_prices'] = True
    utils.set_v2prepare_resp_combo(v2_calc_creator, load_json)
    create_resp = await v2_calc_creator.execute()
    assert create_resp.status_code == 200
    calc = create_resp.json()['calculations'][0]
    calc_id = calc['result']['alternative_options_calcs'][0]['calc_id']
    response = await v1_retrieve_calc(calc_id)
    assert response.json()['details']['combo_coefficient'] == '0.5'


async def test_bulk_retrieve_calc(
        v1_calc_creator, v2_retrieve_calc, load_json,
):
    create_resp = await v1_calc_creator.execute()
    assert create_resp.status_code == 200
    calc = create_resp.json()
    response = await v2_retrieve_calc([calc['calc_id']])

    assert response.status_code == 200
    resp = response.json()

    resp_calc = resp['calculations'][0]['result']
    assert (
        resp_calc['details']['algorithm']['pricing_case']
        == calc['details']['pricing_case']
    )
    assert (
        resp_calc['details']['algorithm']['pricing_case_reason']
        == calc['details']['pricing_case_reason']
    )
    assert resp_calc['details']['waypoints'] == calc['details']['waypoints']
    assert resp_calc['details']['services'] == calc['services']
    assert (
        resp_calc['diagnostics']['taxi_pricing_response']
        == calc['taxi_pricing_response']
    )
    assert resp_calc['prices']['total_price'] == calc['price']
    assert (
        resp_calc['legacy']['taxi_pricing_response_parts']
        == calc['taxi_pricing_response_parts']
    )


async def test_bulk_retrieve_calcs(
        v1_calc_creator, v2_retrieve_calc, load_json,
):
    calcs = []

    for num in range(2):
        if num == 1:
            utils.enable_coupon_and_discounts(v1_calc_creator, load_json)
        create_resp = await v1_calc_creator.execute()
        assert create_resp.status_code == 200
        calc = create_resp.json()
        calcs.append(calc)

    response = await v2_retrieve_calc(
        [calcs[0]['calc_id'], calcs[1]['calc_id']],
    )
    assert response.status_code == 200
    resp = response.json()

    calcs = sorted(calcs, key=lambda calc: calc['calc_id'])
    resp_calcs = sorted(resp['calculations'], key=lambda calc: calc['calc_id'])

    for i in range(2):
        assert resp_calcs[i]['calc_id'] == calcs[i]['calc_id']
        result = resp_calcs[i]['result']
        assert result.get('price_extra_info') == calcs[i].get(
            'price_extra_info',
        )
        assert result['prices'].get('strikeout_price') == calcs[i].get(
            'strikeout_price',
        )


@pytest.mark.yt(
    schemas=[
        'yt/yt_calculations_raw_schema.yaml',
        'yt/yt_receipts_raw_schema.yaml',
    ],
    dyn_table_data=['yt/yt_calculations_raw.yaml', 'yt/yt_receipts_raw.yaml'],
)
async def test_bulk_retrieve_calc_not_valid_id(
        v1_calc_creator, v2_retrieve_calc, yt_apply,
):
    create_resp = await v1_calc_creator.execute()
    assert create_resp.status_code == 200
    calc = create_resp.json()
    not_valid_id = 'cargo-pricing/v1/' + '00000000-0000-0000-0000-000000000000'
    response = await v2_retrieve_calc([calc['calc_id'], not_valid_id])
    assert response.status_code == 200
    resp = response.json()

    error_resp_calc = resp['calculations'][0]
    resp_calc = resp['calculations'][1]
    if resp_calc['calc_id'] == not_valid_id:
        error_resp_calc, resp_calc = resp_calc, error_resp_calc

    assert error_resp_calc['calc_id'] == not_valid_id
    assert error_resp_calc['result']['code'] == 'not_found'
    assert resp_calc['calc_id'] == calc['calc_id']
    assert isinstance(resp_calc['result']['details']['waypoints'], list)


@pytest.mark.yt(
    schemas=[
        'yt/yt_calculations_raw_schema.yaml',
        'yt/yt_receipts_raw_schema.yaml',
    ],
    dyn_table_data=['yt/yt_calculations_raw.yaml', 'yt/yt_receipts_raw.yaml'],
)
async def test_retrieve_calc_yt(yt_apply, v1_retrieve_calc):
    response = await v1_retrieve_calc(
        calc_id='cargo-pricing/v1/731d5f77-8c8b-4ac9-b556-9d38357b92b2',
    )

    assert response.status_code == 200
    resp = response.json()
    assert isinstance(resp['request'], dict)
    assert isinstance(resp['taxi_pricing_response'], dict)
    assert isinstance(resp['details']['waypoints'], list)


@pytest.mark.yt(
    schemas=[
        'yt/yt_calculations_raw_schema.yaml',
        'yt/yt_receipts_raw_schema.yaml',
    ],
    dyn_table_data=['yt/yt_calculations_raw.yaml', 'yt/yt_receipts_raw.yaml'],
)
async def test_retrieve_calc_yt_discount_and_coupon_fields(
        yt_apply, v1_retrieve_calc,
):
    response = await v1_retrieve_calc(
        calc_id='cargo-pricing/v1/731d5f77-8c8b-4ac9-b556-9d38357b92b2',
    )

    assert response.status_code == 200
    resp = response.json()
    assert resp['details']['coupon_price'] == '12.5'
    assert resp['details']['discount_price'] == '11.5'
    assert resp['strikeout_price'] == '312'
    coupon = resp['price_extra_info']['coupon']
    assert coupon['coupon'] == 'coupon22'
    assert coupon['was_applied']
    resp_services = resp['services']
    discount_services = [x for x in resp_services if x['name'] == 'discount']
    assert discount_services == [
        {
            'components': [
                {
                    'name': 'discount',
                    'text': 'Вычет по скидке',
                    'total_price': '-11.5',
                },
            ],
            'name': 'discount',
            'text': 'Скидки',
            'total_price': '-11.5',
        },
    ]

    coupon_services = [x for x in resp_services if x['name'] == 'coupon']
    assert coupon_services == [
        {
            'components': [
                {
                    'name': 'coupon',
                    'text': 'Вычет по промокоду',
                    'total_price': '-12.5',
                },
            ],
            'name': 'coupon',
            'text': 'Промокоды',
            'total_price': '-12.5',
        },
    ]


@pytest.mark.yt(
    schemas=[
        'yt/yt_calculations_raw_schema.yaml',
        'yt/yt_receipts_raw_schema.yaml',
    ],
    dyn_table_data=['yt/yt_calculations_raw.yaml', 'yt/yt_receipts_raw.yaml'],
)
async def test_retrieve_calc_yt_paid_supply_details_and_combo_coeff_fields(
        yt_apply, v1_retrieve_calc,
):
    response = await v1_retrieve_calc(
        calc_id='cargo-pricing/v1/731d5f77-8c8b-4ac9-b556-9d38357b92b2',
    )

    assert response.status_code == 200
    resp = response.json()
    assert resp['details']['paid_supply_price'] == '151.3'
    assert resp['details']['combo_coefficient'] == '0.5'
    resp_services = resp['services']
    paid_supply_services = [
        x for x in resp_services if x['name'] == 'paid_supply'
    ]
    assert paid_supply_services == [
        {
            'components': [
                {
                    'name': 'paid_supply',
                    'text': 'Цена платной подачи',
                    'total_price': '151.3',
                },
            ],
            'name': 'paid_supply',
            'text': 'Платная подача',
            'total_price': '151.3',
        },
    ]


@pytest.mark.yt(
    schemas=[
        'yt/yt_calculations_raw_schema.yaml',
        'yt/yt_receipts_raw_schema.yaml',
    ],
    dyn_table_data=['yt/yt_calculations_raw.yaml', 'yt/yt_receipts_raw.yaml'],
)
async def test_retrieve_calc_yt_empty_fields(yt_apply, v1_retrieve_calc):
    response = await v1_retrieve_calc(
        calc_id='cargo-pricing/v1/4005d50f-d838-4ea5-9fd6-404af4d43c71',
    )

    assert response.status_code == 200
    resp = response.json()
    assert isinstance(resp['request'], dict)
    assert isinstance(resp['taxi_pricing_response'], dict)


@pytest.mark.yt(
    schemas=[
        'yt/yt_calculations_raw_schema.yaml',
        'yt/yt_receipts_raw_schema.yaml',
    ],
    dyn_table_data=['yt/yt_calculations_raw.yaml', 'yt/yt_receipts_raw.yaml'],
)
async def test_retrieve_calculations_yt(v2_retrieve_calc, yt_apply):
    response = await v2_retrieve_calc(
        [
            'cargo-pricing/v1/731d5f77-8c8b-4ac9-b556-9d38357b92b2',
            'cargo-pricing/v1/4005d50f-d838-4ea5-9fd6-404af4d43c71',
        ],
    )

    assert response.status_code == 200
    resp = response.json()
    assert len(resp['calculations']) == 2
    for i in range(2):
        assert isinstance(resp['calculations'][i], dict)
        assert isinstance(
            resp['calculations'][i]['result']['details']['waypoints'], list,
        )


async def test_bulk_retrieve_calcs_with_route(
        v2_retrieve_calc, v1_calc_creator, load_json,
):
    calcs = []

    for num in range(2):
        if num == 1:
            utils.enable_coupon_and_discounts(v1_calc_creator, load_json)
        create_resp = await v1_calc_creator.execute()
        assert create_resp.status_code == 200
        calc = create_resp.json()
        calcs.append(calc)

    response = await v2_retrieve_calc(
        calc_ids=[calcs[0]['calc_id'], calcs[1]['calc_id']],
        response_controller={'diagnostics': {'route': True}},
    )
    assert response.status_code == 200
    resp = response.json()

    calcs = sorted(calcs, key=lambda calc: calc['calc_id'])
    resp_calcs = sorted(resp['calculations'], key=lambda calc: calc['calc_id'])
    request = v1_calc_creator.payload
    route = resp_calcs[0]['result']['diagnostics']['route'][0]
    assert route['from'] == request['waypoints'][0]['position']
    assert route['to'] == request['waypoints'][1]['position']
    assert route['path']


@pytest.mark.yt(
    schemas=[
        'yt/yt_calculations_raw_schema.yaml',
        'yt/yt_receipts_raw_schema.yaml',
    ],
    dyn_table_data=['yt/yt_calculations_raw.yaml', 'yt/yt_receipts_raw.yaml'],
)
async def test_retrieve_calc_yt_with_shared_calc_parts(
        yt_apply,
        v1_retrieve_calc,
        v1_calc_creator,
        lazy_config_shared_calc_parts,
):
    base_price = {
        'boarding': 699,
        'destination_waiting': 25,
        'distance': 487.0624757753609,
        'requirements': 0,
        'time': 0,
        'transit_waiting': 0,
        'waiting': 10,
    }
    prepared_category = {
        'user': {
            'meta': {},
            'base_price': base_price,
            'modifications': {'for_fixed': [1, 2], 'for_taximeter': [4, 6]},
            'price': {'total': 1961},
            'tariff_id': '',
            'category_id': '',
            'category_prices_id': 'c/13330055',
            'additional_prices': {},
            'data': {'category': 'cargo'},
        },
        'driver': {
            'meta': {},
            'base_price': base_price,
            'modifications': {
                'for_fixed': [11, 22],
                'for_taximeter': [44, 66],
            },
            'price': {'total': 1961},
            'tariff_id': '',
            'category_id': '',
            'category_prices_id': 'c/13330055',
            'additional_prices': {},
            'data': {'category': 'cargo'},
        },
        'fixed_price': True,
        'geoarea_ids': ['g/2bab7eff1aa848b681370b2bd83cfbf9'],
        'currency': {'fraction_digits': 0, 'name': 'RUB', 'symbol': '\\u20bd'},
        'tariff_info': {
            'distance': {
                'included_kilometers': 0,
                'price_per_kilometer': 27.599999999999998,
            },
            'max_free_waiting_time': 600,
            'point_a_free_waiting_time': 600,
            'point_b_free_waiting_time': 600,
            'time': {'included_minutes': 0, 'price_per_minute': 0},
        },
    }

    await lazy_config_shared_calc_parts(
        shared_fields=[
            {
                'field': 'prepared_category',
                'sub_fields': [
                    'currency',
                    'tariff_info',
                    'geoarea_ids',
                    'driver.modifications',
                    'user',
                    'driver.base_price',
                ],
            },
        ],
    )
    # добавляем в горячую базу расчет с shared_calc_parts,
    # у которых hash как у calc в yt
    v1_calc_creator.mock_prepare.categories = {'cargocorp': prepared_category}
    create_resp = await v1_calc_creator.execute()
    assert create_resp.status_code == 200

    # загружаем расчет из yt, ожидая, что shared_calc_parts
    # возьмутся из горячей БД по hash
    response = await v1_retrieve_calc(
        calc_id='cargo-pricing/v1/3065451f-d638-43a5-91d6-454a64746c16',
    )

    assert response.status_code == 200
    resp = response.json()
    assert resp['taxi_pricing_response'] == prepared_category


@pytest.mark.yt(
    schemas=[
        'yt/yt_calculations_raw_schema.yaml',
        'yt/yt_receipts_raw_schema.yaml',
        'yt/yt_shared_calcs_parts_raw_schema.yaml',
    ],
    dyn_table_data=[
        'yt/yt_calculations_raw.yaml',
        'yt/yt_receipts_raw.yaml',
        'yt/yt_shared_calcs_parts_raw.yaml',
    ],
)
async def test_retrieve_calc_yt_with_shared_calc_parts_from_yt(
        yt_apply,
        v1_retrieve_calc,
        v1_calc_creator,
        lazy_config_shared_calc_parts,
):
    await lazy_config_shared_calc_parts(
        shared_fields=[
            {
                'field': 'prepared_category',
                'sub_fields': ['driver.modifications', 'user.modifications'],
            },
        ],
    )
    prepared_category = {
        'user': {
            'modifications': {
                'for_taximeter': [1885, 1886, 1292, 2282, 2938, 2432, 2429],
            },
        },
        'driver': {
            'modifications': {
                'for_taximeter': [
                    1885,
                    1886,
                    1292,
                    2276,
                    2269,
                    2822,
                    2750,
                    2307,
                    2434,
                    2447,
                    3011,
                ],
            },
        },
    }

    response = await v1_retrieve_calc(
        calc_id='cargo-pricing/v1/3065451f-d638-43a5-91d6-454a64746c17',
    )

    assert response.status_code == 200
    resp = response.json()
    assert resp['taxi_pricing_response'] == prepared_category


@pytest.mark.yt(
    schemas=[
        'yt/yt_calculations_raw_schema.yaml',
        'yt/yt_receipts_raw_schema.yaml',
    ],
    dyn_table_data=['yt/yt_calculations_raw.yaml', 'yt/yt_receipts_raw.yaml'],
)
async def test_bulk_retrieve_calc_with_backend_variables(
        yt_apply, v2_retrieve_calc,
):
    response = await v2_retrieve_calc(
        ['cargo-pricing/v1/731d5f77-8c8b-4ac9-b556-9d38357b92b2'],
    )

    assert response.status_code == 200
    resp = response.json()
    assert len(resp['calculations']) == 1
    assert (
        resp['calculations'][0]['result']['details']['tariff']['category_name']
        == 'courier_for_performer'
    )


@pytest.mark.yt(
    schemas=[
        'yt/yt_calculations_raw_schema.yaml',
        'yt/yt_receipts_raw_schema.yaml',
    ],
    dyn_table_data=['yt/yt_calculations_raw.yaml', 'yt/yt_receipts_raw.yaml'],
)
async def test_bulk_retrieve_calc_with_entity_id(
        yt_apply,
        v2_retrieve_calc,
        mock_get_processing_events,
        conf_exp3_processing_events_saving_enabled,
):
    response = await v2_retrieve_calc(
        [
            'cargo-pricing/v1/731d5f77-8c8b-4ac9-b556-9d38357b92b2',
            'cargo-pricing/v1/4005d50f-d838-4ea5-9fd6-404af4d43c71',
        ],
    )

    assert response.status_code == 200
    assert mock_get_processing_events.mock.times_called == 1
    assert mock_get_processing_events.requests[0].query['item_id'] == 'claim1'
