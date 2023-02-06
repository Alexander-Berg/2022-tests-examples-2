import json

import pytest


def test_experiments3_empty(taxi_experiments3, now):
    taxi_experiments3.tests_control(now=now, invalidate_caches=True)

    headers = {'YaTaxi-Api-Key': 'exp3_server_api_token'}
    response = _request(taxi_experiments3, {}, headers)
    assert response.status_code == 400


def test_experiments3_empty_with_consumer(taxi_experiments3, now):
    request = {'consumer': 'launch'}
    taxi_experiments3.tests_control(now=now, invalidate_caches=True)
    headers = {'YaTaxi-Api-Key': 'exp3_server_api_token'}
    response = _request(taxi_experiments3, request, headers)
    assert response.status_code == 400


def test_experiments3_empty_with_consumer_and_empty_args(
        taxi_experiments3, now,
):
    request = {'consumer': 'launch', 'args': []}
    taxi_experiments3.tests_control(now=now, invalidate_caches=True)

    headers = {'YaTaxi-Api-Key': 'exp3_server_api_token'}
    response = _request(taxi_experiments3, request, headers)
    assert response.status_code == 200
    content = response.json()
    assert content['items'] == []
    assert content['version'] == -1


@pytest.mark.experiments3(
    name='test1',
    consumers=['launch', 'client_protocol/launch'],
    match={
        'predicate': {'type': 'true'},
        'enabled': True,
        'applications': [
            {
                'name': 'android',
                'version_range': {'from': '0.0.0', 'to': '9.9.9'},
            },
        ],
    },
    clauses=[],
    default_value={'value': 9875},
)
def test_experiments3_exp_doesnt_match(taxi_experiments3, now):
    request = {
        'consumer': 'launch',
        'args': [
            {
                'name': 'version',
                'type': 'application_version',
                'value': '5.5.5',
            },
            {'name': 'application', 'type': 'application', 'value': 'iphone'},
        ],
    }

    taxi_experiments3.tests_control(now=now, invalidate_caches=True)
    headers = {'YaTaxi-Api-Key': 'exp3_server_api_token'}
    response = _request(taxi_experiments3, request, headers)
    assert response.status_code == 200
    content = response.json()
    assert content['version'] == 1
    assert content['items'] == []


