import copy
import json

import pytest

import tests_driver_eta.dispatch_settings as dispatch_settings
import v2_stubs


URL = '/driver-eta/v2/eta'

MOSCOW_AIRPORT_POINT = [26, 16]


def _umlaas_dispatch_classes_info_as_dict(classes_info):
    result = {}
    for class_info in classes_info:
        class_info_dict = copy.deepcopy(class_info)
        if 'candidates' in class_info:
            class_info_dict['candidates'] = {}
            for candidate in class_info['candidates']:
                class_info_dict['candidates'][candidate['uuid']] = candidate
        result[class_info['tariff_class']] = class_info_dict

    return result


def _candidates_remove_classes(request, classes):
    for class_name in classes:
        request['allowed_classes'].remove(class_name)
        request['search_settings'].pop(class_name)


@pytest.mark.dispatch_settings(settings=dispatch_settings.DISPATCH_SETTINGS)
async def test_eta(taxi_driver_eta, mockserver, taxi_config):
    @mockserver.json_handler('/candidates/order-multisearch')
    def _search(request):
        body = json.loads(request.get_data())
        assert body == v2_stubs.CANDIDATES_REQUEST

        return mockserver.make_response(
            json=v2_stubs.CANDIDATES_RESPONSE, status=200,
        )

    @mockserver.json_handler('/driver_scoring/v2/score-candidates-bulk')
    def _scoring(request):
        body = json.loads(request.get_data())
        assert body == v2_stubs.LOOKUP_ORDERING_REQUEST
        return mockserver.make_response(
            json=v2_stubs.LOOKUP_ORDERING_RESPONSE, status=200,
        )

    @mockserver.json_handler(
        '/umlaas-dispatch/umlaas-dispatch/v1/search-radius-prediction',
    )
    def _umlaas_dispatch(request):
        body = json.loads(request.get_data())
        assert body == v2_stubs.UMLAAS_DISPATCH_REQUEST
        return mockserver.make_response(
            json=v2_stubs.UMLAAS_DISPATCH_RESPONSE, status=200,
        )

    response = await taxi_driver_eta.post(
        URL,
        headers={'X-YaTaxi-PhoneId': 'phone_id_0'},
        json=v2_stubs.DRIVER_ETA_REQUEST,
    )
    assert response.status_code == 200
    answer = response.json()
    assert answer == v2_stubs.DRIVER_ETA_RESPONSE
    assert _scoring.has_calls


