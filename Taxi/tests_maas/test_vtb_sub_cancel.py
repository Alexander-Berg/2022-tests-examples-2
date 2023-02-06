import pytest


@pytest.mark.pgsql('maas', files=['subscriptions.sql'])
@pytest.mark.parametrize(
    'maas_sub_id',
    [
        pytest.param('reserved_id', id='cancel_reserved'),
        pytest.param('canceled_id', id='cancel_canceled'),
    ],
)
async def test_cancel_success(
        get_subscription_by_id, taxi_maas, maas_sub_id: str,
):

    headers = {'Accept-Language': 'ru', 'MessageUniqueId': '12345abcd'}
    vtb_cancel = '/vtb/v1/sub/cancel'
    response = await taxi_maas.post(
        vtb_cancel, headers=headers, json={'maas_sub_id': maas_sub_id},
    )
    assert response.status == 200

    subscription = get_subscription_by_id(maas_sub_id)
    assert subscription.status == 'canceled'
    if maas_sub_id == 'canceled_id':
        return
    status_history = subscription.status_history
    assert len(status_history) == 1
    updated_status = status_history[-1]
    assert updated_status.new_status == 'canceled'
    assert updated_status.reason == 'vtb_request'


@pytest.mark.pgsql('maas', files=['subscriptions.sql'])
@pytest.mark.parametrize(
    'maas_sub_id, error_code, error_cause',
    [
        pytest.param(
            'active_id', '10', 'subscription_wrong_state', id='cancel_active',
        ),
        pytest.param(
            'expired_id',
            '10',
            'subscription_wrong_state',
            id='cancel_expired',
        ),
        pytest.param(
            'active_expired_id',
            '10',
            'subscription_wrong_state',
            id='cancel_active_expired',
        ),
        pytest.param(
            'unknown_id', '40', 'subscription_not_found', id='cancel_unknown',
        ),
    ],
)
async def test_cancel_fail(
        get_subscription_by_id,
        taxi_maas,
        maas_sub_id: str,
        error_code: str,
        error_cause: str,
):

    subscription_before = get_subscription_by_id(maas_sub_id)

    headers = {'Accept-Language': 'ru', 'MessageUniqueId': '12345abcd'}
    response = await taxi_maas.post(
        '/vtb/v1/sub/cancel',
        headers=headers,
        json={'maas_sub_id': maas_sub_id},
    )
    assert response.status == 422
    response_body = response.json()
    assert response_body['errorCode'] == error_code
    assert response_body['errorCause'] == error_cause

    subscription_after = get_subscription_by_id(maas_sub_id)
    assert subscription_after == subscription_before
