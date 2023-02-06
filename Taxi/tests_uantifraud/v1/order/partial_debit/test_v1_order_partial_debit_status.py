import abc
import collections
import copy
import functools
import json

import pytest


_REQUEST = {
    'order_id': 'order_id1',
    'user_id': 'user_id1',
    'user_phone_id': 'user_phone_id1',
    'user_uid': 'user_uid1',
    'uber_id': 'uber_id1',
    'city': 'Moscow',
    'nz': 'mytishchi',
    'created': '2022-02-22T22:22:22+03:00',
    'payment_type': 'card',
    'payment_method_id': 'card-1234',
    'class': 'vip',
    'device_id': 'device_id1',
    'antifraud_group': 1,
    'currency': 'RUB',
    'current_price': 512,
    'fixed_price_original': 515.0,
    'is_fixed_price': True,
    'car_number': 'A123BC777',
    'driver_license_personal_id': 'driver_license_pd_1',
    'driver_db_id': 'driver_db_id1',
    'driver_uuid': 'driver_uuid1',
    'is_family': True,
    'family_is_owner': True,
    'family_owner_uid': '123456',
}


def _make_experiment():
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
                        'arg_name': 'rule_type',
                        'arg_type': 'string',
                        'value': 'order_partial_debit_status',
                    },
                    'type': 'eq',
                },
                'value': {'enabled': True},
            },
        ],
    }


async def test_base(taxi_uantifraud):
    resp = await taxi_uantifraud.post(
        '/v1/order/partial_debit/status', json=_REQUEST,
    )
    assert resp.status_code == 200
    assert resp.json() == {'use_custom_config': False}


@pytest.mark.experiments3(**_make_experiment())
async def test_enabled_not_rules(taxi_uantifraud):
    resp = await taxi_uantifraud.post(
        '/v1/order/partial_debit/status', json=_REQUEST,
    )
    assert resp.status_code == 200
    assert resp.json() == {'use_custom_config': False}


async def _test(taxi_uantifraud, testpoint, handler_response, req=None):
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
        '/v1/order/partial_debit/status',
        json=req if req is not None else _REQUEST,
    )
    assert resp.status_code == 200
    assert resp.json() == handler_response

    assert not script_compile_failed_tp.has_calls
    assert not script_run_failed_tp.has_calls
    assert not rule_exec_failed_tp.has_calls


@pytest.mark.experiments3(**_make_experiment())
@pytest.mark.config(
    UAFS_PARTIAL_DEBIT_RT_XARON_ENABLED=True,
    UAFS_PARTIAL_DEBIT_STATUS_PRIORITY=['hacker'],
)
async def test_args(taxi_uantifraud, testpoint, mockserver):
    expected_json = {
        'order_id': 'order_id1',
        'user_id': 'user_id1',
        'user_phone_id': 'user_phone_id1',
        'user_uid': 'user_uid1',
        'uber_id': 'uber_id1',
        'city': 'Moscow',
        'nz': 'mytishchi',
        'created': '2022-02-22T19:22:22.000Z',
        'payment_type': 'card',
        'payment_method_id': 'card-1234',
        'class': 'vip',
        'device_id': 'device_id1',
        'antifraud_group': 1,
        'currency': 'RUB',
        'current_price': 512,
        'fixed_price_original': 515.0,
        'is_fixed_price': True,
        'car_number': 'A123BC777',
        'driver_license_personal_id': 'driver_license_pd_1',
        'driver_db_id': 'driver_db_id1',
        'driver_uuid': 'driver_uuid1',
        'is_family': True,
        'family_is_owner': True,
        'family_owner_uid': '123456',
    }

    @testpoint('test_args')
    def test_args_tp(data):
        # aggregates will be checked in separate test
        del data['aggregates']

        assert data == {
            **expected_json,
            **{'auto_entity_map': {}, 'rt_xaron': ['rule1']},
        }
        return {'frauder': True, 'status': 'hacker'}

    @mockserver.json_handler('/rt-xaron/taxi/order/partial_debit/status')
    def _rt_xaron_handler(request):
        assert request.json == {
            **expected_json,
            **{'created': _REQUEST['created']},
        }
        return {
            'id': 42,
            'result': [
                {'name': 'rule1', 'value': True},
                {'name': 'rule2', 'value': False},
            ],
        }

    await _test(
        taxi_uantifraud,
        testpoint,
        {'use_custom_config': True, 'status': 'hacker'},
    )

    assert await test_args_tp.wait_call()
    assert await _rt_xaron_handler.wait_call()


