from abc import ABC
from abc import abstractmethod
from functools import reduce

import pytest

_REQUEST = {
    'passport_uid': 'passport_uid',
    'service_id': 'service_id',
    'login_id': 'login_id',
    'application': 'application',
    'language': 'language',
    'user_id': 'user_id',
    'pass_flags': 'pass_flags',
    'user': 'user',
    'bound_uids': 'bound_uids',
    'payload': {'field1': 'value1', 'field2': ['value2']},
}


@pytest.mark.parametrize(
    'req,result',
    [
        (_REQUEST, 'auto'),
        ({**_REQUEST, **{'type': 'additional'}}, 'standard2_force_cvv'),
    ],
)
def test_base(taxi_antifraud, mockserver, testpoint, req, result):
    @testpoint('test_rule_triggered')
    def test_rule_triggered(_):
        pass

    @testpoint('rule_passed')
    def rule_passed(_):
        pass

    @testpoint('rule_triggered')
    def rule_triggered(_):
        pass

    @mockserver.json_handler('/user-api/users/get')
    def mock_user_get(_):
        return {'id': 'user_id'}

    response = taxi_antifraud.post('/v1/card/verification/type', json=req)

    assert response.status_code == 200
    assert response.json() == {'result': result}

    assert not test_rule_triggered.has_calls
    assert not rule_passed.has_calls
    assert not rule_triggered.has_calls
    assert not mock_user_get.has_calls


def test_base_test_rule(taxi_antifraud, testpoint):
    @testpoint('test_rule_triggered')
    def test_rule_triggered(_):
        pass

    @testpoint('rule_passed')
    def rule_passed(_):
        pass

    @testpoint('rule_triggered')
    def rule_triggered(_):
        pass

    response = taxi_antifraud.post('/v1/card/verification/type', json=_REQUEST)

    assert response.status_code == 200
    assert response.json() == {'result': 'random_amt'}

    assert test_rule_triggered.wait_call() == {
        '_': {'result': 'standard2_3ds', 'rule': 'test_rule1'},
    }
    assert [rule_passed.wait_call(), rule_passed.wait_call()] == [
        {'_': {'result': 'auto', 'rule': 'test_rule2'}},
        {'_': {'result': 'random_amt', 'rule': 'rule1'}},
    ]
    assert not rule_triggered.has_calls


def test_rule_ret_priority(taxi_antifraud, testpoint):
    rules_passed = []
    rules_triggered = []

    @testpoint('test_rule_triggered')
    def test_rule_triggered_tp(_):
        pass

    @testpoint('rule_passed')
    def rule_passed_tp(data):
        rules_passed.append(data['rule'])

    @testpoint('rule_triggered')
    def rule_triggered_tp(data):
        rules_triggered.append(data['rule'])

    response = taxi_antifraud.post('/v1/card/verification/type', json=_REQUEST)

    assert response.status_code == 200
    assert response.json() == {'result': 'standard2_3ds'}

    assert not test_rule_triggered_tp.has_calls

    assert rules_passed == ['rule1', 'rule2', 'rule3', 'rule4']
    assert rules_triggered == ['rule5']


@pytest.mark.config(
    AFS_CARD_VERIFY_PASS_TELESIGN=True, AFS_CARD_VERIFY_GEOBASE_ENABLED=True,
)
@pytest.mark.parametrize(
    'req,failed,passed,triggered,result',
    [
        (
            _REQUEST,
            ['rule9', 'rule8', 'rule7', 'rule5'],
            ['rule4', 'rule3', 'rule2', 'rule1'],
            ['rule6'],
            'standard2_3ds',
        ),
        (
            {**_REQUEST, **{'type': 'additional'}},
            ['rule9', 'rule8'],
            ['rule7', 'rule6', 'rule4', 'rule3', 'rule2', 'rule1'],
            ['rule5'],
            'standard2_3ds',
        ),
        (
            {
                **_REQUEST,
                **{
                    'user_ip': 'some_ip',
                    'remote_ip': 'some_remote_ip',
                    'app_metrica_device_id': 'some_value',
                },
            },
            ['rule9', 'rule8', 'rule5'],
            ['rule4', 'rule3', 'rule2', 'rule1'],
            ['rule7', 'rule6'],
            'standard2_3ds',
        ),
        (
            {**_REQUEST, **{'user_ip': '8.8.8.8', 'remote_ip': '1.1.1.1'}},
            ['rule7', 'rule5'],
            ['rule4', 'rule3', 'rule2', 'rule1'],
            ['rule9', 'rule8', 'rule6'],
            'standard2_3ds',
        ),
    ],
)
def test_args(
        taxi_antifraud,
        mockserver,
        testpoint,
        req,
        failed,
        passed,
        triggered,
        result,
):
    rules_passed = []
    rules_failed = []
    rules_triggered = []

    @testpoint('executer_rule_failed_tp')
    def rule_failed_tp(data):
        rules_failed.append(data['rule'])

    @testpoint('test_rule_triggered')
    def test_rule_triggered_tp(_):
        pass

    @testpoint('rule_passed')
    def rule_passed_tp(data):
        rules_passed.append(data['rule'])

    @testpoint('rule_triggered')
    def rule_triggered_tp(data):
        rules_triggered.append(data['rule'])

    @mockserver.json_handler('/user-api/users/get')
    def mock_user_get(request):
        assert request.json == {
            'id': 'user_id',
            'lookup_uber': True,
            'primary_replica': False,
        }
        return {'id': 'user_id', 'phone_id': '54f7632696421984c36931f9'}

    response = taxi_antifraud.post('/v1/card/verification/type', json=req)

    assert response.status_code == 200
    assert response.json() == {'result': result}

    assert not test_rule_triggered_tp.has_calls

    assert rules_failed == failed
    assert rules_passed == passed
    assert rules_triggered == triggered


