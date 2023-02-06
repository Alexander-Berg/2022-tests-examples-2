import json

import pytest


@pytest.mark.parametrize('yamaps_second_call', [True, False])
async def test_geomagnet_request(
        taxi_persuggest, mockserver, load_json, yamaps, yamaps_second_call,
):
    @yamaps.set_fmt_geo_objects_callback
    def _get_geo_objects(request):
        resp = load_json('yamaps_response.json')
        if request.args['ll'] == '76.000000,52.000000':
            if not yamaps_second_call:
                return []
            resp['name'] = 'After move short'
            resp['geocoder']['address'][
                'formatted_address'
            ] = 'After move full'
        return [resp]

    # pylint: disable=unused-variable
    @mockserver.json_handler('/special-zones/special-zones/v1/filter')
    def mock_zones(request):
        return {'results': [{'in_zone': False}]}

    response = await taxi_persuggest.post(
        '/3.0/geomagnet', load_json('geomagnet_request.json'),
    )
    expected_response = load_json('expected_geomagnet_response.json')
    if yamaps_second_call:
        expected_response['short_text'] = 'After move short'
        expected_response['full_text'] = 'After move full'
    assert response.status_code == 200
    assert response.json() == expected_response


@pytest.mark.config(MAX_ENTRANCE_LENGTH=6)
@pytest.mark.parametrize(
    'porch_number,codes', [('9' * 7, [400]), ('9' * 6, [200, 404])],
)
async def test_geomagnet_long_porch_request(
        taxi_persuggest, mockserver, load_json, yamaps, porch_number, codes,
):
    yamaps.add_fmt_geo_object(load_json('yamaps_response.json'))

    req = load_json('geomagnet_request.json')
    req['porch_number'] = porch_number

    response = await taxi_persuggest.post('/3.0/geomagnet', req)
    assert response.status_code in codes


@pytest.mark.config(
    MODES=[
        {
            'mode': 'boats',
            'zone_activation': {
                'point_image_tag': 'custom_pp_icons_2_red',
                'point_title': 'boats.pickuppoint_name',
                'zone_type': 'boat',
            },
        },
    ],
)
async def test_geomagnet_config(
        taxi_persuggest, mockserver, yamaps, load_json,
):
    yamaps.add_fmt_geo_object(load_json('yamaps_response.json'))

    # pylint: disable=unused-variable
    @mockserver.json_handler('/special-zones/special-zones/v1/filter')
    def mock_zones(request):
        request_json = json.loads(request.get_data())
        assert request_json['excluded_zone_types'] == ['boat']
        return {'results': [{'in_zone': True}]}

    response = await taxi_persuggest.post(
        '/3.0/geomagnet', load_json('geomagnet_request.json'),
    )
    assert response.status_code == 404


async def test_bad_position(taxi_persuggest, load_json, mockserver):
    request = load_json('geomagnet_request.json')
    request['ll'] = [-181, 91]
    response = await taxi_persuggest.post('/3.0/geomagnet', request)
    assert response.status_code == 400
