import pytest

_PHONE_ID_BLOCKED_BY_SUPPORT = '5040000000000000000FFFFF'
_PHONE_ID_BLOCKED_BY_REQUEST = '5040000004560000000FFFFF'


def _make_experiment():
    return {
        'name': 'afs_is_spammer_enabled',
        'consumers': ['afs/is_spammer'],
        'match': {
            'consumers': [{'name': 'afs/is_spammer'}],
            'predicate': {'type': 'true'},
            'enabled': True,
        },
        'clauses': [
            {'predicate': {'type': 'true'}, 'value': {'enabled': True}},
        ],
    }


@pytest.mark.parametrize(
    'input,out,code',
    [
        pytest.param(
            {
                'order_id': 'not_exists',
                'is_multiorder': True,
                'user_id': 'not_exists',
                'user_phone_id': '000000000000000000000000',
                'device_id': 'not_exists',
            },
            {'is_spammer': False},
            200,
        ),
        pytest.param(
            {
                'order_id': 'not_exists',
                'is_multiorder': False,
                'user_id': 'not_exists',
                'user_phone_id': '000000000000000000000000',
                'device_id': 'not_exists',
            },
            {'is_spammer': False},
            200,
        ),
        pytest.param(
            {
                'order_id': 'not_exists',
                'is_multiorder': True,
                'user_id': 'not_exists',
                'user_phone_id': '000000000000000000000000',
            },
            {'is_spammer': False},
            200,
        ),
        pytest.param(
            {
                'is_multiorder': True,
                'user_id': 'not_exists',
                'user_phone_id': '000000000000000000000000',
            },
            {'is_spammer': False},
            200,
        ),
        # user_phone_id is not valid mongo OID (wrong length)
        # => 400
        pytest.param(
            {
                'order_id': 'not_exists',
                'is_multiorder': True,
                'user_id': 'not_exists',
                'user_phone_id': '00000000000000000000000',
            },
            {'is_spammer': False},
            400,
        ),
        pytest.param(
            {
                'order_id': 'not_exists',
                'is_multiorder': True,
                'user_id': '200',
                'user_phone_id': '000000000000000000000000',
                'device_id': 'not_exists',
            },
            {'is_spammer': False},
            200,
        ),
        pytest.param(
            {
                'order_id': 'not_exists',
                'is_multiorder': False,
                'user_id': '200',
                'user_phone_id': '000000000000000000000000',
                'device_id': 'not_exists',
            },
            {'is_spammer': False},
            200,
        ),
        pytest.param(
            {
                'order_id': 'not_exists',
                'is_multiorder': True,
                'user_id': '400',
                'user_phone_id': '000000000000000000000000',
                'device_id': 'not_exists',
            },
            {'is_spammer': False},
            200,
        ),
        pytest.param(
            {
                'order_id': 'not_exists',
                'is_multiorder': False,
                'user_id': '400',
                'user_phone_id': '000000000000000000000000',
                'device_id': 'not_exists',
            },
            {'is_spammer': True, 'blocked_until': '2018-10-01T09:00:01+00:00'},
            200,
        ),
        pytest.param(
            {
                'order_id': 'not_exists',
                'is_multiorder': False,
                'user_id': '400',
                'user_phone_id': '502000000000000000000000',
            },
            {'is_spammer': True, 'blocked_until': '2018-10-01T09:05:39+00:00'},
            200,
        ),
        pytest.param(
            {
                'order_id': 'not_exists',
                'is_multiorder': False,
                'user_id': '400',
                'user_phone_id': '502000000000000000000000',
                'device_id': '100500',
            },
            {'is_spammer': True, 'blocked_until': '2018-10-01T09:05:40+00:00'},
            200,
        ),
        pytest.param(
            {
                'order_id': 'not_exists',
                'is_multiorder': True,
                'user_id': '500',
                'user_phone_id': '502000000000000000000000',
                'device_id': '100500',
            },
            {'is_spammer': True, 'blocked_until': '2018-10-01T09:00:07+00:00'},
            200,
        ),
        pytest.param(
            {
                'order_id': 'not_exists',
                'is_multiorder': True,
                'user_id': '500',
                'user_phone_id': '503000000000000000000000',
                'device_id': '200500',
            },
            {'is_spammer': True, 'blocked_until': '2018-10-01T09:00:09+00:00'},
            200,
        ),
        pytest.param(
            {
                'order_id': 'not_exists',
                'is_multiorder': False,
                'user_id': 'not_exists',
                'user_phone_id': '503000000000000000000000',
                'device_id': 'not_exists',
            },
            {'is_spammer': False},
            200,
        ),
        pytest.param(
            {
                'order_id': 'not_exists',
                'is_multiorder': False,
                'user_id': 'does not matter',
                'user_phone_id': _PHONE_ID_BLOCKED_BY_SUPPORT,
            },
            {'is_spammer': True, 'blocked_until': '2018-10-01T09:05:43+00:00'},
            200,
        ),
        pytest.param(
            {
                'order_id': 'not_exists',
                'is_multiorder': False,
                'user_id': 'does not matter',
                'user_phone_id': _PHONE_ID_BLOCKED_BY_SUPPORT,
            },
            {'is_spammer': True, 'blocked_until': '2018-10-01T09:05:43+00:00'},
            200,
        ),
        pytest.param(
            {
                'order_id': 'not_exists',
                'is_multiorder': False,
                'user_id': 'does not matter',
                'user_phone_id': _PHONE_ID_BLOCKED_BY_SUPPORT,
                'user_source_id': 'cargo',
            },
            {'is_spammer': True, 'blocked_until': '2018-10-01T09:05:43+00:00'},
            200,
        ),
        pytest.param(
            {
                'order_id': 'not_exists',
                'is_multiorder': False,
                'user_id': 'does not matter',
                'user_phone_id': _PHONE_ID_BLOCKED_BY_SUPPORT,
                'user_source_id': 'cargo',
            },
            {'is_spammer': False},
            200,
            marks=[pytest.mark.config(AFS_USER_SOURCES_WHITE_LIST=['cargo'])],
        ),
    ],
)
@pytest.mark.config(
    AFS_CUSTOM_USERS_STATISTICS=True, AFS_SAVE_STATISTICS_BY_USER_ID=True,
)
@pytest.mark.now('2018-10-01T09:00:00+0000')
@pytest.mark.experiments3(**_make_experiment())
def test_is_spammer_base(taxi_antifraud, input, out, code):
    for postfix in (
            '',
            '/launch',
            '/profile',
            '/orders_estimate',
            '/auth',
            '/auth_confirm',
            '/integration_orders_commit',
            '/order',
            '/order_by_sms',
            '/order_commit',
            '/order_draft',
            '/startup',
    ):
        response = taxi_antifraud.post(
            'client/user/is_spammer' + postfix, json=input,
        )
        assert response.status_code == code
        if response.status_code == 200:
            assert response.json() == out


