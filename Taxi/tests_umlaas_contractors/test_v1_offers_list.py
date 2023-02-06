import pytest

URL = '/umlaas-contractors/contractor-merch/v1/offers_list'
URL_FLUTTER = '/umlaas-contractors/contractor-merch/v1/offers_list_flutter'

PARK_ID = 'park_id'
DRIVER_ID = 'driver_id'
HEADERS = {
    'X-YaTaxi-Park-Id': PARK_ID,
    'X-YaTaxi-Driver-Profile-Id': DRIVER_ID,
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.50',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
    'X-Selection-Id': 'selection_id_1',
    'Accept-Language': 'en_GB',
}


@pytest.mark.experiments3(filename='exp_params_disabled.json')
async def test_ok(taxi_umlaas_contractors, load_json):
    request = load_json('request.json')
    response = await taxi_umlaas_contractors.post(
        URL, request, headers=HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == load_json('unranked_response.json')


@pytest.mark.parametrize(
    ('prioritize_manual_offers', 'slider_cnt'), ((False, 4), (True, 13)),
)
@pytest.mark.experiments3(filename='exp_params_enabled_random.json')
async def test_random(
        taxi_umlaas_contractors,
        load_json,
        prioritize_manual_offers,
        slider_cnt,
        taxi_config,
):
    taxi_config.set_values(
        {'UMLAAS_CONTRACTORS_PRIORITIZE_MANUAL': prioritize_manual_offers},
    )
    request = load_json('request.json')
    response = await taxi_umlaas_contractors.post(
        URL, request, headers=HEADERS,
    )
    assert response.status_code == 200
    unranked_response = load_json('unranked_response.json')
    response_slider_cnt = 0
    response_json = response.json()
    expected_offer_ids = {x['offer_id'] for x in unranked_response['offers']}
    response_offer_ids = {x['offer_id'] for x in response_json['offers']}
    assert response_offer_ids == expected_offer_ids
    for offer in response_json['offers']:
        response_slider_cnt += int(offer['offer_data']['slider'])
    assert response_slider_cnt == slider_cnt


@pytest.mark.experiments3(filename='exp_params_enabled_popularity.json')
async def test_popularity(taxi_umlaas_contractors, load_json, testpoint):
    @testpoint('force_weights')
    def force_weights(data):  # pylint: disable=unused-variable
        return {
            'categories_weights': {'': 0, 'car_maintenance': 1},
            'offers_weights': {'1': 1, '2': 0},
        }

    request = load_json('request.json')
    response = await taxi_umlaas_contractors.post(
        URL, request, headers=HEADERS,
    )
    assert response.status_code == 200
    response_offer_ids = [
        x['immutable_offer_id'] for x in response.json()['offers']
    ]
    assert response_offer_ids[0] == '1'
    assert response_offer_ids[-1] == '2'
    assert set(response_offer_ids[1:-1]) == set(map(str, range(3, 16)))


@pytest.mark.experiments3(filename='exp_params_enabled_popularity.json')
async def test_flutter_popularity(
        taxi_umlaas_contractors, load_json, testpoint,
):
    @testpoint('force_weights')
    def force_weights(data):  # pylint: disable=unused-variable
        return {
            'categories_weights': {'': 0, 'car_maintenance': 1},
            'offers_weights': {'1': 1, '2': 0},
        }

    request = load_json('request.json')
    response = await taxi_umlaas_contractors.post(
        URL_FLUTTER, request, headers=HEADERS,
    )
    assert response.status_code == 200
    response_pinned_offer_ids = [
        x['immutable_offer_id']
        for x in response.json()['pinned_with_ranked_offers']
    ]
    slider_offers = [
        x for x in request['offers'] if x['offer_data'].get('slider', False)
    ]
    expected_pinned_ids = [x['immutable_offer_id'] for x in slider_offers] + [
        '3',
    ]  # pinned offer
    assert set(expected_pinned_ids) == set(
        response_pinned_offer_ids[: len(expected_pinned_ids)],
    )

    response_fully_ranked_offer_ids = [
        x['immutable_offer_id'] for x in response.json()['fully_ranked_offers']
    ]
    assert response_fully_ranked_offer_ids[0] == '1'
    assert response_fully_ranked_offer_ids[-1] == '2'
    assert set(response_fully_ranked_offer_ids[1:]) == set(
        map(str, range(2, 16)),
    )
