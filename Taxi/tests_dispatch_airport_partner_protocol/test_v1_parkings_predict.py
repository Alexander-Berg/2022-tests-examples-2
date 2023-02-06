from tests_dispatch_airport_partner_protocol import common


async def test_v1_parkings_predict(
        taxi_dispatch_airport_partner_protocol, mockserver, load_json,
):
    @mockserver.json_handler('/dispatch-airport/v1/partner_parkings/predict')
    def _partner_parkings_predict(request):
        parkings = [x['parking_id'] for x in request.json['parkings']]
        all_data = load_json('dispatch_airport_response.json')
        result = {
            'parking_predictions': [
                x for x in all_data['parkings'] if x['parking_id'] in parkings
            ],
        }
        return result

    response = await taxi_dispatch_airport_partner_protocol.post(
        '/1.0/parkings/predict',
        {
            'parkings': [
                {'parking_id': 'ekb_dl1_comfortplus'},
                {'parking_id': 'ekb_dl1_econom'},
                {'parking_id': 'ekb_all'},
            ],
        },
        headers=common.DEFAULT_DISPATCH_AIRPORT_PARTNER_PROTOCOL_HEADER,
    )
    assert response.status_code == 200
    etalon = load_json('dispatch_airport_response.json')['parkings']

    response_predictions = response.json()['parking_predictions']
    response_predictions.sort(key=lambda x: x['parking_id'])
    for parking in response_predictions:
        parking['predictions'].sort(key=lambda x: x['tariff'])

    assert etalon == response_predictions


async def test_negative(taxi_dispatch_airport_partner_protocol):
    resp = await taxi_dispatch_airport_partner_protocol.post(
        '/1.0/parkings/predict',
        {'parkings': [{'parking_id': 'ekb_all'}]},
        headers={'YaTaxi-Api-Key': 'not_existing_api_key'},
    )
    assert resp.status_code == 403
    assert resp.json()['code'] == 'INVALID_API_KEY'

    # bad request, no Api-Key header
    resp = await taxi_dispatch_airport_partner_protocol.post(
        '/1.0/parkings/predict',
        {'parkings': [{'parking_id': 'ekb_all'}]},
        headers={},
    )
    assert resp.status_code == 400

    # bad request, empty car_numbers
    resp = await taxi_dispatch_airport_partner_protocol.post(
        '/1.0/parkings/predict',
        {},
        headers=common.DEFAULT_DISPATCH_AIRPORT_PARTNER_PROTOCOL_HEADER,
    )
    assert resp.status_code == 400
    assert resp.json()['code'] == 'BAD_REQUEST'