@pytest.mark.now('2018-10-01T09:00:00+0000')
@pytest.mark.parametrize(
    'input,out',
    [
        (
            {
                'order_id': 'not_exists',
                'is_multiorder': False,
                'user_id': 'not_exists',
                'user_phone_id': '000000000000000000000000',
                'device_id': 'not_exists',
            },
            {'is_spammer': False},
        ),
        (
            {
                'order_id': 'not_exists',
                'is_multiorder': True,
                'user_id': 'not_exists',
                'user_phone_id': '000000000000000000000000',
            },
            {'is_spammer': False},
        ),
        (
            {
                'order_id': 'not_exists',
                'is_multiorder': True,
                'user_id': 'user_blocked_for_bad_driver_cancels',
                'user_phone_id': '000000000000000000000000',
                'device_id': 'not_exists',
            },
            {'is_spammer': True, 'blocked_until': '2018-10-01T09:05:01+00:00'},
        ),
        (
            {
                'order_id': 'not_exists',
                'is_multiorder': False,
                'user_id': 'user_blocked_for_bad_driver_cancels',
                'user_phone_id': '000000000000000000000000',
                'device_id': 'not_exists',
            },
            {'is_spammer': True, 'blocked_until': '2018-10-01T09:05:01+00:00'},
        ),
        (
            {
                'order_id': 'not_exists',
                'is_multiorder': False,
                'user_id': 'user_blocked_for_bad_driver_cancels',
                'user_phone_id': '502000000000000000000000',
            },
            {'is_spammer': True, 'blocked_until': '2018-10-01T09:05:39+00:00'},
        ),
        (
            {
                'order_id': 'not_exists',
                'is_multiorder': False,
                'user_id': 'user_blocked_for_bad_driver_cancels',
                'user_phone_id': '502000000000000000000000',
                'device_id': '100500',
            },
            {'is_spammer': True, 'blocked_until': '2018-10-01T09:05:40+00:00'},
        ),
    ],
)
@pytest.mark.config(
    AFS_IS_SPAMMER_BAD_DRIVER_CANCELS=True,
    AFS_SAVE_STATISTICS_BY_USER_ID=True,
    AFS_CUSTOM_USERS_STATISTICS=True,
)
@pytest.mark.experiments3(**_make_experiment())
def test_is_spammer_bad_driver_cancels(taxi_antifraud, input, out):
    for postfix in ('', '/launch', '/profile', '/orders_estimate'):
        response = taxi_antifraud.post(
            'client/user/is_spammer' + postfix, json=input,
        )
        assert response.status_code == 200
        assert response.json() == out