@pytest.mark.dispatch_settings(settings=dispatch_settings.DISPATCH_SETTINGS)
async def test_no_candidates_eta(taxi_driver_eta, mockserver, taxi_config):
    @mockserver.json_handler('/candidates/order-multisearch')
    def _search(request):
        body = json.loads(request.get_data())
        assert body == v2_stubs.CANDIDATES_REQUEST

        return mockserver.make_response(status=500)

    @mockserver.json_handler('/driver_scoring/v2/score-candidates-bulk')
    def _scoring(request):
        body = json.loads(request.get_data())
        assert body == v2_stubs.LOOKUP_ORDERING_REQUEST
        return mockserver.make_response(
            json=v2_stubs.LOOKUP_ORDERING_RESPONSE, status=200,
        )

    @mockserver.json_handler(
        '/umlaas-dispatch/umlaas-dispatch/v1/search-radius-prediction',
    )
    def _umlaas_dispatch(request):
        body = json.loads(request.get_data())
        assert body == v2_stubs.UMLAAS_DISPATCH_EMPTY_REQUEST
        return mockserver.make_response(
            json=v2_stubs.UMLAAS_DISPATCH_EMPTY_RESPONSE, status=200,
        )

    response = await taxi_driver_eta.post(
        URL,
        headers={'X-YaTaxi-PhoneId': 'phone_id_0'},
        json=v2_stubs.DRIVER_ETA_REQUEST,
    )
    assert response.status_code == 200
    answer = response.json()
    assert answer == v2_stubs.DRIVER_ETA_EMPTY_RESPONSE
    assert not _scoring.has_calls


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='driver_eta_parallel_candidates',
    consumers=['driver-eta'],
    clauses=[
        {
            'title': 'title',
            'value': {
                'enabled': True,
                'split_by_tariffs': [
                    ['cargo', 'business'],
                    ['vip', 'econom', 'express'],
                ],
            },
            'predicate': {
                'type': 'in_set',
                'init': {
                    'set': ['phone_id_0'],
                    'arg_name': 'phone_id',
                    'set_elem_type': 'string',
                },
            },
        },
    ],
    default_value={'enabled': False, 'split_by_tariffs': []},
    is_config=True,
)
@pytest.mark.dispatch_settings(settings=dispatch_settings.DISPATCH_SETTINGS)
async def test_eta_parallel_by_exp(taxi_driver_eta, mockserver):

    candidates_times_called = 0
    lookup_ordering_times_called = 0

    @mockserver.json_handler('/candidates/order-multisearch')
    def _search(request):
        nonlocal candidates_times_called
        candidates_times_called += 1
        body = json.loads(request.get_data())

        request1 = copy.deepcopy(v2_stubs.CANDIDATES_REQUEST)
        request2 = copy.deepcopy(v2_stubs.CANDIDATES_REQUEST)

        _candidates_remove_classes(request1, ['comfort'])
        _candidates_remove_classes(request2, ['econom', 'vip', 'express'])

        assert body in (request1, request2)

        if body == request1:
            response = copy.deepcopy(v2_stubs.CANDIDATES_RESPONSE)
            del response['search_details']['comfort']
            return mockserver.make_response(json=response, status=200)

        return mockserver.make_response(status=500)

    @mockserver.json_handler('/driver_scoring/v2/score-candidates-bulk')
    def _scoring(request):
        nonlocal lookup_ordering_times_called
        lookup_ordering_times_called += 1
        body = json.loads(request.get_data())
        request1 = copy.deepcopy(v2_stubs.LOOKUP_ORDERING_REQUEST)
        request2 = copy.deepcopy(v2_stubs.LOOKUP_ORDERING_REQUEST)
        request1['requests'].pop(0)

        request2['requests'].pop(2)
        request2['requests'].pop(1)
        assert body in (request1, request2)

        response1 = copy.deepcopy(v2_stubs.LOOKUP_ORDERING_RESPONSE)
        response1['responses'].pop(0)
        response2 = copy.deepcopy(v2_stubs.LOOKUP_ORDERING_RESPONSE)
        response2['responses'].pop(2)
        response2['responses'].pop(1)
        if body == request1:
            return mockserver.make_response(json=response1, status=200)

        return mockserver.make_response(json=response2, status=200)

    @mockserver.json_handler(
        '/umlaas-dispatch/umlaas-dispatch/v1/search-radius-prediction',
    )
    def _umlaas_dispatch(request):
        body = json.loads(request.get_data())
        expected_req = copy.deepcopy(v2_stubs.UMLAAS_DISPATCH_REQUEST)
        body['classes_info'] = _umlaas_dispatch_classes_info_as_dict(
            body['classes_info'],
        )
        expected_req['classes_info'] = _umlaas_dispatch_classes_info_as_dict(
            expected_req['classes_info'],
        )
        # no response from candidates, so empty request incoming
        expected_req['classes_info']['comfort'] = {
            'free_time': 0,
            'free_distance': 0,
            'no_data_from_candidates': True,
            'tariff_class': 'comfort',
        }
        assert body == expected_req
        return mockserver.make_response(
            json=v2_stubs.UMLAAS_DISPATCH_RESPONSE, status=200,
        )

    response = await taxi_driver_eta.post(
        URL,
        headers={'X-YaTaxi-PhoneId': 'phone_id_0'},
        json=v2_stubs.DRIVER_ETA_REQUEST,
    )
    assert response.status_code == 200
    answer = response.json()
    expected_answer = copy.deepcopy(v2_stubs.DRIVER_ETA_RESPONSE)
    expected_answer['classes']['comfort'] = {
        'found': False,
        'no_cars_order_enabled': True,
        'paid_supply_enabled': False,
        'order_allowed': True,
        'no_data': True,
    }

    assert answer == expected_answer
    # taking retries into account (3 + 1 calls)
    assert candidates_times_called == 4
    # after candidates failed to response lookup called once
    assert lookup_ordering_times_called == 1


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='driver_eta_parallel_candidates',
    consumers=['driver-eta'],
    clauses=[
        {
            'title': 'title',
            'value': {
                'enabled': True,
                'split_by_tariffs': [['cargo', 'business'], ['vip']],
            },
            'predicate': {
                'type': 'in_set',
                'init': {
                    'set': ['phone_id_0'],
                    'arg_name': 'phone_id',
                    'set_elem_type': 'string',
                },
            },
        },
    ],
    default_value={'enabled': False, 'split_by_tariffs': []},
    is_config=True,
)
@pytest.mark.dispatch_settings(settings=dispatch_settings.DISPATCH_SETTINGS)
async def test_eta_parallel_by_requirements(taxi_driver_eta, mockserver):

    requirements = {'req1': True, 'req2': 42}
    candidates_times_called = 0
    lookup_ordering_times_called = 0

    @mockserver.json_handler('/candidates/order-multisearch')
    def _search(request):
        nonlocal candidates_times_called
        candidates_times_called += 1
        body = json.loads(request.get_data())

        request1 = copy.deepcopy(v2_stubs.CANDIDATES_REQUEST)
        request2 = copy.deepcopy(v2_stubs.CANDIDATES_REQUEST)
        request3 = copy.deepcopy(v2_stubs.CANDIDATES_REQUEST)

        # comfort
        _candidates_remove_classes(request1, ['vip', 'econom', 'express'])

        # econom, express
        _candidates_remove_classes(request2, ['comfort', 'vip'])

        # comfort
        _candidates_remove_classes(request3, ['comfort', 'econom', 'express'])

        request2['requirements'] = requirements
        request3['requirements'] = requirements

        if 'comfort' in body['allowed_classes']:
            assert body == request1

        if 'econom' in body['allowed_classes']:
            assert body == request2

        if 'vip' in body['allowed_classes']:
            assert body == request3

        assert body in (request1, request2, request3)
        return mockserver.make_response(
            json=v2_stubs.CANDIDATES_RESPONSE, status=200,
        )

    @mockserver.json_handler('/driver_scoring/v2/score-candidates-bulk')
    def _scoring(request):
        nonlocal lookup_ordering_times_called
        lookup_ordering_times_called += 1

        body = json.loads(request.get_data())
        request1 = copy.deepcopy(v2_stubs.LOOKUP_ORDERING_REQUEST)
        request2 = copy.deepcopy(v2_stubs.LOOKUP_ORDERING_REQUEST)
        request3 = copy.deepcopy(v2_stubs.LOOKUP_ORDERING_REQUEST)

        request1['requests'] = [request1['requests'][0]]
        request2['requests'] = [request2['requests'][1]]
        request3['requests'] = [request3['requests'][2]]

        request2['requests'][0]['search']['requirements'] = requirements
        request3['requests'][0]['search']['requirements'] = requirements

        allowed_classes = body['requests'][0]['search']['allowed_classes']
        if allowed_classes == ['comfort']:
            assert body == request1

        if allowed_classes == ['econom']:
            assert body == request2

        if allowed_classes == ['vip']:
            assert body == request3

        assert body in (request1, request2, request3)

        response1 = copy.deepcopy(v2_stubs.LOOKUP_ORDERING_RESPONSE)
        response1['responses'] = [response1['responses'][0]]

        response2 = copy.deepcopy(v2_stubs.LOOKUP_ORDERING_RESPONSE)
        response2['responses'] = [response2['responses'][1]]

        response3 = copy.deepcopy(v2_stubs.LOOKUP_ORDERING_RESPONSE)
        response3['responses'] = [response3['responses'][2]]

        if body == request1:
            return mockserver.make_response(json=response1, status=200)
        if body == request2:
            return mockserver.make_response(json=response2, status=200)
        return mockserver.make_response(json=response3, status=200)

    @mockserver.json_handler(
        '/umlaas-dispatch/umlaas-dispatch/v1/search-radius-prediction',
    )
    def _umlaas_dispatch(request):
        body = json.loads(request.get_data())
        expected_req = copy.deepcopy(v2_stubs.UMLAAS_DISPATCH_REQUEST)
        body['classes_info'] = _umlaas_dispatch_classes_info_as_dict(
            body['classes_info'],
        )
        expected_req['classes_info'] = _umlaas_dispatch_classes_info_as_dict(
            expected_req['classes_info'],
        )
        expected_req['classes_info']['econom']['requirements'] = requirements
        expected_req['classes_info']['vip']['requirements'] = requirements
        expected_req['classes_info']['express']['requirements'] = requirements
        assert body == expected_req
        return mockserver.make_response(
            json=v2_stubs.UMLAAS_DISPATCH_RESPONSE, status=200,
        )

    request_with_requirements = {
        **v2_stubs.DRIVER_ETA_REQUEST,
        'requirements_by_classes': [
            {
                'classes': ['econom', 'vip', 'express'],
                'requirements': requirements,
            },
        ],
    }

    response = await taxi_driver_eta.post(
        URL,
        headers={'X-YaTaxi-PhoneId': 'phone_id_0'},
        json=request_with_requirements,
    )
    assert response.status_code == 200
    answer = response.json()
    assert answer == v2_stubs.DRIVER_ETA_RESPONSE
    assert candidates_times_called == 3
    assert lookup_ordering_times_called == 3


