import copy
import json

import pytest

AUTHORIZED_HEADERS = {
    'X-YaTaxi-UserId': '12345678901234567890123456789012',
    'X-YaTaxi-PhoneId': '123456789012345678901234',
    'X-Yandex-UID': '400000000',
    'X-YaTaxi-Bound-Uids': '400000000,834149473,834149474',
}
BASE_REQUEST = {
    'id': '12345678901234567890123456789012',
    'll': [37.57, 55.72],
    'dx': 140.1,
}


@pytest.mark.translations(
    client_messages={
        'pickup_point.is_last.label': {'ru': 'You were here'},
        'best_point_a': {'ru': 'Good place!'},
    },
)
@pytest.mark.experiments3(filename='exp3_last_point.json')
@pytest.mark.parametrize(
    'hide_if_other_labels,hide_if_pin_in_point,pos,hidden',
    [
        (False, False, [37.57, 55.72], False),
        (True, False, [37.57, 55.72], True),
        (False, True, [37.57, 55.72], False),
        (False, True, [37.5763, 55.7272], True),
    ],
)
async def test_pickuppoints_simple(
        taxi_persuggest,
        load_json,
        yamaps,
        mockserver,
        experiments3,
        hide_if_other_labels,
        hide_if_pin_in_point,
        pos,
        hidden,
):
    exp3_best_point = load_json('exp3_best_pickuppoint_label.json')
    value = exp3_best_point['experiments'][0]['clauses'][0]['value']
    settings = value['settings']['a']
    settings['hide_if_other_labels'] = hide_if_other_labels
    settings['hide_if_pin_in_point'] = hide_if_pin_in_point
    experiments3.add_experiments_json(exp3_best_point)

    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones(request):
        request_body = json.loads(request.get_data())
        assert request_body['type'] == 'a'
        return load_json('zones_empty_response.json')

    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/finalsuggest')
    def _mock_umlaas_geo(request):
        return load_json('uml_finalsuggest_points.json')

    @mockserver.json_handler('/special-zones/special-zones/v1/filter')
    def _mock_pp_bzf(request):
        return load_json('bzf_response.json')

    yamaps.add_fmt_geo_object(load_json('yamaps_simple_geo_object.json'))

    req = copy.deepcopy(BASE_REQUEST)
    req['ll'] = pos
    response = await taxi_persuggest.post(
        '/3.0/pickuppoints', req, headers=AUTHORIZED_HEADERS,
    )

    assert response.status_code == 200
    expected_response = load_json('expected_response_simple.json')
    if not hidden:
        expected_response['points'][1]['label'] = {'text': 'Good place!'}
    assert response.json() == expected_response


@pytest.mark.config(PICKUPPOINTS_ENABLED=False)
async def test_pickuppoints_disabled(taxi_persuggest):
    response = await taxi_persuggest.post(
        '/3.0/pickuppoints', BASE_REQUEST, headers=AUTHORIZED_HEADERS,
    )

    assert response.status_code == 200
    assert response.json() == {'points': []}