@pytest.mark.now('2018-10-01T09:00:00+0000')
@pytest.mark.parametrize(
    'input,out',
    [
        (
            {
                'order_id': 'not_exists',
                'is_multiorder': False,
                'user_id': '500',
                'user_phone_id': '000000000000000000000000',
            },
            {'is_spammer': False},
        ),
    ],
)
@pytest.mark.config(
    AFS_IS_SPAMMER_BAD_DRIVER_CANCELS=True, AFS_CUSTOM_USERS_STATISTICS=True,
)
@pytest.mark.experiments3(**_make_experiment())
def test_is_spammer_bad_driver_cancels_without_users(
        taxi_antifraud, input, out,
):
    for postfix in ('', '/launch', '/profile', '/orders_estimate'):
        response = taxi_antifraud.post(
            'client/user/is_spammer' + postfix, json=input,
        )
        assert response.status_code == 200
        assert response.json() == out


@pytest.mark.now('2050-10-01T09:00:00+0000')
@pytest.mark.parametrize(
    'input,out',
    [
        (
            {
                'order_id': 'not_exists',
                'is_multiorder': True,
                'user_id': 'not_exists',
                'user_phone_id': '503000000000000000000000',
            },
            {'is_spammer': False},
        ),
    ],
)
@pytest.mark.config(
    AFS_IS_SPAMMER_BAD_DRIVER_CANCELS=True, AFS_CUSTOM_USERS_STATISTICS=False,
)
@pytest.mark.experiments3(**_make_experiment())
def test_is_spammer_if_custom_statistics_does_not_save(
        taxi_antifraud, input, out,
):
    for postfix in ('', '/launch', '/profile', '/orders_estimate'):
        response = taxi_antifraud.post(
            'client/user/is_spammer' + postfix, json=input,
        )
        assert response.status_code == 200
        assert response.json() == out


@pytest.mark.now('2050-10-01T09:00:00+0000')
@pytest.mark.parametrize(
    'input,out',
    [
        (
            {
                'order_id': 'not_exists',
                'is_multiorder': False,
                'user_id': 'not_exists',
                'user_phone_id': '504000000000000000000000',
            },
            {'is_spammer': False},
        ),
    ],
)
@pytest.mark.config(
    AFS_IS_SPAMMER_BAD_DRIVER_CANCELS=True, AFS_CUSTOM_USERS_STATISTICS=True,
)
@pytest.mark.experiments3(**_make_experiment())
def test_afs_block_reason_matters(taxi_antifraud, input, out):
    for postfix in ('', '/launch', '/profile', '/orders_estimate'):
        response = taxi_antifraud.post(
            'client/user/is_spammer' + postfix, json=input,
        )
        assert response.status_code == 200
        assert response.json() == out


