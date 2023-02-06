import json

import pytest


CONFIG = dict(
    PROMO_STORIES=['story_1', 'story_2', 'story_3', 'story_4'],
    PROMO_STORIES_SETTINGS={
        'story_1': {'countries': ['country_1']},
        'story_2': {'countries': ['country_2']},
        'story_3': {'zones': ['zone_1']},
        'story_4': {'zones': ['zone_2']},
    },
)


def mock_bigb(mockserver, ticket, return_value=None, status_code=200):
    @mockserver.json_handler('/bigb')
    def route_bigb(request):
        assert 'X-Ya-Service-Ticket' in request.headers
        assert request.headers['X-Ya-Service-Ticket'] == ticket
        if status_code == 200:
            return return_value
        else:
            return mockserver.make_response(status=status_code)

    return route_bigb


@pytest.mark.config(**CONFIG)
def test_empty_request(tvm2_client, taxi_ml, load_json, mockserver):
    tvm2_client.set_ticket(json.dumps({'21': {'ticket': 'ticket'}}))
    mock_bigb(mockserver, 'ticket')
    response = taxi_ml.post('stories/v1', json={})
    assert response.status_code == 400


@pytest.mark.parametrize(
    'request_file',
    ['request_without_geography.json', 'request_without_geography_noid.json'],
)
@pytest.mark.config(**CONFIG)
def test_request_without_geography(
        tvm2_client, taxi_ml, load_json, mockserver, request_file,
):
    tvm2_client.set_ticket(json.dumps({'21': {'ticket': 'ticket'}}))
    route_bigb = mock_bigb(mockserver, 'ticket')
    request = load_json(request_file)
    response = taxi_ml.post('stories/v1?client_name=trip', json=request)
    assert response.status_code == 200
    story_ids = [obj['id'] for obj in response.json()['stories']]
    assert story_ids == ['story_1', 'story_2', 'story_3', 'story_4']
    route_bigb.wait_call()


@pytest.mark.parametrize(
    'request_file', ['request_full.json', 'request_full_noid.json'],
)
@pytest.mark.config(**CONFIG)
def test_request_full(
        tvm2_client, taxi_ml, load_json, mockserver, request_file,
):
    tvm2_client.set_ticket(json.dumps({'21': {'ticket': 'ticket'}}))
    route_bigb = mock_bigb(mockserver, 'ticket')
    request = load_json(request_file)
    response = taxi_ml.post('stories/v1?client_name=trip', json=request)
    assert response.status_code == 200
    story_ids = [obj['id'] for obj in response.json()['stories']]
    assert story_ids == ['story_2', 'story_4']
    route_bigb.wait_call()


@pytest.mark.config(**CONFIG)
def test_request_full_wrong_client_name(
        tvm2_client, taxi_ml, load_json, mockserver,
):
    tvm2_client.set_ticket(json.dumps({'21': {'ticket': 'ticket'}}))
    mock_bigb(mockserver, 'ticket')
    request = load_json('request_full.json')
    response = taxi_ml.post('stories/v1?client_name=trips', json=request)
    assert response.status_code == 400


@pytest.mark.config(**CONFIG)
def test_request_full_empty_client_name(
        tvm2_client, taxi_ml, load_json, mockserver,
):
    tvm2_client.set_ticket(json.dumps({'21': {'ticket': 'ticket'}}))
    mock_bigb(mockserver, 'ticket')
    request = load_json('request_full.json')
    response = taxi_ml.post('stories/v1', json=request)
    assert response.status_code == 400


@pytest.mark.config(**CONFIG)
def test_request_without_identity(tvm2_client, taxi_ml, load_json, mockserver):
    tvm2_client.set_ticket(json.dumps({'21': {'ticket': 'ticket'}}))
    mock_bigb(mockserver, 'ticket')
    request = load_json('request_without_identity.json')
    response = taxi_ml.post('stories/v1?client_name=trip', json=request)
    assert response.status_code == 400


@pytest.mark.parametrize(
    'request_file',
    ['request_without_order.json', 'request_without_order_noid.json'],
)
@pytest.mark.config(**CONFIG)
def test_request_without_order(
        tvm2_client, taxi_ml, load_json, mockserver, request_file,
):
    tvm2_client.set_ticket(json.dumps({'21': {'ticket': 'ticket'}}))
    route_bigb = mock_bigb(mockserver, 'ticket')
    request = load_json(request_file)
    response = taxi_ml.post('stories/v1?client_name=trip', json=request)
    assert response.status_code == 200
    story_ids = [obj['id'] for obj in response.json()['stories']]
    assert story_ids == ['story_2', 'story_4']
    route_bigb.wait_call()


@pytest.mark.parametrize(
    'request_file', ['request_full.json', 'request_full_noid.json'],
)
@pytest.mark.config(**CONFIG)
def test_time_format(
        tvm2_client, taxi_ml, load_json, mockserver, request_file,
):
    tvm2_client.set_ticket(json.dumps({'21': {'ticket': 'ticket'}}))
    mock_bigb(mockserver, 'ticket')
    request = load_json(request_file)
    request['time'] = '123'
    response = taxi_ml.post('stories/v1?client_name=trip', json=request)
    assert response.status_code == 400


@pytest.mark.parametrize(
    'request_file', ['request_full.json', 'request_full_noid.json'],
)
@pytest.mark.config(**CONFIG)
def test_bigb_503(tvm2_client, taxi_ml, load_json, mockserver, request_file):
    tvm2_client.set_ticket(json.dumps({'21': {'ticket': 'ticket'}}))
    route_bigb = mock_bigb(mockserver, 'ticket', status_code=503)

    request = load_json(request_file)
    response = taxi_ml.post('stories/v1?client_name=trip', json=request)
    assert response.status_code == 200
    story_ids = [obj['id'] for obj in response.json()['stories']]
    assert story_ids == ['story_2', 'story_4']
    route_bigb.wait_call()