@pytest.mark.parametrize(
    ['verdict', 'expected_value'],
    [
        pytest.param(
            'no_cars_order_enabled',
            True,
            marks=(
                pytest.mark.experiments3(
                    filename='own_chair_no_cars_order_exp3.json',
                )
            ),
        ),
        pytest.param(
            'order_allowed',
            False,
            marks=(
                pytest.mark.experiments3(
                    filename='own_chair_order_disallowed_exp3.json',
                )
            ),
        ),
        pytest.param(
            'paid_supply_enabled',
            True,
            marks=(
                pytest.mark.experiments3(
                    filename='own_chair_paid_supply_exp3.json',
                )
            ),
        ),
    ],
)
async def test_own_chair_requirement(
        taxi_driver_eta,
        mockserver,
        load_json,
        verdict,
        expected_value,
        taxi_config,
):
    @mockserver.json_handler('/candidates/order-multisearch')
    def _search(request):
        return mockserver.make_response(
            json=load_json('candidates_response.json'), status=200,
        )

    @mockserver.json_handler('/driver_scoring/v2/score-candidates-bulk')
    def _scoring(request):
        return mockserver.make_response(
            json={
                'responses': [
                    {
                        'candidates': [{'id': 'dbid2_uuid2', 'score': 1}],
                        'search': {},
                    },
                ],
            },
            status=200,
        )

    @mockserver.json_handler(
        '/umlaas-dispatch/umlaas-dispatch/v1/search-radius-prediction',
    )
    def _umlaas_dispatch(request):
        umlaas_dispatch_response = copy.deepcopy(
            v2_stubs.UMLAAS_DISPATCH_RESPONSE,
        )
        for verdict_dict in umlaas_dispatch_response['verdicts']:
            if verdict == 'paid_supply_enabled' and expected_value:
                verdict_dict.update({'estimate_distance': 1999})
                verdict_dict.update({'estimate_time': 199})
            else:
                verdict_dict.update({'estimate_distance': 999})
                verdict_dict.update({'estimate_time': 99})
        return mockserver.make_response(
            json=umlaas_dispatch_response, status=200,
        )

    request_with_requirements = {
        **v2_stubs.DRIVER_ETA_REQUEST,
        'requirements_by_classes': [
            {
                'classes': ['econom', 'vip', 'express'],
                'requirements': {'own_chair_v2': True},
            },
        ],
    }

    response = await taxi_driver_eta.post(
        URL,
        headers={'X-YaTaxi-PhoneId': 'phone_id_0'},
        json=request_with_requirements,
    )
    assert response.status_code == 200
    answer = response.json()
    assert answer['classes']['vip'][verdict] == expected_value
    assert answer['classes']['express'][verdict] == expected_value


