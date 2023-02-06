import pytest


@pytest.mark.config(GEOTRACKS_API_KEYS_ENABLED=True)
def test_api_keys_enable(taxi_geotracks, mockserver):
    @mockserver.handler('/s3mds/')
    def mock_user_list(request):
        return mockserver.make_response('', 200)

    arr = [
        'user/track?user_id=spider-man&last=10',
        'gps-storage/set?&db_id=0&driver_id=42&lat=55&lon=82&angel=0&speed=0',
        'gps-storage/get?&db_id=0&driver_id=42&last=10',
    ]

    for val in arr:
        response = taxi_geotracks.get(
            val, headers={'X-YaTaxi-API-Key': 'GEOTRACKS-VALID-API-KEY'},
        )
        assert response.status_code == 200
        response = taxi_geotracks.get(
            val, headers={'X-YaTaxi-API-Key': 'GEOTRACKS-INVALID-API-KEY'},
        )
        assert response.status_code == 401
        response = taxi_geotracks.get(val)
        assert response.status_code == 401


def test_api_keys_disable(taxi_geotracks, mockserver):
    @mockserver.handler('/s3mds/')
    def mock_user_list(request):
        return mockserver.make_response('', 200)

    arr = [
        'user/track?user_id=spider-man&last=10',
        'gps-storage/set?&db_id=0&driver_id=42&lat=55&lon=82&angel=0&speed=0',
        'gps-storage/get?&db_id=0&driver_id=42&last=10',
    ]

    for val in arr:
        response = taxi_geotracks.get(
            val, headers={'X-YaTaxi-API-Key': 'GEOTRACKS-VALID-API-KEY'},
        )
        assert response.status_code == 200
        response = taxi_geotracks.get(
            val, headers={'X-YaTaxi-API-Key': 'GEOTRACKS-INVALID-API-KEY'},
        )
        assert response.status_code == 401
        response = taxi_geotracks.get(val)
        assert response.status_code == 200
