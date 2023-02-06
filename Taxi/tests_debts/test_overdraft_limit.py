import json

import pytest

from tests_debts import common


async def test_overdraft_limit_4xx(taxi_debts):
    response = await taxi_debts.post('v1/overdraft/limit')
    assert response.status_code == 400

    response = await taxi_debts.post('v1/overdraft/limit', json={})
    assert response.status_code == 400


@pytest.mark.pgsql('debts', files=['taxi_order_debts.sql'])
@pytest.mark.config(TVM_SERVICES=common.TVM_SERVICES)
async def test_overdraft_limit_no_debts(taxi_debts, mock_antifraud_limit):
    mock_antifraud_limit.value = 50

    response = await taxi_debts.post(
        'v1/overdraft/limit',
        json={
            'personal_phone_id': 'personal_phone_id1',
            'phone_id': 'phone_id_10',
        },
    )
    assert response.status_code == 200


@pytest.mark.pgsql('debts', files=['taxi_order_debts.sql'])
@pytest.mark.config(TVM_SERVICES=common.TVM_SERVICES)
async def test_overdraft_limit_with_debts(taxi_debts, mock_antifraud_limit):
    mock_antifraud_limit.value = 50

    response = await taxi_debts.post(
        'v1/overdraft/limit',
        json={
            'personal_phone_id': 'personal_phone_id2',
            'phone_id': 'phone_id_1',
        },
    )
    assert response.status_code == 200


@pytest.mark.pgsql('debts', files=['taxi_order_debts.sql'])
@pytest.mark.config(TVM_SERVICES=common.TVM_SERVICES)
async def test_overdraft_limit_personal_phone_id(
        taxi_debts, mock_antifraud_limit,
):
    mock_antifraud_limit.value = 50

    response = await taxi_debts.post(
        'v1/overdraft/limit',
        json={
            'personal_phone_id': 'personal_id_xxx',
            'phone_id': 'phone_id_1',
        },
    )
    assert response.status_code == 200


@pytest.mark.pgsql('debts', files=['taxi_order_debts.sql'])
@pytest.mark.config(TVM_SERVICES=common.TVM_SERVICES)
@pytest.mark.parametrize(
    'code,response,expected_code',
    [
        (200, '', 500),
        (200, {}, 500),
        (200, {'value': 50, 'currency': 'RUB'}, 200),
        (400, '', 500),
        (404, {}, 200),
        (500, {}, 200),
    ],
)
async def test_commit_overdraft_servererror(
        taxi_debts, mockserver, code, response, expected_code,
):
    @mockserver.handler('/antifraud/v1/overdraft/limit')
    def _mock_limit(request):
        resp = response if isinstance(response, str) else json.dumps(response)
        return mockserver.make_response(resp, code)

    response = await taxi_debts.post(
        'v1/overdraft/limit',
        json={
            'personal_phone_id': 'personal_phone_id2',
            'phone_id': 'phone_id_1',
            'brand': 'yataxi',
        },
    )
    assert response.status_code == expected_code


@pytest.mark.parametrize('force_request', [True, False, None])
@pytest.mark.pgsql('debts', files=['taxi_order_debts.sql'])
@pytest.mark.config(TVM_SERVICES=common.TVM_SERVICES)
async def test_overdraft_limit_force_request(
        taxi_debts, mock_antifraud_limit, force_request,
):
    payload = {
        'personal_phone_id': 'personal_phone_id1',
        'phone_id': 'phone_id_10',
    }
    if force_request is not None:
        payload['force_overdraft_request'] = force_request
    response = await taxi_debts.post('v1/overdraft/limit', json=payload)

    if force_request:
        assert mock_antifraud_limit.last_request == {
            'personal_phone_id': 'personal_phone_id1',
            'debts': [],
            'currency': 'RUB',
        }
    else:
        assert mock_antifraud_limit.last_request is None

    assert response.status_code == 200