@pytest.mark.parametrize(
    ['is_order_allowed'],
    [
        pytest.param(
            True,
            marks=(
                pytest.mark.experiments3(
                    filename='working_radius_disabled_exp3.json',
                )
            ),
        ),
        pytest.param(
            False,
            marks=(
                pytest.mark.experiments3(
                    filename='working_radius_small_time_radius_exp3.json',
                )
            ),
        ),
        pytest.param(
            False,
            marks=(
                pytest.mark.experiments3(
                    filename='working_radius_small_distance_radius_exp3.json',
                )
            ),
        ),
        pytest.param(
            True,
            marks=(
                pytest.mark.experiments3(
                    filename='working_radius_large_exp3.json',
                )
            ),
        ),
    ],
)
async def test_working_radius(
        taxi_driver_eta, mockserver, load_json, is_order_allowed, taxi_config,
):
    @mockserver.json_handler('/candidates/order-multisearch')
    def _search(request):
        return mockserver.make_response(
            json=load_json('candidates_response.json'), status=200,
        )

    @mockserver.json_handler('/driver_scoring/v2/score-candidates-bulk')
    def _scoring(request):
        return mockserver.make_response(
            json={
                'responses': [
                    {
                        'candidates': [{'id': 'dbid2_uuid2', 'score': 1}],
                        'search': {},
                    },
                ],
            },
            status=200,
        )

    @mockserver.json_handler(
        '/umlaas-dispatch/umlaas-dispatch/v1/search-radius-prediction',
    )
    def _umlaas_dispatch(request):
        umlaas_response = copy.deepcopy(v2_stubs.UMLAAS_DISPATCH_RESPONSE)
        for verdict_dict in umlaas_response['verdicts']:
            verdict_dict.update({'estimate_distance': 100})
            verdict_dict.update({'estimate_time': 20})
        return mockserver.make_response(json=umlaas_response, status=200)

    request_with_requirements = {
        **v2_stubs.DRIVER_ETA_REQUEST,
        'requirements_by_classes': [
            {
                'classes': ['econom', 'vip', 'express'],
                'requirements': {'own_chair_v2': True},
            },
        ],
    }

    response = await taxi_driver_eta.post(
        URL,
        headers={'X-YaTaxi-PhoneId': 'phone_id_0'},
        json=request_with_requirements,
    )
    assert response.status_code == 200
    answer = response.json()
    assert answer['classes']['econom']['order_allowed'] == is_order_allowed
    assert not answer['classes']['comfort']['order_allowed']