@pytest.mark.experiments3(**_make_experiment())
@pytest.mark.config(UAFS_PARTIAL_DEBIT_STATUS_PRIORITY=[])
async def test_empty_config(taxi_uantifraud, testpoint):
    await _test(taxi_uantifraud, testpoint, {'use_custom_config': False})


@pytest.mark.experiments3(**_make_experiment())
@pytest.mark.config(
    UAFS_PARTIAL_DEBIT_STATUS_PRIORITY=[
        'status1',
        'status2',
        'most_priority_status',
    ],
)
async def test_priority(taxi_uantifraud, testpoint):
    await _test(
        taxi_uantifraud,
        testpoint,
        {'status': 'most_priority_status', 'use_custom_config': True},
    )


@pytest.mark.experiments3(**_make_experiment())
@pytest.mark.config(UAFS_PARTIAL_DEBIT_FETCH_LOGIN_ID=True)
@pytest.mark.parametrize('device_id', ['metrica_device_id1', None])
async def test_fetch_login_id_empty_collection(
        taxi_uantifraud, testpoint, device_id,
):
    @testpoint('wo_device_one_empty')
    def _wo_device_one_empty(_):
        pass

    @testpoint('with_device_many_empty')
    def _with_device_many_empty(_):
        pass

    req = copy.deepcopy(_REQUEST)
    if device_id is not None:
        req['device_id'] = device_id
    elif 'device_id' in req:
        del req['device_id']

    resp = await taxi_uantifraud.post(
        '/v1/order/partial_debit/status', json=req,
    )
    assert resp.status_code == 200
    assert resp.json() == {'use_custom_config': False}

    if device_id is None:
        assert await _wo_device_one_empty.wait_call()
    else:
        assert await _with_device_many_empty.wait_call()


@pytest.mark.experiments3(**_make_experiment())
@pytest.mark.config(UAFS_PARTIAL_DEBIT_FETCH_LOGIN_ID=True)
@pytest.mark.parametrize('device_id', ['metrica_device_id1', None])
async def test_fetch_login_id_one_record_only_uid(
        taxi_uantifraud, testpoint, device_id,
):
    @testpoint('test_args')
    def _test_args_tp(data):
        assert data['login_info'] == {
            'id': 't:26452126',
            'is_with_device': False,
        }

    @testpoint('wo_device_one_found')
    def _wo_device_one_found(_):
        pass

    @testpoint('with_device_many_one')
    def _with_device_many_one(_):
        pass

    req = copy.deepcopy(_REQUEST)
    if device_id is not None:
        req['device_id'] = device_id
    elif 'device_id' in req:
        del req['device_id']

    resp = await taxi_uantifraud.post(
        '/v1/order/partial_debit/status',
        json={**req, **{'user_uid': '4073579358'}},
    )
    assert resp.status_code == 200
    assert resp.json() == {'use_custom_config': False}

    assert await _test_args_tp.wait_call()

    if device_id is None:
        assert await _wo_device_one_found.wait_call()
    else:
        assert await _with_device_many_one.wait_call()


