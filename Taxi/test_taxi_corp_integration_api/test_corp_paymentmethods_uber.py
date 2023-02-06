# pylint: disable=invalid-name
# pylint: disable=redefined-outer-name
# pylint: disable=too-many-lines

import pytest

from test_taxi_corp_integration_api import utils


EXP3_CONSUMER = 'corp-integration-api/v1/corp_paymentmethods'
UBER_EXP_NAME = 'yandex_corp_payment_uber'

PHONE_ID_IN_DB = '0123456789abcdef01234001'
PHONE_ID = '0123456789abcdef01234002'
DEFAULT_ZONE_NAME = 'moscow'
DEFAULT_PERSONAL_PHONE_ID = 'test_personal_phone_id'


def get_request(class_='uberblack', personal_phone_id=None, phone_id=PHONE_ID):
    result = {
        'identity': {'uid': 'test_yandex_uid', 'phone_id': phone_id},
        'class': class_,
        'order_price': '400',
        'source': {'app': 'uber_application'},
    }
    if personal_phone_id is not None:
        result['identity']['personal_phone_id'] = personal_phone_id
    return result


def get_response_method(can_order=True):
    result = {
        'can_order': can_order,
        'classes_available': ['econom', 'vip', 'start', 'uberblack'],
        'client_comment': 'comment',
        'cost_center': 'cost center',
        'cost_center_fields': [],
        'cost_centers': {'format': 'mixed', 'required': False, 'values': []},
        'currency': 'RUB',
        'description': 'Осталось 5000 из 5000 руб.',
        'hide_user_cost': False,
        'id': 'corp-test_client_id',
        'label': 'Yandex.Uber team',
        'type': 'corp',
        'user_id': 'test_corp_user_id',
        'zone_available': True,
    }
    if not can_order:
        result['order_disable_reason'] = ' недоступны'

    return result


def make_uber_exp_value(enabled=False):
    return {'enabled': enabled}


def make_uber_exp_args(
        phone_id=PHONE_ID, corp_source_application='uber_application',
):
    return [
        {'name': 'phone_id', 'type': 'string', 'value': phone_id},
        {
            'name': 'corp_source_application',
            'type': 'string',
            'value': corp_source_application,
        },
    ]


def make_uber_exp_mark_kwargs():
    return {
        'consumer': EXP3_CONSUMER,
        'experiment_name': UBER_EXP_NAME,
        'args': make_uber_exp_args(),
        'value': make_uber_exp_value(enabled=True),
    }


def make_uber_exp_mark():
    return pytest.mark.client_experiments3(**make_uber_exp_mark_kwargs())


@pytest.mark.skip()
@pytest.mark.parametrize(
    'is_uber_exp_enabled',
    [
        pytest.param(False, id='uber exp off'),
        pytest.param(True, marks=[make_uber_exp_mark()], id='uber exp on'),
    ],
)
@pytest.mark.parametrize(
    'personal_phone_id',
    [
        pytest.param(None, id='No personal_phone_id in request'),
        pytest.param(DEFAULT_PERSONAL_PHONE_ID),
    ],
)
@pytest.mark.parametrize(
    'is_phone_id_in_db,phone_id',
    [
        pytest.param(False, PHONE_ID, id='some phone_id'),
        pytest.param(
            True,
            PHONE_ID_IN_DB,
            id='phone_id is from the corp payment method',
        ),
    ],
)
@pytest.mark.translations(**utils.TRANSLATIONS)
@pytest.mark.now('2019-11-02T10:02:03+0300')
async def test_ok(
        exp3_decoupling_mock,
        mockserver,
        mock_billing,
        taxi_corp_integration_api,
        is_uber_exp_enabled,
        personal_phone_id,
        is_phone_id_in_db,
        phone_id,
):
    are_methods_expected = is_phone_id_in_db or (
        is_uber_exp_enabled and personal_phone_id is not None
    )
    expected_methods = [get_response_method()] if are_methods_expected else []

    request = get_request(
        personal_phone_id=personal_phone_id, phone_id=phone_id,
    )

    response = await utils.request_corp_paymentmethods(
        taxi_corp_integration_api,
        mockserver,
        request,
        DEFAULT_ZONE_NAME,
        None,
    )

    assert response.status == 200

    data = await response.json()
    assert data == {'methods': expected_methods}