@pytest.mark.parametrize(
    ['requirements'],
    [
        pytest.param(
            {
                'request': [
                    {
                        'classes': ['vip', 'express', 'comfort'],
                        'requirements': {'simple_requirement': True},
                    },
                    {
                        'classes': ['econom'],
                        'requirements': {'simple_requirement': True},
                    },
                ],
                'merge': [
                    {
                        'allowed_classes': [
                            'comfort',
                            'econom',
                            'express',
                            'vip',
                        ],
                        'requirements': {'simple_requirement': True},
                    },
                ],
            },
        ),
        pytest.param(
            {
                'request': [
                    {
                        'classes': ['vip', 'express', 'comfort'],
                        'requirements': {},
                    },
                    {'classes': ['econom'], 'requirements': {}},
                ],
                'merge': [
                    {
                        'allowed_classes': [
                            'comfort',
                            'econom',
                            'express',
                            'vip',
                        ],
                        'requirements': {},
                    },
                ],
            },
        ),
        pytest.param(
            {
                'request': [
                    {
                        'classes': ['vip', 'express', 'comfort'],
                        'requirements': {
                            'int_value': 1,
                            'bool_value': True,
                            'same_array': [1, 2, 3],
                        },
                    },
                    {
                        'classes': ['econom'],
                        'requirements': {
                            'int_value': 1,
                            'bool_value': True,
                            'same_array': [1, 2, 3],
                        },
                    },
                ],
                'merge': [
                    {
                        'allowed_classes': [
                            'comfort',
                            'econom',
                            'express',
                            'vip',
                        ],
                        'requirements': {
                            'int_value': 1,
                            'bool_value': True,
                            'same_array': [1, 2, 3],
                        },
                    },
                ],
            },
        ),
        pytest.param(
            {
                'request': [
                    {
                        'classes': ['vip', 'express', 'comfort'],
                        'requirements': {
                            'int_value': 1,
                            'bool_value': True,
                            'different_array': [1, 2, 3],
                        },
                    },
                    {
                        'classes': ['econom'],
                        'requirements': {
                            'int_value': 1,
                            'bool_value': True,
                            'different_array': [1, 3, 2],
                        },
                    },
                ],
                'merge': [
                    {
                        'allowed_classes': ['comfort', 'express', 'vip'],
                        'requirements': {
                            'int_value': 1,
                            'bool_value': True,
                            'different_array': [1, 2, 3],
                        },
                    },
                    {
                        'allowed_classes': ['econom'],
                        'requirements': {
                            'int_value': 1,
                            'bool_value': True,
                            'different_array': [1, 3, 2],
                        },
                    },
                ],
            },
        ),
        pytest.param(
            {
                'request': [
                    {
                        'classes': ['vip', 'express', 'comfort'],
                        'requirements': {
                            'bad_type': 'string',
                            'bool_value': True,
                        },
                    },
                    {
                        'classes': ['econom'],
                        'requirements': {
                            'bad_type': 'string',
                            'bool_value': True,
                        },
                    },
                ],
                'merge': [
                    {
                        'allowed_classes': ['comfort', 'express', 'vip'],
                        'requirements': {
                            'bad_type': 'string',
                            'bool_value': True,
                        },
                    },
                    {
                        'allowed_classes': ['econom'],
                        'requirements': {
                            'bad_type': 'string',
                            'bool_value': True,
                        },
                    },
                ],
            },
        ),
    ],
)
async def test_merge_requirements_by_classes(
        taxi_driver_eta, mockserver, load_json, requirements,
):
    @mockserver.json_handler('/candidates/order-multisearch')
    def _search(request):
        body = json.loads(request.get_data())

        classes_found = False
        for merge_requirements in requirements['merge']:
            if (
                    body['allowed_classes']
                    == merge_requirements['allowed_classes']
            ):
                assert (
                    body['requirements'] == merge_requirements['requirements']
                )
                classes_found = True

        assert classes_found

        return mockserver.make_response(
            json=load_json('candidates_response.json'), status=200,
        )

    @mockserver.json_handler('/driver_scoring/v2/score-candidates-bulk')
    def _scoring(request):
        return mockserver.make_response(status=200)

    @mockserver.json_handler(
        '/umlaas-dispatch/umlaas-dispatch/v1/search-radius-prediction',
    )
    def _umlaas_dispatch(request):
        umlaas_response = copy.deepcopy(v2_stubs.UMLAAS_DISPATCH_RESPONSE)
        return mockserver.make_response(json=umlaas_response, status=200)

    request_with_requirements = {
        **v2_stubs.DRIVER_ETA_REQUEST,
        'requirements_by_classes': requirements['request'],
    }

    response = await taxi_driver_eta.post(
        URL,
        headers={'X-YaTaxi-PhoneId': 'phone_id_0'},
        json=request_with_requirements,
    )
    assert response.status_code == 200