@pytest.mark.experiments3(**_make_experiment())
@pytest.mark.config(UAFS_PARTIAL_DEBIT_FETCH_LOGIN_ID=True)
@pytest.mark.parametrize(
    'device_id', ['50bbdc21dbc25f8737b9020c3765f24a', None],
)
async def test_fetch_login_id_one_record_only_uid_device_id(
        taxi_uantifraud, testpoint, device_id,
):
    @testpoint('test_args')
    def _test_args_tp(data):
        if device_id is not None:
            assert data['login_info'] == {
                'id': 't:26452126',
                'is_with_device': True,
            }
        else:
            assert 'login_id' not in data

    @testpoint('wo_device_one_empty')
    def _wo_device_one_empty(_):
        pass

    @testpoint('with_device_many_one')
    def _with_device_many_one(_):
        pass

    req = copy.deepcopy(_REQUEST)
    if device_id is not None:
        req['device_id'] = device_id
    elif 'device_id' in req:
        del req['device_id']

    resp = await taxi_uantifraud.post(
        '/v1/order/partial_debit/status',
        json={**req, **{'user_uid': '4073579358'}},
    )
    assert resp.status_code == 200
    assert resp.json() == {'use_custom_config': False}

    assert await _test_args_tp.wait_call()

    if device_id is None:
        assert await _wo_device_one_empty.wait_call()
    else:
        assert await _with_device_many_one.wait_call()


@pytest.mark.experiments3(**_make_experiment())
@pytest.mark.config(UAFS_PARTIAL_DEBIT_FETCH_LOGIN_ID=True)
@pytest.mark.parametrize(
    'device_id', ['50bbdc21dbc25f8737b9020c3765f24a', None],
)
async def test_fetch_login_id_multiple_records(
        taxi_uantifraud, testpoint, device_id,
):
    @testpoint('test_args')
    def _test_args_tp(data):
        if device_id is not None:
            assert data['login_info'] == {
                'id': 't:21408028',
                'is_with_device': True,
            }
        else:
            assert data['login_info'] == {
                'id': 't:26452126',
                'is_with_device': False,
            }

    @testpoint('wo_device_one_found')
    def _wo_device_one_found(_):
        pass

    @testpoint('with_device_many_two')
    def _with_device_many_two(_):
        pass

    req = copy.deepcopy(_REQUEST)
    if device_id is not None:
        req['device_id'] = device_id
    elif 'device_id' in req:
        del req['device_id']

    resp = await taxi_uantifraud.post(
        '/v1/order/partial_debit/status',
        json={**req, **{'user_uid': '4073579358'}},
    )
    assert resp.status_code == 200
    assert resp.json() == {'use_custom_config': False}

    assert await _test_args_tp.wait_call()

    if device_id is None:
        assert await _wo_device_one_found.wait_call()
    else:
        assert await _with_device_many_two.wait_call()


class UantifraudCountWrapper:
    def __init__(self, taxi_uantifraud, testpoint):
        self.taxi_uantifraud = taxi_uantifraud
        self.requests_count = 0

        @testpoint('order_partial_debit_status_update_user_aggregates_done')
        def user_aggregates_updated_tp(_):
            pass

        @testpoint('order_partial_debit_status_update_device_aggregates_done')
        def device_aggregates_updated_tp(_):
            pass

        self.user_aggregates_updated_tp = user_aggregates_updated_tp
        self.device_aggregates_updated_tp = device_aggregates_updated_tp

    async def order_partial_debit_status(self, request):
        self.requests_count += 1
        return await self.taxi_uantifraud.post(
            '/v1/order/partial_debit/status', json=request,
        )

    def reset_count(self):
        self.requests_count = 0

    async def wait_for_background_testpoints(self):
        if self.requests_count > 0:
            await self.device_aggregates_updated_tp.wait_call()
            await self.user_aggregates_updated_tp.wait_call()
            self.requests_count = 0


class Stage(abc.ABC):
    @abc.abstractmethod
    async def run(self, taxi_uantifraud, mongodb, log_extra):
        pass


