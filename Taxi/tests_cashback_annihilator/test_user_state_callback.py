import pytest

BASIC_STQ_KWARGS = {'yandex_uid': '1111111'}


@pytest.mark.now('2022-06-10T00:00:00.00Z')
@pytest.mark.parametrize(
    'blackbox_fail, blackbox_not_found, user_has_plus',
    [
        pytest.param(False, False, True, id='happy_path'),
        pytest.param(False, False, False, id='has_not_plus'),
        pytest.param(True, False, True, id='blackbox_fail'),
        pytest.param(False, True, True, id='blackbox_404'),
    ],
)
@pytest.mark.pgsql('cashback_annihilator', files=['balances.sql'])
async def test_user_state_callback(
        stq_runner,
        stq,
        mockserver,
        blackbox_fail,
        blackbox_not_found,
        user_has_plus,
):
    @mockserver.json_handler('/blackbox')
    async def _mock_blackbox(request):
        assert request.args['method'] == 'userinfo'

        attributes = {}
        if user_has_plus:
            attributes.update({'1015': '1', '1025': '1'})

        if blackbox_fail:
            return mockserver.make_response(status=500)

        json_response = {
            'users': [
                {
                    'aliases': {'1': 'portal-account'},
                    'attributes': attributes,
                    'uid': {'value': '1111111'},
                },
            ],
        }

        if blackbox_not_found:
            json_response = {'id': '1111111', 'uid': {}}

        return mockserver.make_response(status=200, json=json_response)

    await stq_runner.cashback_annihilator_process_user_state_change.call(
        task_id='task_id', kwargs=BASIC_STQ_KWARGS, expect_fail=False,
    )

    stq_times_called = (
        1
        if (not blackbox_fail and not blackbox_not_found and user_has_plus)
        else 0
    )

    assert (
        stq.cashback_set_pending_annihilation.times_called == stq_times_called
    )