@pytest.mark.parametrize(
    ['intent', 'enabled_ml'],
    [
        pytest.param('eta', True),
        pytest.param('eta-autoreorder', False),
        pytest.param('other', True),
    ],
)
@pytest.mark.experiments3(
    filename='driver_eta_intent_based_settings_exp3.json',
)
async def test_intent_based_settings_disable_ml(
        taxi_driver_eta, mockserver, load_json, intent, enabled_ml,
):
    @mockserver.json_handler('/candidates/order-multisearch')
    def _search(request):
        body = json.loads(request.get_data())
        assert body == v2_stubs.CANDIDATES_REQUEST

        return mockserver.make_response(
            json=v2_stubs.CANDIDATES_RESPONSE, status=200,
        )

    @mockserver.json_handler('/driver_scoring/v2/score-candidates-bulk')
    def _scoring(_):
        return mockserver.make_response(status=200)

    @mockserver.json_handler(
        '/umlaas-dispatch/umlaas-dispatch/v1/search-radius-prediction',
    )
    def _umlaas_dispatch(_):
        assert enabled_ml
        umlaas_dispatch_response = copy.deepcopy(
            v2_stubs.UMLAAS_DISPATCH_RESPONSE,
        )
        return mockserver.make_response(
            json=umlaas_dispatch_response, status=200,
        )

    request_with_requirements = {
        **v2_stubs.DRIVER_ETA_REQUEST,
        'intent': intent,
    }

    response = await taxi_driver_eta.post(
        URL,
        headers={'X-YaTaxi-PhoneId': 'phone_id_0'},
        json=request_with_requirements,
    )
    assert response.status_code == 200
    answer = response.json()
    assert answer['classes']['econom']['order_allowed']
    assert answer['classes']['vip']['order_allowed']
    if enabled_ml:
        assert answer['classes']['econom']['estimated_time'] == 42
    else:
        assert answer['classes']['econom']['estimated_time'] == 50
