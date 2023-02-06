import abc
import functools

import pytest


_REQUEST = {
    'service': 'service',
    'service_type': 'service_type',
    'app_metrica_device_id': 'E030F317-4FE0-4EE0-8C0B-42EA9BC4F552',
    'app_metrica_uuid': 'app_metrica_uuid',
    'cards': [
        {
            'id': 'card_id1',
            'number': 'card_number1',
            'verification_details': {
                'level': 'card_level1',
                'service_id': 1,
                'verified_at': '2021-01-10T09:10:11+03:00',
            },
        },
        {
            'id': 'card_id2',
            'number': 'card_number2',
            'verification_details': {
                'level': 'card_level2',
                'service_id': 2,
                'verified_at': '2021-01-20T10:11:12+03:00',
            },
        },
        {
            'id': 'card_id3',
            'number': 'card_number3',
            'verification_details': {
                'level': 'card_level3',
                'service_id': 3,
                'verified_at': '2021-01-20T10:11:12+03:00',
            },
        },
        {
            'id': 'card_id4',
            'number': 'card_number4',
            'verification_details': {
                'level': 'card_level4',
                'service_id': 4,
                'verified_at': '2021-01-20T10:11:12+03:00',
            },
        },
        {
            'id': 'card_id5',
            'number': 'card_number5',
            'verification_details': {
                'level': '3ds',
                'service_id': 5,
                'verified_at': '2021-01-20T10:11:12+03:00',
            },
        },
    ],
}
_YANDEX_UID = '4023520426'
_USER_ID = 'our_user_id1'


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
                        'predicates': [
                            {
                                'init': {
                                    'arg_name': 'rule_type',
                                    'arg_type': 'string',
                                    'value': 'card_verify_required',
                                },
                                'type': 'eq',
                            },
                            {
                                'init': {
                                    'arg_name': 'uuid',
                                    'arg_type': 'string',
                                    'value': _YANDEX_UID,
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


@pytest.mark.experiments3(**_make_experiment())
async def test_base(taxi_uantifraud, mongodb, testpoint):
    @testpoint('script_compile_failed')
    def script_compile_failed_tp(_):
        pass

    @testpoint('script_run_failed')
    def script_run_failed_tp(_):
        pass

    @testpoint('rule_exec_failed')
    def rule_exec_failed_tp(_):
        pass

    @testpoint('test_args')
    def test_args_tp(data):
        assert data == {
            'service': 'service',
            'service_type': 'service_type',
            'app_metrica_device_id': 'E030F317-4FE0-4EE0-8C0B-42EA9BC4F552',
            'app_metrica_uuid': 'app_metrica_uuid',
            'cards': [
                {
                    'id': 'card_id1',
                    'number': 'card_number1',
                    'verification_details': {
                        'level': 'card_level1',
                        'service_id': 1,
                        'verified_at': '2021-01-10T06:10:11.000Z',
                    },
                },
                {
                    'id': 'card_id2',
                    'number': 'card_number2',
                    'verification_details': {
                        'level': 'card_level2',
                        'service_id': 2,
                        'verified_at': '2021-01-20T07:11:12.000Z',
                    },
                },
                {
                    'id': 'card_id3',
                    'number': 'card_number3',
                    'verification_details': {
                        'level': 'card_level3',
                        'service_id': 3,
                        'verified_at': '2021-01-20T07:11:12.000Z',
                    },
                },
                {
                    'id': 'card_id4',
                    'number': 'card_number4',
                    'verification_details': {
                        'level': 'card_level4',
                        'service_id': 4,
                        'verified_at': '2021-01-20T07:11:12.000Z',
                    },
                },
                {
                    'id': 'card_id5',
                    'number': 'card_number5',
                    'verification_details': {
                        'level': '3ds',
                        'service_id': 5,
                        'verified_at': '2021-01-20T07:11:12.000Z',
                    },
                },
            ],
            'is_authorized': True,
            'yandex_uid': _YANDEX_UID,
            'yandex_login': '',
            'login_id': '',
            'yandex_taxi_userid': _USER_ID,
            'flags': {
                'has_portal': False,
                'has_pdd': False,
                'has_phonish': False,
                'has_neophonish': False,
                'has_lite': False,
                'has_social': False,
                'is_portal': False,
                'has_ya_plus': False,
                'no_login': False,
                'phone_confirm_required': False,
                'has_plus_cashback': False,
            },
            'locale': '',
            'app_vars': {
                'app_name': '',
                'platform_ver1': '',
                'platform_ver2': '',
                'platform_ver3': '',
                'app_ver': '',
                'app_ver1': '',
                'app_ver2': '',
                'app_ver3': '',
                'app_build': '',
                'app_brand': '',
            },
            'personal_data': {'phone_id': '', 'email_id': '', 'eats_id': ''},
            'auto_entity_map': {},
            'remote_ip': '8.8.8.8',
            'remote_ip_info': {
                'is_tor': False,
                'is_hosting': False,
                'is_proxy': False,
                'is_vpn': False,
                'is_mobile': False,
            },
            'country': 'us',
            'city': 'us was',
        }
        return {
            'statuses': [
                {'id': 'card_id1', 'status': 'auto'},
                {
                    'id': 'card_id2',
                    'status': 'standard2',
                    'reason': 'custom_reason',
                },
                {'id': 'card_id3', 'status': 'standard2_3ds'},
                {
                    'id': 'card_id5',
                    'status': 'standard2',
                    'reason': 'test_rule1_custom_reason',
                },
                {'id': 'nonexistent_card_id', 'status': 'standard2_3ds'},
            ],
        }

    @testpoint('card_verify_required_update_results_done')
    def update_results_done_tp(_):
        pass

    resp = await taxi_uantifraud.post(
        '/v1/card/verification/required',
        json=_REQUEST,
        headers={
            'X-YaTaxi-UserId': _USER_ID,
            'X-Yandex-UID': _YANDEX_UID,
            'X-Remote-IP': '8.8.8.8',
        },
    )
    assert resp.status_code == 200
    assert resp.json() == {
        'unavailable_cards': [
            {'id': 'card_id2', 'reason': {'key': 'custom_reason'}},
            {
                'id': 'card_id3',
                'reason': {'key': 'common_errors.NEED_CARD_ANTIFRAUD'},
            },
            {'id': 'card_id5', 'reason': {'key': 'test_rule2_custom_reason'}},
        ],
    }

    await test_args_tp.wait_call()

    assert not script_compile_failed_tp.has_calls
    assert not script_run_failed_tp.has_calls
    assert not rule_exec_failed_tp.has_calls

    await update_results_done_tp.wait_call()

    assert (
        mongodb.antifraud_card_verification_required_results.find_one(
            {'_id': _YANDEX_UID},
        )['results']
        == [
            {'card_id': 'card_id1', 'result': 'auto'},
            {'card_id': 'card_id2', 'result': 'standard2'},
            {'card_id': 'card_id3', 'result': 'standard2_3ds'},
            {'card_id': 'card_id4', 'result': 'auto'},
            {'card_id': 'card_id5', 'result': 'standard2_3ds'},
        ]
    )


@pytest.mark.experiments3(**_make_experiment())
async def test_auto_entity_map(taxi_uantifraud):
    resp = await taxi_uantifraud.post(
        '/v1/card/verification/required',
        json=_REQUEST,
        headers={'X-YaTaxi-UserId': 'user_id', 'X-Yandex-UID': _YANDEX_UID},
    )
    assert resp.status_code == 200
    assert resp.json() == {
        'unavailable_cards': [
            {'id': 'card_id1', 'reason': {'key': 'test_rule2_custom_reason'}},
            {
                'id': 'card_id2',
                'reason': {'key': 'common_errors.NEED_CARD_ANTIFRAUD'},
            },
            {
                'id': 'card_id3',
                'reason': {'key': 'common_errors.NEED_CARD_ANTIFRAUD'},
            },
            {
                'id': 'card_id4',
                'reason': {'key': 'common_errors.NEED_CARD_ANTIFRAUD'},
            },
        ],
    }


class UantifraudCountWrapper:
    def __init__(self, taxi_uantifraud, testpoint):
        self.taxi_uantifraud = taxi_uantifraud
        self.requests_count = 0

        @testpoint('card_verify_required_update_device_aggregates_done')
        def device_aggregates_updated_tp(_):
            pass

        @testpoint('card_verify_required_update_user_aggregates_done')
        def user_aggregates_updated_tp(_):
            pass

        self.device_aggregates_updated_tp = device_aggregates_updated_tp
        self.user_aggregates_updated_tp = user_aggregates_updated_tp

    async def card_verification_required(self, request, headers):
        self.requests_count += 1
        return await self.taxi_uantifraud.post(
            '/v1/card/verification/required', json=request, headers=headers,
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
    def __init__(self, device_id, user_id, cards, expected_result):
        self.device_id = device_id
        self.user_id = user_id
        self.cards = cards
        self.expected_result = expected_result

    def __str__(self):
        return (
            f'MakeRequest(device_id={self.device_id}, '
            f'user_id={self.user_id}, cards={self.cards}, '
            f'expected_result={self.expected_result})'
        )

    async def run(self, taxi_uantifraud, mongodb, log_extra):

        response = await taxi_uantifraud.card_verification_required(
            request={
                **_REQUEST,
                **{
                    'yandex_uid': self.user_id,
                    'app_metrica_device_id': self.device_id,
                    'cards': self.cards,
                },
            },
            headers={
                'X-YaTaxi-UserId': 'user_id',
                'X-Yandex-UID': self.user_id,
            },
        )

        # NOTE: pytest treats left arg as expected result and right arg as
        # actual result and shows diff accordingly, but pylint dont know it
        # pylint: disable=C0122
        assert 200 == response.status_code

        if self.expected_result is not None:
            assert {
                'unavailable_cards': self.expected_result,
            } == response.json(), log_extra


class CheckState(Stage):
    def __init__(self, devices, users):
        self.expected_devices = devices
        self.expected_users = users

    def __str__(self):
        return (
            f'CheckState(expected_devices={self.expected_devices}, '
            f'expected_devices={self.expected_users})'
        )

    async def run(self, taxi_uantifraud, mongodb, log_extra):
        await taxi_uantifraud.wait_for_background_testpoints()

        self.verify_collection__(
            mongodb.antifraud_card_verification_required_device_aggregates,
            'device_id',
            self.expected_devices,
            log_extra,
        )

        self.verify_collection__(
            mongodb.antifraud_card_verification_required_user_aggregates,
            'user_id',
            self.expected_users,
            log_extra,
        )

    def verify_collection__(self, colection, key_field, items, log_extra):
        for key_value, expected_fields_values in items.items():
            docs = list(colection.find({key_field: key_value}))
            for (
                    field_name,
                    expected_field_value,
            ) in expected_fields_values.items():
                buckets = [doc[field_name] for doc in docs]
                actual_field_value = functools.reduce(
                    lambda x, y: x | set(y), buckets, set(),
                )
                assert sorted(expected_field_value) == sorted(
                    actual_field_value,
                ), log_extra


_USER_01 = _YANDEX_UID

_DEVICE_01 = 'device_1'

_CARD_01 = {
    'id': 'card_id1',
    'number': 'card_number1',
    'verification_details': {
        'level': 'card_level1',
        'service_id': 1,
        'verified_at': '2021-01-10T09:10:11+03:00',
    },
}

_CARD_02 = {
    'id': 'card_id2',
    'number': 'card_number2',
    'verification_details': {
        'level': 'card_level2',
        'service_id': 2,
        'verified_at': '2021-01-20T10:11:12+03:00',
    },
}

_CARD_03 = {
    'id': 'card_id3',
    'number': 'card_number3',
    'verification_details': {
        'level': 'card_level3',
        'service_id': 3,
        'verified_at': '2021-01-20T10:11:12+03:00',
    },
}

_CARD_04 = {
    'id': 'card_id4',
    'number': 'card_number4',
    'verification_details': {
        'level': 'card_level4',
        'service_id': 4,
        'verified_at': '2021-01-20T10:11:12+03:00',
    },
}


def _make_aggregates_experiment(entity, mode, arg_name, arg_value):
    return {
        'name': f'uafs_{entity}_aggregates_{mode}_enabled',
        'match': {
            'consumers': [{'name': f'uafs_{entity}_aggregates_{mode}'}],
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
                                    'arg_name': arg_name,
                                    'arg_type': 'string',
                                    'value': arg_value,
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


def _make_experiment_device_aggregates_read():
    return _make_aggregates_experiment(
        'device', 'read', 'device_id', _DEVICE_01,
    )


def _make_experiment_device_aggregates_write():
    return _make_aggregates_experiment(
        'device', 'write', 'device_id', _DEVICE_01,
    )


def _make_experiment_user_aggregates_read():
    return _make_aggregates_experiment('user', 'read', 'yuid', _USER_01)


def _make_experiment_user_aggregates_write():
    return _make_aggregates_experiment('user', 'write', 'yuid', _USER_01)


@pytest.mark.experiments3(**_make_experiment())
@pytest.mark.experiments3(**_make_experiment_device_aggregates_read())
@pytest.mark.experiments3(**_make_experiment_device_aggregates_write())
@pytest.mark.experiments3(**_make_experiment_user_aggregates_read())
@pytest.mark.experiments3(**_make_experiment_user_aggregates_write())
@pytest.mark.parametrize(
    'stages',
    [
        # basic test
        [
            MakeRequest(_DEVICE_01, _USER_01, [_CARD_01], []),
            MakeRequest(_DEVICE_01, _USER_01, [_CARD_02], []),
            MakeRequest(
                _DEVICE_01,
                _USER_01,
                [_CARD_03, _CARD_04],
                [
                    {
                        'id': card['id'],
                        'reason': {'key': 'test_rule1_custom_reason'},
                    }
                    for card in [_CARD_03, _CARD_04]
                ],
            ),
            CheckState(
                {
                    _DEVICE_01: {
                        'cards_ids': [
                            card['id']
                            for card in [
                                _CARD_01,
                                _CARD_02,
                                _CARD_03,
                                _CARD_04,
                            ]
                        ],
                    },
                },
                {
                    _USER_01: {
                        'cards_ids': [
                            card['id']
                            for card in [
                                _CARD_01,
                                _CARD_02,
                                _CARD_03,
                                _CARD_04,
                            ]
                        ],
                    },
                },
            ),
        ],
    ],
)
async def test_device_aggregates(taxi_uantifraud, mongodb, testpoint, stages):
    taxi_uantifraud = UantifraudCountWrapper(taxi_uantifraud, testpoint)
    for i, stage in enumerate(stages):
        await stage.run(taxi_uantifraud, mongodb, f'at stage {i}: {stage}')
