from typing import Optional

import pytest


@pytest.mark.parametrize(
    'sub_id, external_status, changed_status, check_later',
    [
        pytest.param(
            'sub_reserved',
            'CREATED',
            None,
            True,
            id='do_not_update_reserved_to_reserved',
        ),
        pytest.param(
            'sub_reserved',
            'ACTIVE',
            'active',
            False,
            id='update_reserved_to_active',
        ),
        pytest.param(
            'sub_reserved',
            'CANCELED',
            'canceled',
            False,
            id='update_reserved_to_canceled',
        ),
        pytest.param(
            'sub_active',
            'PROCESSING',
            None,
            False,
            id='do_not_update_active_to_reserved',
        ),
        pytest.param(
            'sub_active',
            'CANCELED',
            None,
            False,
            id='do_not_update_active_to_canceled',
        ),
        pytest.param(
            'sub_active',
            'ACTIVE',
            None,
            False,
            id='do_not_update_active_to_active',
        ),
        pytest.param(
            'sub_canceled',
            'PROCESSING',
            None,
            False,
            id='do_not_update_canceled_to_reserved',
        ),
        pytest.param(
            'sub_canceled',
            'ACTIVE',
            None,
            False,
            id='do_not_update_canceled_to_active',
        ),
        pytest.param(
            'sub_canceled',
            'CANCELED',
            None,
            False,
            id='do_not_update_canceled_to_canceled',
        ),
    ],
)
@pytest.mark.pgsql('maas', files=['subscriptions.sql'])
async def test_external_update(
        mockserver,
        stq_runner,
        get_subscription_by_id,
        sub_id: str,
        external_status: Optional[str],
        changed_status: Optional[str],
        check_later: bool,
):
    @mockserver.json_handler(
        r'/stq-agent/queues/api/add/(?P<queue_name>\w+)', regex=True,
    )
    def mock_stq(request, queue_name):
        pass

    @mockserver.json_handler('/vtb-maas/api/0.1/subscription/status')
    def _subscription_status(request):
        assert sub_id == request.json['service_sub_id']
        return mockserver.make_response(json={'status': external_status})

    subscription_before = get_subscription_by_id(sub_id, True)

    await stq_runner.maas_check_reserved_subscription.call(
        task_id=sub_id, args=[sub_id],
    )
    subscription_after = get_subscription_by_id(sub_id, True)

    assert subscription_after is not None
    assert _subscription_status.times_called == 1

    if changed_status:
        assert subscription_after.status == changed_status
    else:
        assert subscription_before == subscription_after

    if check_later:
        assert mock_stq.times_called == 1
    else:
        assert mock_stq.times_called == 0


SETTINGS_WITH_RESERVED_TTL = {
    'reserved_subscription_ttl_ms': 600000,
    'first_check_delay_ms': 2000,
    'second_check_delay_ms': 500,
}
SETTINGS_WITHOUT_RESERVED_TTL = {
    'first_check_delay_ms': 2000,
    'second_check_delay_ms': 500,
}


@pytest.mark.pgsql('maas', files=['subscriptions.sql'])
@pytest.mark.parametrize(
    'sub_id, changed_status, check_later',
    [
        pytest.param(
            'sub_reserved',
            None,
            True,
            marks=pytest.mark.config(
                MAAS_RESERVED_CHECK_SETTINGS=SETTINGS_WITH_RESERVED_TTL,
            ),
            id='do_not_update_reserved',
        ),
        pytest.param(
            'sub_reserved_to_cancel',
            'canceled',
            False,
            marks=pytest.mark.config(
                MAAS_RESERVED_CHECK_SETTINGS=SETTINGS_WITH_RESERVED_TTL,
            ),
            id='update_reserved_to_canceled',
        ),
        pytest.param(
            'sub_reserved_to_cancel',
            None,
            True,
            marks=pytest.mark.config(
                MAAS_RESERVED_CHECK_SETTINGS=SETTINGS_WITHOUT_RESERVED_TTL,
            ),
            id='do_not_update_reserved_if_autocanceling_disabled',
        ),
        pytest.param(
            'sub_canceled',
            None,
            False,
            id='do_not_canceled',
            marks=pytest.mark.config(
                MAAS_RESERVED_CHECK_SETTINGS=SETTINGS_WITH_RESERVED_TTL,
            ),
        ),
        pytest.param(
            'sub_active',
            None,
            False,
            marks=pytest.mark.config(
                MAAS_RESERVED_CHECK_SETTINGS=SETTINGS_WITH_RESERVED_TTL,
            ),
            id='do_not_update_active',
        ),
    ],
)
async def test_internal_update(
        mockserver,
        stq_runner,
        get_subscription_by_id,
        sub_id: str,
        changed_status: Optional[str],
        check_later: bool,
):
    @mockserver.json_handler(
        r'/stq-agent/queues/api/add/(?P<queue_name>\w+)', regex=True,
    )
    def mock_stq(request, queue_name):
        pass

    @mockserver.json_handler('/vtb-maas/api/0.1/subscription/status')
    def _subscription_status(request):
        assert sub_id == request.json['service_sub_id']
        return mockserver.make_response(
            json={
                'meta': {
                    'errorcode': 'errorcode',
                    'cause': 'cause',
                    'timestamp': '2032-01-01T12:00:27.870000+03:00',
                },
            },
        )

    subscription_before = get_subscription_by_id(sub_id, True)

    await stq_runner.maas_check_reserved_subscription.call(
        task_id=sub_id, args=[sub_id],
    )
    subscription_after = get_subscription_by_id(sub_id, True)

    assert subscription_after is not None
    assert _subscription_status.times_called == 1

    if changed_status:
        assert subscription_after.status == changed_status

        status_history = subscription_after.status_history
        assert len(status_history) == 1
        last_update = status_history[-1]
        assert last_update.new_status == changed_status
        assert last_update.reason == 'stq_reserved_selfcheck'
    else:
        assert subscription_before == subscription_after

    if check_later:
        assert mock_stq.times_called == 1
    else:
        assert mock_stq.times_called == 0
