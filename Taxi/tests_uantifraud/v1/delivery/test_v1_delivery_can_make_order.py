import copy

import pytest

_AUTH_HEADERS = {'X-Yandex-UID': 'yandex_uid'}
_REQUEST = {
    'delivery_description': {
        'payment_info': {'id': 'card-xxxxx', 'type': 'card'},
        'route_points': [
            {
                'type': 'source',
                'position': {'lat': 1.2, 'lon': 5.7},
                'contact': {'phone_pd_id': '1213ea8f2'},
            },
            {
                'type': 'destination',
                'position': {'lat': 3.6, 'lon': 4.5},
                'full_text': 'Some info',
            },
            {'type': 'destination', 'position': {'lat': 5.6, 'lon': 7.5}},
        ],
    },
}
_BAD_COMMENT = 'very bad comment'
_BLOCK_STATUS = 'block'
_ALLOW_STATUS = 'allow'


def _make_experiment(uid):
    return {
        'name': 'uafs_js_rules_enabled',
        'match': {
            'consumers': [{'name': 'uafs_js_rule'}],
            'predicate': {'type': 'true'},
            'enabled': True,
        },
        'clauses': [
            {
                'predicate': {
                    'init': {
                        'predicates': [
                            {
                                'init': {
                                    'arg_name': 'rule_type',
                                    'arg_type': 'string',
                                    'value': 'delivery_order',
                                },
                                'type': 'eq',
                            },
                            {
                                'init': {
                                    'arg_name': 'uuid',
                                    'arg_type': 'string',
                                    'value': uid,
                                },
                                'type': 'eq',
                            },
                        ],
                    },
                    'type': 'all_of',
                },
                'value': {'enabled': True},
            },
        ],
    }


@pytest.fixture(name='rt_xaron_service')
def _rt_xaron_service(mockserver):
    @mockserver.json_handler('rt-xaron/delivery/order-draft')
    def _handle(request):
        expected_request_json = {
            'client_ip': '',
            'payment_info': {'id': 'card-xxxxx', 'type': 'card'},
            'route_points': [
                {
                    'type': 'source',
                    'position': {'lat': 1.2, 'lon': 5.7},
                    'contact': {'phone_pd_id': '1213ea8f2'},
                },
                {
                    'type': 'destination',
                    'position': {'lat': 3.6, 'lon': 4.5},
                    'full_text': 'Some info',
                },
                {'type': 'destination', 'position': {'lat': 5.6, 'lon': 7.5}},
            ],
            'user_id': '',
            'user_personal_email_id': '',
            'user_personal_phone_id': '',
            'user_uid': 'yandex_uid',
        }

        assert request.json == expected_request_json

        return {
            'id': 1,
            'result': [
                {'name': 'rt_xaron_rule_true', 'value': True},
                {'name': 'rt_xaron_rule_false', 'value': False},
            ],
        }


async def _test_base(taxi_uantifraud, request, expected_status):
    response = await taxi_uantifraud.post(
        'v1/delivery/can_make_order', json=request, headers=_AUTH_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == {'status': expected_status}


async def test_base(taxi_uantifraud):
    await _test_base(taxi_uantifraud, _REQUEST, _ALLOW_STATUS)


@pytest.mark.experiments3(**_make_experiment(_AUTH_HEADERS['X-Yandex-UID']))
async def test_base_exp(taxi_uantifraud):
    await _test_base(taxi_uantifraud, _REQUEST, _ALLOW_STATUS)


@pytest.mark.experiments3(**_make_experiment(_AUTH_HEADERS['X-Yandex-UID']))
async def test_bad_comment(taxi_uantifraud):
    request = copy.deepcopy(_REQUEST)
    request['delivery_description']['comment'] = _BAD_COMMENT
    await _test_base(taxi_uantifraud, request, _BLOCK_STATUS)


@pytest.mark.experiments3(**_make_experiment(_AUTH_HEADERS['X-Yandex-UID']))
@pytest.mark.config(UAFS_DELIVERY_CAN_MAKE_ORDER_RT_XARON_ENABLED=True)
async def test_rtxaron(taxi_uantifraud, rt_xaron_service):
    await _test_base(taxi_uantifraud, _REQUEST, _BLOCK_STATUS)


@pytest.mark.experiments3(**_make_experiment(_AUTH_HEADERS['X-Yandex-UID']))
async def test_args(taxi_uantifraud, testpoint):
    response = {'status': _ALLOW_STATUS}

    @testpoint('test_args')
    def test_args_tp(data):
        assert data == {
            'auto_entity_map': {},
            'client_ip': '',
            'user_personal_email_id': '',
            'user_personal_phone_id': '',
            'user_id': '',
            'user_uid': 'yandex_uid',
            'payment_id': 'card-xxxxx',
            'payment_type': 'card',
            'point_a': {
                'type': 'source',
                'lat': 1.2,
                'lon': 5.7,
                'user_phone_pd_id': '1213ea8f2',
            },
            'point_b': {'type': 'destination', 'lat': 5.6, 'lon': 7.5},
            'route_points': [
                {
                    'type': 'source',
                    'lat': 1.2,
                    'lon': 5.7,
                    'user_phone_pd_id': '1213ea8f2',
                },
                {
                    'type': 'destination',
                    'lat': 3.6,
                    'lon': 4.5,
                    'full_text': 'Some info',
                },
                {'type': 'destination', 'lat': 5.6, 'lon': 7.5},
            ],
        }
        return response

    @testpoint('script_compile_failed')
    def script_compile_failed_tp(_):
        pass

    @testpoint('script_run_failed')
    def script_run_failed_tp(_):
        pass

    @testpoint('rule_exec_failed')
    def rule_exec_failed_tp(_):
        pass

    resp = await taxi_uantifraud.post(
        'v1/delivery/can_make_order', json=_REQUEST, headers=_AUTH_HEADERS,
    )

    assert resp.status_code == 200
    assert resp.json() == response

    assert await test_args_tp.wait_call()

    assert not script_compile_failed_tp.has_calls
    assert not script_run_failed_tp.has_calls
    assert not rule_exec_failed_tp.has_calls