class MakeRequest(Stage):
    def __init__(self, user_id, device_id, order, expected_result):
        self.user_id = user_id
        self.device_id = device_id
        self.order = order
        self.expected_result = expected_result

    def __str__(self):
        return (
            f'MakeRequest(device_id={self.device_id}, '
            f'user_id={self.user_id}, order={self.order}, '
            f'expected_result={self.expected_result})'
        )

    async def run(self, taxi_uantifraud, mongodb, log_extra):
        request = {**_REQUEST, **{'user_uid': self.user_id}}
        if self.device_id is not None:
            if self.device_id != _NO_DEVICE_ID:
                request['device_id'] = self.device_id
            else:
                del request['device_id']
        if self.order is not None:
            request['order_id'] = self.order['order_id']
            request['nz'] = self.order['nz']
            request['payment_type'] = self.order['payment_type']

        response = await taxi_uantifraud.order_partial_debit_status(request)

        # NOTE: pytest treats left arg as expected result and right arg as
        # actual result and shows diff accordingly, but pylint dont know it
        # pylint: disable=C0122
        assert 200 == response.status_code

        if self.expected_result is not None:
            assert self.expected_result == response.json(), log_extra


class DistinctValuesChecker:
    def __init__(self, *args):
        self.expected_value = set(list(args))

    def check(self, buckets, log_extra):
        actual_value = functools.reduce(
            lambda x, y: x | set(y), buckets, set(),
        )
        assert sorted(self.expected_value) == sorted(actual_value), log_extra


class GroupedDistinctValuesChecker:
    def __init__(self, expected_value):
        self.expected_value = expected_value

    def check(self, buckets, log_extra):
        actual_value = collections.defaultdict(set)
        for bucket in buckets:
            for group, values in bucket.items():
                actual_value[group] |= set(values)
        assert sorted(self.expected_value.keys()) == sorted(
            actual_value.keys(),
        ), log_extra
        for group, values in self.expected_value.items():
            assert sorted(values) == sorted(actual_value[group]), log_extra


class CheckState(Stage):
    def __init__(self, users, devices):
        self.expected_users = users
        self.expected_devices = devices

    def __str__(self):
        return (
            f'CheckState(expected_devices={self.expected_devices}, '
            f'expected_devices={self.expected_users})'
        )

    async def run(self, taxi_uantifraud, mongodb, log_extra):
        await taxi_uantifraud.wait_for_background_testpoints()

        self.verify_collection__(
            mongodb.antifraud_order_partial_debit_status_user_aggregates,
            'user_id',
            self.expected_users,
            log_extra,
        )

        self.verify_collection__(
            mongodb.antifraud_order_partial_debit_status_device_aggregates,
            'device_id',
            self.expected_devices,
            log_extra,
        )

    def verify_collection__(self, colection, key_field, items, log_extra):
        for key_value, expected_fields_values in items.items():
            docs = list(colection.find({key_field: key_value}))
            for (field_name, field_checker) in expected_fields_values.items():
                buckets = [
                    doc[field_name] for doc in docs if field_name in doc
                ]
                field_checker.check(buckets, log_extra)


_USER_01 = 'user_uid_01'
_USER_02 = 'user_uid_02'
_USER_03 = 'user_uid_03'
_USER_04 = 'user_uid_04'
_USER_05 = 'user_uid_05'
_USER_06 = 'user_uid_05'

_DEVICE_01 = 'device_01'
_DEVICE_02 = 'device_02'
_DEVICE_03 = 'device_03'
_DEVICE_04 = 'device_04'
_DEVICE_05 = 'device_05'

_NO_DEVICE_ID = 'no_device_id_'


def _make_aggregates_experiment(entity, mode):
    return {
        'name': (
            f'uafs_order_partial_debit_status_{entity}'
            f'_aggregates_{mode}_enabled'
        ),
        'match': {
            'consumers': [
                {
                    'name': (
                        f'uafs_order_partial_debit_status_{entity}'
                        f'_aggregates_{mode}'
                    ),
                },
            ],
            'predicate': {'type': 'true'},
            'enabled': True,
        },
        'clauses': [
            {
                'predicate': {'init': {}, 'type': 'true'},
                'value': {'enabled': True},
            },
        ],
    }


def _make_experiment_device_aggregates_read():
    return _make_aggregates_experiment('device', 'read')


def _make_experiment_device_aggregates_write():
    return _make_aggregates_experiment('device', 'write')