@pytest.mark.config(AFS_CARD_VERIFY_REQUIRED_RESULT_FETCH=True)
def test_card_verify_required_results_fetch(taxi_antifraud):
    response = taxi_antifraud.post('/v1/card/verification/type', json=_REQUEST)

    assert response.status_code == 200
    assert response.json() == {'result': 'standard2_3ds'}


class Stage(ABC):
    @abstractmethod
    def run(self, taxi_antifraud, db, log_extra):
        pass


class MakeRequest(Stage):
    def __init__(self, user_id, device_id, pan, expected_result):
        self.user_id = user_id
        self.device_id = device_id
        self.pan = pan
        self.expected_result = expected_result

    def __str__(self):
        return (
            f'MakeRequest(user_id={self.user_id}, device_id={self.device_id}, '
            f'fpan={self.pan}, expected_result={self.expected_result})'
        )

    def run(self, taxi_antifraud, db, log_extra):
        request = {
            **_REQUEST,
            **{
                'passport_uid': self.user_id,
                'app_metrica_device_id': self.device_id,
            },
        }

        if self.pan is not None:
            if 'payload' not in request:
                request['payload'] = {}
            request['payload']['card_number'] = self.pan

        response = taxi_antifraud.post(
            '/v1/card/verification/type', json=request,
        )

        assert 200 == response.status_code, log_extra
        if self.expected_result is not None:
            assert {
                'result': self.expected_result,
            } == response.json(), log_extra


class CheckState(Stage):
    def __init__(self, users=None, devices=None):
        assert users or devices
        self.expected_users = users or {}
        self.expected_devices = devices or {}

    def __str__(self):
        return (
            f'CheckState(expected_users={self.expected_users}, '
            f'expected_devices={self.expected_devices})'
        )

    def run(self, taxi_antifraud, db, log_extra):
        self.verify_collection__(
            db.antifraud_uids_aggregates,
            'uid',
            self.expected_users,
            log_extra,
        )
        self.verify_collection__(
            db.antifraud_devices_aggregates,
            'device_id',
            self.expected_devices,
            log_extra,
        )

    def verify_collection__(self, colection, key_field, items, log_extra):
        for key_value, expected_fields_values in items.items():
            docs = list(colection.find({key_field: key_value}))
            for (
                    field_name,
                    expected_field_value,
            ) in expected_fields_values.items():
                buckets = map(lambda doc: doc[field_name], docs)
                actual_field_value = reduce(
                    lambda x, y: x | set(y), buckets, set(),
                )
                assert sorted(expected_field_value) == sorted(
                    actual_field_value,
                ), log_extra


@pytest.mark.config(AFS_CARD_VERIFY_DEVICES_UIDS_AGGREGATION_ENABLED=True)
@pytest.mark.parametrize(
    'stages',
    [
        # basic test
        [
            MakeRequest('user_1', 'device_1', None, 'auto'),
            MakeRequest('user_1', 'device_1', None, 'auto'),
            MakeRequest('user_1', 'device_2', None, 'auto'),
            MakeRequest('user_1', 'device_3', None, 'standard2_3ds'),
            CheckState(
                {
                    'user_1': {
                        'devices_ids': ['device_1', 'device_2', 'device_3'],
                    },
                },
                {
                    'device_1': {'uids': ['user_1']},
                    'device_2': {'uids': ['user_1']},
                    'device_3': {'uids': ['user_1']},
                },
            ),
            MakeRequest('user_2', 'device_1', None, 'auto'),
            MakeRequest('user_2', 'device_2', None, 'auto'),
            MakeRequest('user_2', 'device_2', None, 'standard2_3ds'),
            MakeRequest('user_2', 'device_4', None, 'standard2_3ds'),
            CheckState(
                {
                    'user_1': {
                        'devices_ids': ['device_1', 'device_2', 'device_3'],
                    },
                    'user_2': {
                        'devices_ids': ['device_1', 'device_2', 'device_4'],
                    },
                },
                {
                    'device_1': {'uids': ['user_1', 'user_2']},
                    'device_2': {'uids': ['user_1', 'user_2']},
                    'device_3': {'uids': ['user_1']},
                    'device_4': {'uids': ['user_2']},
                },
            ),
        ],
        # with pans
        [
            MakeRequest('user_1', 'device_1', 'card_****_1', 'auto'),
            MakeRequest('user_1', 'device_2', 'card_****_2', 'auto'),
            MakeRequest('user_1', 'device_3', 'card_****_3', 'standard2_3ds'),
            CheckState(
                {
                    'user_1': {
                        'devices_ids': ['device_1', 'device_2', 'device_3'],
                        'pans': ['card_****_1', 'card_****_2', 'card_****_3'],
                    },
                },
                {
                    'device_1': {'uids': ['user_1'], 'pans': ['card_****_1']},
                    'device_2': {'uids': ['user_1'], 'pans': ['card_****_2']},
                    'device_3': {'uids': ['user_1'], 'pans': ['card_****_3']},
                },
            ),
        ],
    ],
)
def test_devicesuids_aggregates(taxi_antifraud, db, stages):
    for i, stage in enumerate(stages):
        stage.run(taxi_antifraud, db, f'at stage {i}: {stage}')
