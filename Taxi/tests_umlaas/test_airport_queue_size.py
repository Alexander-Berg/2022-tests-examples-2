import datetime

import pytest


@pytest.mark.config(
    DISPATCH_AIRPORT_ML_SETTINGS={
        'vko': {
            'ml_visible_classes': [
                'econom',
                'business',
                'comfortplus',
                'vip',
                'ultimate',
                'minivan',
                'child_tariff',
                'maybach',
                'premium_van',
            ],
        },
        'yerevan_airport': {
            'ml_visible_classes': [
                'start',
                'standart',
                'vip',
                'minivan',
                'child_tariff',
                'comfortplus',
            ],
        },
    },
    UMLAAS_QUEUE_MODEL_CACHE_UPDATE_ENABLED=True,
    UMLAAS_AIRPORT_QUEUE_RESOURCES=[{'name': 'model', 'resource_name': '0'}],
)
@pytest.mark.experiments3(filename='umlaas_airport_queue_size_params.json')
async def test_static_predictor(taxi_umlaas, mocked_time):
    mocked_time.set(datetime.datetime(2020, 1, 1, 10, 00, 00))

    await taxi_umlaas.tests_control()

    params = {'airport': 'vko', 'tariff': 'econom', 'nearest_mins': 30}
    response = await taxi_umlaas.get('airport_queue_size/v1', params=params)
    assert response.status_code == 200
    assert 'queue_size' not in response.json()
    assert not response.json()['estimated_times']
