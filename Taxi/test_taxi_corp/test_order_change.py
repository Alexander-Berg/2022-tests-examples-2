import pytest

from test_taxi_corp import request_util as util

OLD_COST_CENTER = {'cost_center': 'some cost center'}
OLD_COST_CENTER_EMPTY = {'cost_center': ''}
NEW_COST_CENTER_VALUES = {
    'cost_centers': [
        {
            'id': 'cost_center',
            'title': 'Центр затрат',
            'value': 'командировка',
        },
    ],
}
BOTH_COST_CENTERS = dict(OLD_COST_CENTER, **NEW_COST_CENTER_VALUES)
BOTH_COST_CENTERS_WITH_EMPTY = dict(
    OLD_COST_CENTER_EMPTY, **NEW_COST_CENTER_VALUES,
)
OLD_CONFIG = pytest.param(
    False,
    marks=[pytest.mark.config(COST_CENTERS_CHECK_VIA_NEW_HANDLE=False)],
    id='via-paymentmethods',
)
NEW_CONFIG = pytest.param(
    True,
    marks=[pytest.mark.config(COST_CENTERS_CHECK_VIA_NEW_HANDLE=True)],
    id='via-cost-centers-check',
)


def mock_corp_paymentmethods(
        patch, post_content, client_id, order_disable_reason=None,
):
    api_module = (
        'taxi_corp.clients.' 'corp_integration_api.CorpIntegrationApiClient'
    )

    @patch(f'{api_module}.corp_paymentmethods')
    async def _corp_paymentmethods(*args, **kwargs):
        util.check_interim_request(
            post_content, kwargs, util.CHANGE_COST_CENTER_FIELDS,
        )
        method = {
            'id': 'corp-{}'.format(client_id),
            'can_order': True,
            'zone_available': True,
        }
        if order_disable_reason is not None:
            method['can_order'] = False
            method['order_disable_reason'] = order_disable_reason
        return {'methods': [method]}

    @patch(f'{api_module}.cost_centers_check_by_user_id')
    async def _cost_centers_check(*args, **kwargs):
        util.check_interim_request(
            post_content, kwargs, util.CHANGE_COST_CENTER_FIELDS,
        )
        if order_disable_reason is not None:
            return {'can_use': False, 'reason': order_disable_reason}
        return {'can_use': True}

    return _corp_paymentmethods, _cost_centers_check


@pytest.mark.parametrize(
    'passport_mock, order_id',
    [('client2', 'order1'), ('client1', 'order2'), ('client1', 'order3')],
    indirect=['passport_mock'],
)
@pytest.mark.parametrize(
    'request_data',
    [
        OLD_COST_CENTER,
        OLD_COST_CENTER_EMPTY,
        NEW_COST_CENTER_VALUES,
        BOTH_COST_CENTERS,
        BOTH_COST_CENTERS_WITH_EMPTY,
    ],
)
@pytest.mark.parametrize(
    argnames=['is_new_check'], argvalues=[OLD_CONFIG, NEW_CONFIG],
)
async def test_single_put(
        taxi_corp_real_auth_client,
        patch,
        db,
        passport_mock,
        order_id,
        request_data,
        is_new_check,
):
    api_mocks = mock_corp_paymentmethods(patch, request_data, passport_mock)
    response = await taxi_corp_real_auth_client.put(
        '/1.0/client/{}/order/{}/change'.format(passport_mock, order_id),
        json=request_data,
    )

    response_json = await response.json()
    assert response.status == 200, response_json
    assert response_json == {}
    db_item = await db.corp_orders.find_one({'_id': order_id})
    for key, value in request_data.items():
        assert db_item[key]['cabinet'] == value, f'{key} must be {value}'

    _check_mocks(api_mocks, is_new_check)


@pytest.mark.parametrize(
    'passport_mock', ['client2'], indirect=['passport_mock'],
)
@pytest.mark.parametrize(
    'client_id, order_id, put_content, order_disable_reason, expected_code',
    [
        ('client2', 'non_existing', OLD_COST_CENTER, None, 404),
        ('non_existing', 'order1', OLD_COST_CENTER, None, 404),
        ('client2', 'non_existing', NEW_COST_CENTER_VALUES, None, 404),
        ('non_existing', 'order1', NEW_COST_CENTER_VALUES, None, 404),
        ('client2', 'order1', {}, None, 400),
        ('client2', 'order1', OLD_COST_CENTER, 'wrong CC text', 406),
        ('client2', 'order1', NEW_COST_CENTER_VALUES, 'required CC text', 406),
    ],
)
@pytest.mark.parametrize(
    argnames=['is_new_check'], argvalues=[OLD_CONFIG, NEW_CONFIG],
)
async def test_single_put_fail(
        taxi_corp_real_auth_client,
        patch,
        db,
        passport_mock,
        client_id,
        order_id,
        put_content,
        order_disable_reason,
        expected_code,
        is_new_check,
):
    old_order = await db.corp_orders.find_one({'_id': order_id})
    api_mocks = mock_corp_paymentmethods(
        patch, put_content, client_id, order_disable_reason,
    )
    response = await taxi_corp_real_auth_client.put(
        '/1.0/client/{}/order/{}/change'.format(client_id, order_id),
        json=put_content,
    )
    response_json = await response.json()
    assert response.status == expected_code, response_json
    if order_disable_reason is not None:
        expected_error = {
            'text': order_disable_reason,
            'code': 'COST_CENTERS_CANNOT_CHANGE',
        }
        assert response_json['errors'] == [expected_error]

        _check_mocks(api_mocks, is_new_check)

    new_order = await db.corp_orders.find_one({'_id': order_id})
    assert old_order == new_order


def _check_mocks(mocks, is_new_check):
    pm_mock, ccc_mock = mocks
    if is_new_check:
        assert len(ccc_mock.calls) == 1
        assert not pm_mock.calls
    else:
        assert len(pm_mock.calls) == 1
        assert not ccc_mock.calls