def _make_experiment_user_aggregates_read():
    return _make_aggregates_experiment('user', 'read')


def _make_experiment_user_aggregates_write():
    return _make_aggregates_experiment('user', 'write')


@pytest.mark.experiments3(**_make_experiment())
@pytest.mark.experiments3(**_make_experiment_device_aggregates_read())
@pytest.mark.experiments3(**_make_experiment_device_aggregates_write())
@pytest.mark.experiments3(**_make_experiment_user_aggregates_read())
@pytest.mark.experiments3(**_make_experiment_user_aggregates_write())
@pytest.mark.parametrize(
    'stages',
    [
        # user/device aggregates basic test
        [
            MakeRequest(_USER_01, _DEVICE_01, None, None),
            MakeRequest(_USER_01, _DEVICE_02, None, None),
            MakeRequest(_USER_01, _DEVICE_03, None, None),
            MakeRequest(_USER_02, _DEVICE_04, None, None),
            MakeRequest(_USER_03, _DEVICE_04, None, None),
            MakeRequest(_USER_04, _DEVICE_04, None, None),
            CheckState(
                {
                    _USER_01: {
                        'devices_ids': DistinctValuesChecker(
                            _DEVICE_01, _DEVICE_02, _DEVICE_03,
                        ),
                    },
                    _USER_02: {
                        'devices_ids': DistinctValuesChecker(_DEVICE_04),
                    },
                    _USER_03: {
                        'devices_ids': DistinctValuesChecker(_DEVICE_04),
                    },
                    _USER_04: {
                        'devices_ids': DistinctValuesChecker(_DEVICE_04),
                    },
                },
                {
                    _DEVICE_01: {'users_ids': DistinctValuesChecker(_USER_01)},
                    _DEVICE_02: {'users_ids': DistinctValuesChecker(_USER_01)},
                    _DEVICE_03: {'users_ids': DistinctValuesChecker(_USER_01)},
                    _DEVICE_04: {
                        'users_ids': DistinctValuesChecker(
                            _USER_02, _USER_03, _USER_04,
                        ),
                    },
                },
            ),
        ],
        # user/payments aggregates basic test
        [
            MakeRequest(
                _USER_05,
                _DEVICE_05,
                {
                    'nz': 'nz_01',
                    'payment_type': 'card',
                    'order_id': 'order_01',
                },
                None,
            ),
            MakeRequest(
                _USER_05,
                _DEVICE_05,
                {
                    'nz': 'nz_01',
                    'payment_type': 'card',
                    'order_id': 'order_02',
                },
                None,
            ),
            MakeRequest(
                _USER_05,
                _DEVICE_05,
                {
                    'nz': 'nz_01',
                    'payment_type': 'cash',
                    'order_id': 'order_03',
                },
                None,
            ),
            MakeRequest(
                _USER_05,
                _DEVICE_05,
                {
                    'nz': 'nz_02',
                    'payment_type': 'cash',
                    'order_id': 'order_04',
                },
                None,
            ),
            MakeRequest(
                _USER_05,
                _DEVICE_05,
                {
                    'nz': 'nz_02',
                    'payment_type': 'cash',
                    'order_id': 'order_05',
                },
                None,
            ),
            CheckState(
                {
                    _USER_05: {
                        'zones_payments': GroupedDistinctValuesChecker(
                            {
                                'nz_01|card': ['order_01', 'order_02'],
                                'nz_01|cash': ['order_03'],
                                'nz_02|cash': ['order_04', 'order_05'],
                            },
                        ),
                    },
                },
                {},
            ),
        ],
        # requests without device_id
        [
            MakeRequest(
                _USER_06,
                _NO_DEVICE_ID,
                {
                    'nz': 'nz_01',
                    'payment_type': 'card',
                    'order_id': 'order_06',
                },
                None,
            ),
            CheckState(
                {
                    _USER_06: {
                        'devices_ids': DistinctValuesChecker(),
                        'zones_payments': GroupedDistinctValuesChecker(
                            {'nz_01|card': ['order_06']},
                        ),
                    },
                },
                {},
            ),
        ],
    ],
)
async def test_user_device_aggregates(
        taxi_uantifraud, mongodb, testpoint, stages,
):
    taxi_uantifraud = UantifraudCountWrapper(taxi_uantifraud, testpoint)
    for i, stage in enumerate(stages):
        await stage.run(taxi_uantifraud, mongodb, f'at stage {i}: {stage}')