@pytest.mark.now('2050-10-01T09:00:00+0000')
@pytest.mark.parametrize(
    'input,out',
    [
        (
            {
                'order_id': 'not_exists',
                'is_multiorder': True,
                'user_id': 'not_exists',
                'user_phone_id': '503000000000000000000000',
            },
            {'is_spammer': False},
        ),
    ],
)
@pytest.mark.config(
    AFS_IS_SPAMMER_BAD_DRIVER_CANCELS=True,
    AFS_CUSTOM_USERS_STATISTICS=True,
    AFS_IS_SPAMMER_WHITE_LIST=['503000000000000000000000'],
)
@pytest.mark.experiments3(**_make_experiment())
def test_is_spammer_white_list(taxi_antifraud, input, out):
    for postfix in ('', '/launch', '/profile', '/orders_estimate'):
        response = taxi_antifraud.post(
            'client/user/is_spammer' + postfix, json=input,
        )
        assert response.status_code == 200
        assert response.json() == out


@pytest.mark.now('2018-01-01T09:00:00+0000')
@pytest.mark.parametrize(
    'req,resp',
    [
        (
            {
                'order_id': 'not_exists',
                'is_multiorder': False,
                'user_id': 'does not matter',
                'user_phone_id': _PHONE_ID_BLOCKED_BY_SUPPORT,
            },
            {'is_spammer': True, 'blocked_until': '2018-10-01T09:05:43+00:00'},
        ),
        (
            {
                'order_id': 'not_exists',
                'is_multiorder': False,
                'user_id': 'does not matter',
                'user_phone_id': _PHONE_ID_BLOCKED_BY_REQUEST,
            },
            {'is_spammer': True, 'blocked_until': '2018-10-01T09:05:43+00:00'},
        ),
    ],
)
@pytest.mark.config(AFS_IS_SPAMMER_SIMPLE_IMPL_ENABLED=True)
@pytest.mark.experiments3(**_make_experiment())
def test_is_spammer_simple_impl(taxi_antifraud, req, resp):
    response = taxi_antifraud.post('client/user/is_spammer/launch', json=req)
    assert response.status_code == 200
    assert response.json() == resp


@pytest.mark.now('2018-01-01T09:00:00+0000')
@pytest.mark.parametrize(
    'req,resp',
    [
        (
            {
                'order_id': 'order_id1',
                'is_multiorder': False,
                'user_id': 'user_id1',
                'user_phone_id': '504000000000000000000000',
                'user_source_id': 'user_source_id1',
                'device_id': 'device_id1',
            },
            {'is_spammer': False},
        ),
        (
            {
                'order_id': 'order_id1',
                'is_multiorder': False,
                'user_id': 'user_id1',
                'user_phone_id': '504000000000000000000001',
                'user_source_id': 'user_source_id1',
                'device_id': 'device_id1',
            },
            {'is_spammer': True, 'blocked_until': '2021-01-10T10:11:12+00:00'},
        ),
        (
            {
                'order_id': 'order_id1',
                'is_multiorder': False,
                'user_id': 'user_id1',
                'user_phone_id': '504000000000000000000000',
                'user_source_id': 'user_source_id1',
                'device_id': 'fraud_device_id1',
            },
            {'is_spammer': True, 'blocked_until': '2023-01-10T10:11:12+00:00'},
        ),
    ],
)
@pytest.mark.config(AFS_IS_SPAMMER_TO_UAFS_ENABLED=True)
@pytest.mark.experiments3(**_make_experiment())
def test_is_spammer_uafs_impl(taxi_antifraud, mockserver, req, resp):
    @mockserver.json_handler('/uantifraud/v1/user/is_blocked')
    def v1_user_is_blocked_mock(request):
        assert request.json == req
        if request.json['user_phone_id'] == '504000000000000000000001':
            return {'is_blocked': True, 'until': '2021-01-10T10:11:12+00:00'}
        elif request.json['device_id'] == 'fraud_device_id1':
            return {'is_blocked': True, 'until': '2023-01-10T10:11:12+00:00'}
        return {'is_blocked': False}

    response = taxi_antifraud.post('client/user/is_spammer', json=req)

    assert v1_user_is_blocked_mock.wait_call()

    assert response.status_code == 200
    assert response.json() == resp
