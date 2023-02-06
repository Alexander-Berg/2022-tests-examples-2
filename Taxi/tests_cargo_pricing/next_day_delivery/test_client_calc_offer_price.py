import pytest

from tests_cargo_pricing.next_day_delivery import utils


# pylint: disable=invalid-name
pytestmark = [
    pytest.mark.config(
        CURRENCY_ROUNDING_RULES={
            'ILS': {'__default__': 0.1},
            '__default__': {'__default__': 0.01},
        },
    ),
]


@pytest.mark.geoareas(tg_filename='typed_geoareas_base.json')
async def test_offer_calc(
        v1_ndd_offer_calc_client_creator,
        mock_ndd_tariff_composer,
        default_calcplan_config,
):
    response = await v1_ndd_offer_calc_client_creator.execute()
    assert response.status_code == 200
    resp = response.json()

    assert resp['calculation'].pop('id').startswith('cargo-pricing/ndd/v1/')

    created_ts = resp['calculation'].pop('created_ts')
    assert created_ts != '1970-01-01T00:00:00+00:00'
    assert created_ts != ''

    assert resp == {
        'calculation': {},
        'currency': {'code': 'RUB'},
        'price': utils.get_default_calculated_price(),
    }

    tariff_request = mock_ndd_tariff_composer.request
    assert tariff_request == {
        'destination_point': [37.597414, 55.739554],
        'employer_id': 'a82624ff-303a-4242-bf93-cceb31869bc1',
        'source_point': [37.0, 55.0],
        'tariff_category': 'interval_with_fees',
    }


@pytest.mark.geoareas(tg_filename='typed_geoareas_base.json')
async def test_recalc_after_offer_calc(
        v1_ndd_offer_calc_client_creator,
        v1_ndd_calc_client_creator,
        mock_ndd_tariff_composer_retrieve,
        default_calcplan_config,
        reset_calcplan_config,
):
    response1 = await v1_ndd_offer_calc_client_creator.execute()
    assert response1.status_code == 200
    resp1 = response1.json()
    assert resp1['price'] == utils.get_default_calculated_price()
    prev_calc_id = resp1['calculation']['id']

    await reset_calcplan_config.reset(plan=[])

    response2 = await v1_ndd_calc_client_creator.execute(
        previous_calc_id=prev_calc_id,
    )
    assert response2.status_code == 200
    resp2 = response2.json()
    assert resp2['calculation']['id'] != prev_calc_id
    assert resp2['price'] == resp1['price']
    tariff = utils.get_default_tariff_composition()
    assert (
        tariff['composition_id']
        == mock_ndd_tariff_composer_retrieve.requested_id
    )


@pytest.mark.geoareas(tg_filename='typed_geoareas_base.json')
async def test_offer_calc_retry_idempotency_token(
        v1_ndd_offer_calc_client_creator,
        mock_ndd_tariff_composer,
        default_calcplan_config,
        reset_calcplan_config,
):
    first_response = await v1_ndd_offer_calc_client_creator.execute()
    assert first_response.status_code == 200

    await reset_calcplan_config.reset(plan=[])

    second_response = await v1_ndd_offer_calc_client_creator.execute()
    assert second_response.status_code == 200

    assert second_response.json() == first_response.json()


@pytest.mark.geoareas(tg_filename='typed_geoareas_base.json')
async def test_offer_calc_no_tariff(
        v1_ndd_offer_calc_client_creator,
        default_calcplan_config,
        mock_ndd_tariff_composer,
):
    mock_ndd_tariff_composer.response_status_code = 404
    response = await v1_ndd_offer_calc_client_creator.execute()
    assert response.status_code == 400
    assert response.json() == {
        'code': 'tariff_not_found',
        'message': 'no tariff found: cannot compose tariff',
    }


@pytest.mark.geoareas(tg_filename='typed_geoareas_base.json')
async def test_offer_calc_with_other_country(
        v1_ndd_offer_calc_client_creator,
        default_calcplan_config,
        mock_countries_list,
):
    v1_ndd_offer_calc_client_creator.payload['locale'] = {'iso_code': 'isr'}
    response = await v1_ndd_offer_calc_client_creator.execute()
    assert response.status_code == 200

    price = utils.get_default_calculated_price()
    price['total'] = round(
        price['total_without_vat'] * 1.17, -1,
    )  # VAT in Israel

    assert mock_countries_list.mock.times_called == 1

    assert response.json()['currency'] == {'code': 'ILS'}
    assert response.json()['price'] == price
