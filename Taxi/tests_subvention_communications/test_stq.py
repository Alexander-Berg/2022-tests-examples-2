import pytest

from . import test_common


@pytest.mark.config(
    SUBVENTION_COMMUNICATIONS_STQ={'enabled': False, 'max_retries': 10},
)
async def test_stq_disabled(
        taxi_subvention_communications, mockserver, stq, stq_runner,
):
    response = await taxi_subvention_communications.post(
        '/v1/driver_fix/block',
        json={
            'idempotency_token': 'abcd1234abcd',
            'driver_info': {'park_id': 'dbid', 'driver_profile_id': 'uuid'},
        },
    )
    assert response.status_code == 200
    assert stq.subvention_communications.times_called == 0


@pytest.mark.parametrize(
    'exec_tries, expect_fail', [(2, True), (3, False), (10, False)],
)
@pytest.mark.config(
    SUBVENTION_COMMUNICATIONS_NOTIFICATIONS=test_common.create_config(
        'driver_fix', 'fraud', ['push'],
    ),
)
@pytest.mark.config(
    SUBVENTION_COMMUNICATIONS_STQ={'enabled': True, 'max_retries': 2},
)
async def test_stq_reschedule(
        taxi_subvention_communications,
        mockserver,
        taxi_config,
        stq,
        stq_runner,
        exec_tries,
        expect_fail,
):
    @mockserver.json_handler('/communications/driver/notification/bulk-push')
    def _driver_push(request):
        return mockserver.make_response('fail', status=500)

    response = await taxi_subvention_communications.post(
        '/v1/driver_fix/block',
        json={
            'idempotency_token': 'abcd1234abcd',
            'driver_info': {'park_id': 'dbid', 'driver_profile_id': 'uuid'},
        },
    )

    assert response.status_code == 200
    next_call = stq.subvention_communications.next_call()
    await stq_runner.subvention_communications.call(
        task_id=next_call['id'],
        args=[],
        kwargs=next_call['kwargs'],
        expect_fail=expect_fail,
        exec_tries=exec_tries,
    )
    if expect_fail:
        assert _driver_push.times_called == 2
    else:
        assert _driver_push.times_called == 0
