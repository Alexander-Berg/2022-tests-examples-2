import pytest


@pytest.fixture(name='physical_price_transforms')
def _physical_price_transforms(
        v1_ndd_calc_client_creator, mock_ndd_tariff_composer, taxi_config,
):
    taxi_config.set_values(
        {
            'CARGO_PRICING_NDD_CALCULATION_PLAN': {
                'plan': [{'stage_name': 'AddPhysical', 'version': 1}],
            },
        },
    )

    async def execute(weights, prices_per_kg):
        included_weight_price = 11
        req = v1_ndd_calc_client_creator.payload
        physical = req['model']['resource']['features'][2][
            'resource_physical_feature'
        ]['physical_dims']
        tariff = mock_ndd_tariff_composer.response['tariff']
        tariff['parcels']['weight_prices'] = prices_per_kg
        tariff['parcels']['included_weight_price'] = str(included_weight_price)

        result_prices = []
        for weight in weights:
            physical['weight_gross'] = weight * 1000
            req['idempotency_token'] = str(weight)

            response = await v1_ndd_calc_client_creator.execute()
            assert response.status_code == 200
            resp = response.json()

            duty_price = resp['price']['total']
            cleaned_price = duty_price / 100 - included_weight_price
            result_prices.append(cleaned_price)

        return result_prices

    return execute


@pytest.mark.geoareas(tg_filename='typed_geoareas_base.json')
async def test_physical_price_transforms_pricemap(physical_price_transforms):
    prices_per_kg = [
        {'begin': '5.0', 'price_per_kilogram': '10.0'},
        {'begin': '10.0', 'price_per_kilogram': '20.0'},
        {'begin': '20.0', 'price_per_kilogram': '30.0'},
        {'begin': '25.0', 'price_per_kilogram': '40.0'},
    ]
    prices = await physical_price_transforms(
        weights=[1, 7, 10, 15, 21, 26, 26.5], prices_per_kg=prices_per_kg,
    )
    assert prices == [0, 20, 50, 150, 280, 440, 480]


@pytest.mark.geoareas(tg_filename='typed_geoareas_base.json')
async def test_physical_price_transforms_empty_pricemap(
        physical_price_transforms,
):
    prices = await physical_price_transforms(weights=[7], prices_per_kg=[])
    assert prices == [0]


@pytest.mark.geoareas(tg_filename='typed_geoareas_base.json')
@pytest.mark.config(
    CARGO_PRICING_NDD_CALCULATION_PLAN={
        'plan': [
            {'stage_name': 'AddIntake', 'version': 1},
            {'stage_name': 'AddReturn', 'version': 1},
        ],
    },
)
async def test_add_return_transform(v1_ndd_calc_client_creator):
    response = await v1_ndd_calc_client_creator.execute()
    assert response.status_code == 200
    assert response.json()['price']['total'] == 1000


@pytest.mark.geoareas(tg_filename='typed_geoareas_base.json')
@pytest.mark.config(
    CARGO_PRICING_NDD_CALCULATION_PLAN={
        'plan': [{'stage_name': 'AddIntake', 'version': 1}],
    },
)
async def test_add_intake_transform(v1_ndd_offer_calc_client_creator):
    response = await v1_ndd_offer_calc_client_creator.execute()
    assert response.status_code == 200
    assert response.json()['price']['total'] == 10000


@pytest.mark.geoareas(tg_filename='typed_geoareas_base.json')
@pytest.mark.config(
    CARGO_PRICING_NDD_CALCULATION_PLAN={
        'plan': [{'stage_name': 'AddItems', 'version': 1}],
    },
)
async def test_add_items_transform(
        v1_ndd_offer_calc_client_creator, mock_ndd_tariff_composer,
):
    v1_ndd_offer_calc_client_creator.payload['items'] = [
        {
            'billing_details': {
                'refundable': True,
                'i_n_n': '7705739450',
                'currency': 'RUB',
                'assessed_unit_price': 4900,
                'n_d_s': 20,
                'tax_system_code': 1,
            },
        },
        {
            'billing_details': {
                'refundable': True,
                'i_n_n': '7705739450',
                'currency': 'RUB',
                'assessed_unit_price': 1000,
                'n_d_s': 20,
                'tax_system_code': 1,
            },
            'count': 3,
        },
    ]
    mock_ndd_tariff_composer.response['tariff']['parcels'][
        'add_declared_value_pct'
    ] = '10'
    response = await v1_ndd_offer_calc_client_creator.execute()
    assert response.status_code == 200
    assert response.json()['price']['total'] == 790


@pytest.mark.geoareas(tg_filename='typed_geoareas_base.json')
@pytest.mark.config(
    CARGO_PRICING_NDD_CALCULATION_PLAN={
        'plan': [
            {'stage_name': 'AddIntake', 'version': 1},
            {'stage_name': 'AddVat', 'version': 1},
        ],
    },
)
async def test_add_vat_transform(v1_ndd_calc_client_creator):
    response = await v1_ndd_calc_client_creator.execute()
    assert response.status_code == 200
    assert response.json()['price'] == {
        'total': 12000,
        'total_without_vat': 10000,
    }
