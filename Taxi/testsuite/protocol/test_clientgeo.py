import pytest


def test_clientgeo_bad_request(taxi_protocol):
    response = taxi_protocol.post(
        '3.0/clientgeo', {'key': 'request_body_malformed'},
    )
    assert response.status_code == 400


def test_clientgeo_user_not_found(taxi_protocol):
    response = taxi_protocol.post(
        '3.0/clientgeo',
        {
            'id': 'non_existent_user_id',
            'geo_position': {
                'lon': 0,
                'lat': 0,
                'accuracy': 0,
                'retrieved_at': '2018-08-22T18:51:25+0300',
            },
        },
    )
    assert response.status_code == 404


def test_clientgeo_user_unauthorized(taxi_protocol):
    response = taxi_protocol.post(
        '3.0/clientgeo',
        {
            'id': '7c5cea02692a49a5b5e277e4582af45b',
            'geo_position': {
                'lon': 0,
                'lat': 0,
                'accuracy': 0,
                'retrieved_at': '2018-08-22T18:51:25+0300',
            },
        },
    )
    assert response.status_code == 401


def test_clientgeo_disabled(mockserver, taxi_protocol):

    response = taxi_protocol.post(
        '3.0/clientgeo',
        {
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'geo_position': {
                'lon': 0,
                'lat': 0,
                'accuracy': 0,
                'retrieved_at': '2018-08-22T18:51:25+0300',
            },
        },
    )
    assert response.status_code == 200
    assert response.json().get('enabled') is False


@pytest.mark.user_experiments('client_geo', 'client_geo_request')
@pytest.mark.config(EXPERIMENTS_ENABLED=True)
def test_clientgeo_enabled(mockserver, taxi_protocol):
    @mockserver.json_handler('/user-tracking/user/position/store')
    def position_store(request):
        return ''

    @mockserver.json_handler('/yagr/pipeline/go-users/position/store')
    def yagr_position_store(request):
        return ''

    response = taxi_protocol.post(
        '3.0/clientgeo',
        {
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'geo_position': {
                'lon': 0,
                'lat': 0,
                'accuracy': 0,
                'retrieved_at': '2018-08-22T18:51:25+0300',
            },
        },
    )
    assert response.status_code == 200
    assert response.json().get('enabled') is True

    assert yagr_position_store.times_called == 1
    assert position_store.times_called == 1


@pytest.mark.user_experiments('client_geo', 'client_geo_request')
@pytest.mark.config(EXPERIMENTS_ENABLED=True)
def test_clientgeo_expired_timestamp(mockserver, taxi_protocol):
    @mockserver.json_handler('/user-tracking/user/position/store')
    def position_store(request):
        return mockserver.make_response(status=400)

    @mockserver.json_handler('/yagr/pipeline/go-users/position/store')
    def yagr_position_store(request):
        return ''

    response = taxi_protocol.post(
        '3.0/clientgeo',
        {
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'geo_position': {
                'lon': 0,
                'lat': 0,
                'accuracy': 0,
                'retrieved_at': '2018-08-22T18:51:25+0300',
            },
        },
    )
    assert response.status_code == 200
    assert response.json().get('enabled') is True

    assert yagr_position_store.times_called == 1
    assert position_store.times_called == 1
