import pytest

from tests_dispatch_airport import common


@pytest.mark.config(
    DISPATCH_AIRPORT_PARTNER_PARKING_QUOTAS={
        'ekb_dl1_comfortplus': {
            'predict_airport_id': 'ekb',
            'capacities': {'comfortplus': 1000},
        },
        'ekb_dl1_econom': {
            'predict_airport_id': 'ekb',
            'capacities': {'econom': 4},
        },
        'ekb_all': {
            'predict_airport_id': 'ekb',
            'capacities': {'econom': 3, 'comfortplus': 2, 'ultima': 5},
        },
    },
)
@pytest.mark.experiments3(
    filename='experiments3_umlaas_queue_predictions.json',
)
async def test_v1_needs(taxi_dispatch_airport, mockserver):
    @mockserver.json_handler('/umlaas/airport_queue_size/v1')
    def _umlaas(request):
        response = {'estimated_times': [], 'queue_size': 5}
        return response

    response = await taxi_dispatch_airport.post(
        '/v1/partner_parkings/predict',
        {
            'parkings': [
                {'parking_id': 'ekb_dl1_comfortplus'},
                {'parking_id': 'ekb_dl1_econom'},
                {'parking_id': 'ekb_all'},
            ],
        },
        headers=common.DEFAULT_DISPATCH_AIRPORT_HEADER,
    )
    assert response.status_code == 200
    etalon = [
        {
            'parking_id': 'ekb_all',
            'predictions': [
                {'tariff': 'comfortplus', 'prediction': 2},
                {'tariff': 'econom', 'prediction': 3},
                {'tariff': 'ultima', 'prediction': 0},
            ],
        },
        {
            'parking_id': 'ekb_dl1_comfortplus',
            'predictions': [{'tariff': 'comfortplus', 'prediction': 5}],
        },
        {
            'parking_id': 'ekb_dl1_econom',
            'predictions': [{'tariff': 'econom', 'prediction': 4}],
        },
    ]

    resonse_predictions = response.json()['parking_predictions']
    resonse_predictions.sort(key=lambda x: x['parking_id'])
    for parking in resonse_predictions:
        parking['predictions'].sort(key=lambda x: x['tariff'])

    assert etalon == resonse_predictions