@pytest.mark.experiments3(**_make_experiment())
@pytest.mark.config(
    UAFS_PARTIAL_DEBIT_STATUS_PRIORITY=[
        'legacy-hacker',  # <-- lowest priority
        'pre-hold-hacker',
        'hacker-when-transporting',
    ],
)
@pytest.mark.parametrize(
    'order_status, taxi_status, expected_status',
    [
        ('assigned', 'driving', 'pre-hold-hacker'),
        ('assigned', 'transporting', 'hacker-when-transporting'),
        (None, None, 'legacy-hacker'),
    ],
)
async def test_different_taxi_statuses(
        taxi_uantifraud, testpoint, order_status, taxi_status, expected_status,
):
    request = copy.deepcopy(_REQUEST)
    if order_status:
        request['order_status'] = order_status
    if taxi_status:
        request['taxi_status'] = taxi_status
    await _test(
        taxi_uantifraud,
        testpoint,
        {'use_custom_config': True, 'status': expected_status},
        request,
    )


@pytest.mark.experiments3(**_make_experiment())
@pytest.mark.config(
    UAFS_PARTIAL_DEBIT_STATUS_PRIORITY=['frauder_from_tag_status'],
    UAFS_PARTIAL_DEBIT_ENABLE_TAGS=True,
)
@pytest.mark.parametrize(
    'tags,response',
    [
        [
            ['frauder'],
            {'use_custom_config': True, 'status': 'frauder_from_tag_status'},
        ],
        [[], {'use_custom_config': False}],
    ],
)
async def test_tags(taxi_uantifraud, testpoint, mockserver, tags, response):
    @mockserver.json_handler('/passenger-tags/v2/match_single')
    def _handler(request):
        data = request.json
        assert data == {
            'match': [{'type': 'personal_phone_id', 'value': 'some_phone_id'}],
        }
        return {'tags': tags}

    request = copy.deepcopy(_REQUEST)
    request['personal_phone_id'] = 'some_phone_id'
    await _test(taxi_uantifraud, testpoint, response, request)


@pytest.mark.experiments3(**_make_experiment())
@pytest.mark.config(
    UAFS_PARTIAL_DEBIT_STATUS_PRIORITY=['frauder_from_tag_status'],
    UAFS_PARTIAL_DEBIT_ENABLE_TAGS=False,
)
@pytest.mark.parametrize(
    'tags,response', [[['frauder'], {'use_custom_config': False}]],
)
async def test_no_tags(taxi_uantifraud, testpoint, mockserver, tags, response):
    @mockserver.json_handler('/passenger-tags/v2/match_single')
    def _handler(request):
        data = request.json
        assert data == {
            'match': [{'type': 'personal_phone_id', 'value': 'some_phone_id'}],
        }
        return {'tags': tags}

    request = copy.deepcopy(_REQUEST)
    request['personal_phone_id'] = 'some_phone_id'
    await _test(taxi_uantifraud, testpoint, response, request)


