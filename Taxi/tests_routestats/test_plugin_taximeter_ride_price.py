import pytest


@pytest.mark.parametrize(
    'experiment_enabled',
    [
        pytest.param(
            True,
            marks=pytest.mark.experiments3(
                filename='exp_taximeter_ride_price.json',
            ),
        ),
        pytest.param(False),
    ],
)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.tariff_settings(filename='tariff_settings.json')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.routestats_plugins(
    names=['top_level:proxy', 'top_level:taximeter_ride_price'],
)
@pytest.mark.translations(
    tariff={'routestats_description_taximeter_price': {'ru': 'rub/km'}},
)
async def test_taximeter_ride_price(
        experiment_enabled, taxi_routestats, mockserver, load_json,
):
    @mockserver.json_handler(f'/protocol-routestats/internal/routestats')
    def _protocol(request):
        return {
            'internal_data': load_json('internal_data.json'),
            **load_json('protocol_response.json'),
        }

    req = load_json('request.json')
    response = await taxi_routestats.post('v1/routestats', req)
    assert response.status_code == 200

    service_levels = response.json()['service_levels']

    for level in service_levels:
        if level['class'] == 'econom' and experiment_enabled:
            assert level['description_parts']['value'] == 'rub/km'
        else:
            assert level['description_parts']['value'] != 'rub/km'
