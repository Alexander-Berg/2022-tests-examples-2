import pytest


@pytest.mark.parametrize(
    'payment_method,cost,need_accept',
    [
        ('card', '100', False),
        ('card', '100000', True),
        ('corp', '100', False),
        ('corp', '100000', True),
    ],
)
async def test_need_accept(
        web_processing_antifraud,
        mock_taxi_tariffs,
        load_json,
        payment_method,
        cost,
        need_accept,
):
    @mock_taxi_tariffs('/v1/tariff_settings/bulk_retrieve')
    async def _mock_tariffs(*args, **kwargs):
        return load_json('tariff_settings.json')

    response = await web_processing_antifraud.need_accept_taxi.make_request(
        cost=cost, payment_method_type=payment_method,
    )
    assert response.status == 200

    content = await response.json()
    if need_accept:
        assert content == {'need_accept': need_accept, 'reason': 'zone_limit'}
    else:
        assert content == {'need_accept': False}


@pytest.mark.config(
    TRACK_ORDER_COST_FIELD_FOR_COMPARING='taximeter_track_cost',
    MIN_PRICE_COST_DIFF_FOR_ACCEPT={'RUB': '50'},
    MAX_TRACK_COST_DIFF_COEF=0.1,
)
@pytest.mark.parametrize(
    'taximeter_cost,taximeter_track_cost,gps_service_track_cost,need_accept',
    [
        ('100', '100', None, False),
        ('1000', '100', None, True),
        ('100', None, '99', False),
        ('1000', None, '100', True),
        ('49', None, '1', False),
    ],
)
async def test_taximeter_diff_cost(
        web_processing_antifraud,
        mock_taxi_tariffs,
        load_json,
        taximeter_cost,
        taximeter_track_cost,
        gps_service_track_cost,
        need_accept,
):
    @mock_taxi_tariffs('/v1/tariff_settings/bulk_retrieve')
    async def _mock_tariffs(*args, **kwargs):
        return load_json('tariff_settings.json')

    response = await web_processing_antifraud.need_accept_taxi.make_request(
        fixed_price=False,
        track_cost={
            'taximeter_cost': taximeter_cost,
            'taximeter_track_cost': taximeter_track_cost,
            'gps_service_track_cost': gps_service_track_cost,
        },
    )
    assert response.status == 200

    content = await response.json()
    if need_accept:
        assert content == {
            'need_accept': need_accept,
            'reason': 'different_costs',
        }
    else:
        assert content == {'need_accept': False}