@pytest.mark.experiments3(
    name='test1',
    consumers=['launch', 'client_protocol/launch'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={'value': 9875},
)
def test_experiments3_incorrect_consumer(taxi_experiments3, now):
    request = {
        'consumer': 'incorrect',
        'args': [
            {
                'name': 'version',
                'type': 'application_version',
                'value': '5.5.5',
            },
            {'name': 'application', 'type': 'application', 'value': 'iphone'},
        ],
    }

    taxi_experiments3.tests_control(now=now, invalidate_caches=True)
    headers = {'YaTaxi-Api-Key': 'exp3_server_api_token'}
    response = _request(taxi_experiments3, request, headers)
    assert response.status_code == 400


@pytest.mark.experiments3(
    name='test1',
    consumers=['launch', 'client_protocol/launch'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={'foo': 9875},
)
def test_experiments3_exp_match(taxi_experiments3, now):
    request = {
        'consumer': 'launch',
        'args': [
            {
                'name': 'version',
                'type': 'application_version',
                'value': '5.5.5',
            },
            {'name': 'application', 'type': 'application', 'value': 'android'},
        ],
    }

    taxi_experiments3.tests_control(now=now, invalidate_caches=True)
    headers = {'YaTaxi-Api-Key': 'exp3_server_api_token'}
    response = _request(taxi_experiments3, request, headers)
    assert response.status_code == 200
    content = response.json()
    assert len(content['items']) == 1
    assert content['items'][0]['value']['foo'] == 9875


@pytest.mark.config(
    # TVM_ENABLED=True, # TODO doesn't pass in develop
    TVM_RULES=[{'src': 'driver_protocol', 'dst': 'experiments3'}],
)
@pytest.mark.experiments3(
    name='test1',
    consumers=['launch', 'client_protocol/launch'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={'foo': 9875},
)
def test_experiments3_exp_match_tvm(taxi_experiments3, now, load):
    request = {
        'consumer': 'launch',
        'args': [
            {
                'name': 'version',
                'type': 'application_version',
                'value': '5.5.5',
            },
            {'name': 'application', 'type': 'application', 'value': 'android'},
        ],
    }

    headers = {'X-Ya-Service-Ticket': load('tvm2_ticket_19_30')}
    taxi_experiments3.tests_control(now=now, invalidate_caches=True)

    response = _request(taxi_experiments3, request, headers)
    assert response.status_code == 200
    content = response.json()
    assert len(content['items']) == 1
    assert content['items'][0]['value']['foo'] == 9875


@pytest.mark.experiments3(filename='exp_match.json')
def test_experiments3_exp_match_with_string(taxi_experiments3, now):
    request = {
        'consumer': 'launch',
        'args': [
            {
                'name': 'version',
                'type': 'application_version',
                'value': '5.5.5',
            },
            {'name': 'application', 'type': 'application', 'value': 'android'},
            {'name': 'key', 'type': 'string', 'value': 'super-key'},
        ],
    }

    taxi_experiments3.tests_control(now=now, invalidate_caches=True)
    headers = {'YaTaxi-Api-Key': 'exp3_server_api_token'}
    response = _request(taxi_experiments3, request, headers)
    assert response.status_code == 200
    content = response.json()
    assert content['version'] == 1
    assert len(content['items']) == 1
    assert content['items'][0]['value'] == 9875


@pytest.mark.experiments3(filename='exp_match.json')
def test_experiments3_exp_match_with_geopoint(taxi_experiments3, now):
    request = {
        'consumer': 'launch',
        'args': [
            {
                'name': 'version',
                'type': 'application_version',
                'value': '5.5.5',
            },
            {'name': 'application', 'type': 'application', 'value': 'android'},
            {
                'name': 'point_a',
                'type': 'point',
                'value': [37.04910393749999, 55.864550814117806],
            },
        ],
    }

    taxi_experiments3.tests_control(now=now, invalidate_caches=True)
    headers = {'YaTaxi-Api-Key': 'exp3_server_api_token'}
    response = _request(taxi_experiments3, request, headers)
    assert response.status_code == 200
    content = response.json()
    assert content['version'] == 1
    assert len(content['items']) == 1
    assert content['items'][0]['value'] == 98754


@pytest.mark.experiments3(filename='exp_match.json')
def test_experiments3_exp_match_with_timepoint(taxi_experiments3, now):
    request = {
        'consumer': 'launch',
        'args': [
            {
                'name': 'version',
                'type': 'application_version',
                'value': '5.5.5',
            },
            {'name': 'application', 'type': 'application', 'value': 'android'},
            {
                'name': 'created',
                'type': 'timepoint',
                'value': '2020-02-20T20:20:20+03:00',
            },
        ],
    }

    taxi_experiments3.tests_control(now=now, invalidate_caches=True)
    headers = {'YaTaxi-Api-Key': 'exp3_server_api_token'}
    response = _request(taxi_experiments3, request, headers)
    assert response.status_code == 200
    content = response.json()
    assert content['version'] == 1
    assert len(content['items']) == 1
    assert content['items'][0]['value'] == 987543


@pytest.mark.config(
    EXPERIMENTS3_EXP3_MATCHER_COMPARE_PERCENTS=100,
    TVM_RULES=[{'experiments3': 'exp3-matcher'}],
)
@pytest.mark.experiments3(filename='exp_match.json')
def test_experiments3_exp3_matcher_compare(taxi_experiments3, now, mockserver):
    request = {
        'consumer': 'launch',
        'args': [
            {
                'name': 'version',
                'type': 'application_version',
                'value': '5.5.5',
            },
            {'name': 'application', 'type': 'application', 'value': 'android'},
            {
                'name': 'created',
                'type': 'timepoint',
                'value': '2020-02-20T20:20:20+03:00',
            },
        ],
    }

    @mockserver.json_handler('/exp3-matcher/v1/experiments/')
    def _mock_exp3_matcher(_request):
        assert json.loads(_request.get_data()) == request
        return {'items': [{'name': 'test1', 'value': 987543}], 'version': 1}

    taxi_experiments3.tests_control(now=now, invalidate_caches=True)
    headers = {'YaTaxi-Api-Key': 'exp3_server_api_token'}

    response = _request(taxi_experiments3, request, headers)
    assert response.status_code == 200

    _mock_exp3_matcher.wait_call()

    content = response.json()
    assert content['version'] == 1
    assert len(content['items']) == 1
    assert content['items'][0]['value'] == 987543


def _request(taxi_experiments3, data, headers):
    response = taxi_experiments3.post('/v1/experiments', data, headers=headers)
    return response