@pytest.mark.experiments3(**_make_experiment())
@pytest.mark.config(
    UAFS_PARTIAL_DEBIT_STATUS_PRIORITY=['status1'],
    UAFS_PARTIAL_DEBIT_SATURN_ENABLED={
        'enabled': True,
        'formula_ids': ['formula1', 'formula2'],
        'store_to_redis': True,
        'load_from_redis': True,
    },
)
async def test_saturn_base(
        taxi_uantifraud, testpoint, mockserver, taxi_config, redis_store,
):
    saturn_requests = {}
    uid = '162823816'

    def _make_saturn_response(formula_id):
        return {
            'reqid': _REQUEST['order_id'],
            'puid': int(uid),
            'score': 38.49,
            'score_percentile': 50.1,
            'formula_id': formula_id,
            'formula_description': 'some formula',
            'data_source': 'some data source',
            'status': 'rejected',
        }

    @mockserver.json_handler('/saturn/api/v1/taxi/search')
    def _saturn(request):
        req = request.json
        saturn_requests[req['formula_id']] = req
        return _make_saturn_response(req['formula_id'])

    @testpoint('test_args')
    def _test_args_tp(data):
        assert data == {
            'aggregates': {},
            'antifraud_group': 1,
            'auto_entity_map': {},
            'car_number': 'A123BC777',
            'city': 'Moscow',
            'class': 'vip',
            'created': '2022-02-22T19:22:22.000Z',
            'currency': 'RUB',
            'current_price': 512,
            'device_id': 'device_id1',
            'driver_db_id': 'driver_db_id1',
            'driver_license_personal_id': 'driver_license_pd_1',
            'driver_uuid': 'driver_uuid1',
            'is_family': True,
            'family_is_owner': True,
            'family_owner_uid': '123456',
            'fixed_price_original': 515,
            'is_fixed_price': True,
            'nz': 'mytishchi',
            'order_id': 'order_id1',
            'payment_method_id': 'card-1234',
            'payment_type': 'card',
            'saturn': {
                f_id: _make_saturn_response(f_id)
                for f_id in taxi_config.get_values()[
                    'UAFS_PARTIAL_DEBIT_SATURN_ENABLED'
                ]['formula_ids']
            },
            'uber_id': 'uber_id1',
            'user_id': 'user_id1',
            'user_phone_id': 'user_phone_id1',
            'user_uid': uid,
        }
        return {'frauder': True, 'status': 'status1'}

    @testpoint('redis_load_empty')
    def _redis_load_empty(_):
        pass

    @testpoint('redis_load_success')
    def _redis_load_success(_):
        pass

    @testpoint('redis_load_failed')
    def _redis_load_failed(_):
        pass

    @testpoint('redis_store_success')
    def _redis_store_success(_):
        pass

    @testpoint('redis_store_failed')
    def _redis_store_failed(_):
        pass

    @testpoint('redis_store_not_needed')
    def _redis_store_not_needed(_):
        pass

    resp1 = await taxi_uantifraud.post(
        '/v1/order/partial_debit/status', {**_REQUEST, **{'user_uid': uid}},
    )

    for _ in range(2):
        assert await _saturn.wait_call()

    assert saturn_requests == {
        f_id: {
            'formula_id': f_id,
            'puid': int(uid),
            'request_id': _REQUEST['order_id'],
            'service': 'taxi',
            'basket': {'total_sum': _REQUEST['fixed_price_original']},
        }
        for f_id in taxi_config.get_values()[
            'UAFS_PARTIAL_DEBIT_SATURN_ENABLED'
        ]['formula_ids']
    }

    assert resp1.status_code == 200
    assert resp1.json() == {'status': 'status1', 'use_custom_config': True}

    assert await _redis_load_empty.wait_call()
    assert await _redis_store_success.wait_call()

    resp2 = await taxi_uantifraud.post(
        '/v1/order/partial_debit/status', {**_REQUEST, **{'user_uid': uid}},
    )

    assert resp2.status_code == 200
    assert resp2.json() == {'status': 'status1', 'use_custom_config': True}

    assert await _redis_load_success.wait_call()
    assert await _redis_store_not_needed.wait_call()

    assert not _redis_store_success.times_called
    assert not _saturn.times_called
    assert not _redis_load_failed.times_called
    assert not _redis_store_failed.times_called

    assert (
        json.loads(
            redis_store.get(
                f'v1:order:partial_debit:status:saturn:{_REQUEST["order_id"]}',
            ).decode(),
        )
        == {
            f_id: _make_saturn_response(f_id)
            for f_id in taxi_config.get_values()[
                'UAFS_PARTIAL_DEBIT_SATURN_ENABLED'
            ]['formula_ids']
        }
    )
