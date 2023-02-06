import pytest


@pytest.fixture(autouse=True)
def classifier_request_override(mockserver):
    @mockserver.json_handler('/classifier/v1/classifier-tariffs/updates')
    def _mock_tariffs_updates(request):
        response = {
            'cursor': {'id': 5},
            'limit': 100,
            'tariffs': [
                {
                    'classifier_id': 'Москва',
                    'is_allowing': True,
                    'tariff_id': 'econom',
                },
                {
                    'classifier_id': 'Москва',
                    'is_allowing': False,
                    'tariff_id': 'exception1',
                },
                {
                    'classifier_id': 'Москва',
                    'is_allowing': False,
                    'tariff_id': 'exception2',
                },
                {
                    'classifier_id': 'Москва',
                    'is_allowing': False,
                    'tariff_id': 'exception3',
                },
                {
                    'classifier_id': 'Москва',
                    'is_allowing': False,
                    'tariff_id': 'exception4',
                },
            ],
        }
        return response

    @mockserver.json_handler('/classifier/v1/classification-rules/updates')
    def _mock_classification_rules_updates(request):
        response = {
            'classification_rules': [
                {
                    'classifier_id': 'Москва',
                    'is_allowing': False,
                    'price_from': 0,
                    'price_to': 99999,
                    'tariff_id': 'econom',
                    'year_from': 2010,
                    'year_to': 2020,
                },
                {
                    'classifier_id': 'Москва',
                    'is_allowing': False,
                    'tariff_id': 'econom',
                    'year_to': 2009,
                },
            ],
            'limit': 100,
        }
        return response

    @mockserver.json_handler('/classifier/v2/classifier-exceptions/updates')
    def _mock_classifier_exceptions_updates_v2(request):
        return {
            'classifier_exceptions_V2': [
                {
                    'id': '123',
                    'car_number': 'Х495НК77',
                    'tariffs': ['exception1', 'exception4'],
                    'zones': [],
                    'updated_at': '2019-12-23T00:00:00+00:00',
                    'is_deleted': False,
                },
                {
                    'id': '124',
                    'car_number': 'Х495НК77',
                    'tariffs': ['exception3'],
                    'zones': ['moscow'],
                    'updated_at': '2019-12-24T00:00:00+00:00',
                    'is_deleted': False,
                },
                {
                    'id': '125',
                    'car_number': 'Х495НК77',
                    'tariffs': ['exception2'],
                    'started_at': '2019-12-25T00:00:00+00:00',
                    'ended_at': '2019-12-12T00:00:00+00:00',
                    'zones': [],
                    'updated_at': '2019-12-25T00:00:00+00:00',
                    'is_deleted': False,
                },
            ],
            'limit': 100,
        }


@pytest.mark.now('2019-12-27T00:00:00+00:00')
async def test_classifier_exceptions(taxi_candidates):
    # fill caches from custom mock handlers
    # defined in this test
    await taxi_candidates.invalidate_caches()

    request_body = {
        'driver_ids': ['dbid0_uuid1'],
        'data_keys': ['car_classes'],
        'allowed_classes': [
            'exception1',
            'exception2',
            'exception3',
            'exception4',
        ],
        'zone_id': 'moscow',
    }
    response = await taxi_candidates.post('profiles', json=request_body)
    assert response.status_code == 200
    assert 'drivers' in response.json()
    drivers = response.json()['drivers']
    assert len(drivers) == 1
    classes = drivers[0]['car_classes']
    assert sorted(classes) == sorted(
        ['exception1', 'exception4', 'exception3'],
    )

    request_body['zone_id'] = 'spb'
    response = await taxi_candidates.post('profiles', json=request_body)
    assert response.status_code == 200
    assert 'drivers' in response.json()
    drivers = response.json()['drivers']
    assert len(drivers) == 1
    classes = drivers[0]['car_classes']
    assert sorted(classes) == sorted(['exception1', 'exception4'])
