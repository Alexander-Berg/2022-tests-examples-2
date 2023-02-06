import datetime

import pytest


def _str_to_datetime(
        time_str: str, with_ms: bool = False,
) -> datetime.datetime:
    if with_ms:
        return datetime.datetime.strptime(
            time_str + '00', '%Y-%m-%d %H:%M:%S.%f%z',
        )
    return datetime.datetime.strptime(time_str + '00', '%Y-%m-%d %H:%M:%S%z')


@pytest.mark.pgsql('maas', files=['subscriptions.sql'])
@pytest.mark.parametrize(
    'maas_sub_id, sub_status_called',
    [
        pytest.param('reserved_id', True, id='activate_reserved'),
        pytest.param(
            'reserved_id',
            False,
            marks=pytest.mark.config(MAAS_ACTIVATION_ANTIFROD_ENABLED=False),
            id='activate_reserved_without_antifrod',
        ),
        pytest.param('active_id', True, id='activate_active'),
    ],
)
async def test_activate_success(
        mockserver,
        get_subscription_by_id,
        taxi_maas,
        maas_sub_id: str,
        sub_status_called: bool,
):
    @mockserver.json_handler('/vtb-maas/api/0.1/subscription/status')
    def _subscription_status(request):
        assert maas_sub_id == request.json['service_sub_id']
        return mockserver.make_response(json={'status': 'ACTIVE'})

    headers = {'Accept-Language': 'ru', 'MessageUniqueId': '12345abcd'}

    start_time = datetime.datetime.now().astimezone()
    vtb_activate = '/vtb/v1/sub/activate'
    response = await taxi_maas.post(
        vtb_activate, headers=headers, json={'maas_sub_id': maas_sub_id},
    )
    assert response.status == 200

    subscription = get_subscription_by_id(maas_sub_id)
    active = 'active'
    assert subscription.status == active

    status_history = subscription.status_history
    if maas_sub_id != 'active_id':
        assert len(status_history) == 1
        status_update = status_history[0]
        assert status_update.new_status == active
        assert (
            start_time
            <= _str_to_datetime(status_update.updated_at, with_ms=True)
            <= datetime.datetime.now().astimezone()
        )
        assert status_update.reason == 'vtb_request'

    if sub_status_called:
        assert _subscription_status.times_called == 1
    else:
        assert _subscription_status.times_called == 0


@pytest.mark.pgsql('maas', files=['subscriptions.sql'])
@pytest.mark.parametrize(
    'maas_sub_id, error_code, error_cause, external_status',
    [
        pytest.param(
            'canceled_id',
            '10',
            'subscription_wrong_state',
            'ACTIVE',
            id='activate_canceled',
        ),
        pytest.param(
            'expired_id',
            '10',
            'subscription_wrong_state',
            'ACTIVE',
            id='activate_expired',
        ),
        pytest.param(
            'active_expired_id',
            '10',
            'subscription_wrong_state',
            'ACTIVE',
            id='activate_active_expired',
        ),
        pytest.param(
            'reserved_id',
            '10',
            'subscription_wrong_state',
            'PROCESSING',
            id='wrong_external_state',
        ),
        pytest.param(
            'unknown_id',
            '40',
            'subscription_not_found',
            'ACTIVE',
            id='activate_unknown',
        ),
    ],
)
async def test_activate_fail(
        mockserver,
        get_subscription_by_id,
        taxi_maas,
        maas_sub_id: str,
        error_code: str,
        error_cause: str,
        external_status: str,
):
    @mockserver.json_handler('/vtb-maas/api/0.1/subscription/status')
    def _subscription_status(request):
        assert maas_sub_id == request.json['service_sub_id']
        return mockserver.make_response(json={'status': external_status})

    subscription_before = get_subscription_by_id(maas_sub_id)

    headers = {'Accept-Language': 'ru', 'MessageUniqueId': '12345abcd'}
    response = await taxi_maas.post(
        '/vtb/v1/sub/activate',
        headers=headers,
        json={'maas_sub_id': maas_sub_id},
    )
    assert response.status == 422
    response_body = response.json()
    assert response_body['errorCode'] == error_code
    assert response_body['errorCause'] == error_cause

    subscription_after = get_subscription_by_id(maas_sub_id)
    assert subscription_after == subscription_before
    assert _subscription_status.times_called == 1
