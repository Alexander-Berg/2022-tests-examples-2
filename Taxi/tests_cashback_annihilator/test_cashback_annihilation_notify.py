import json

import pytest


@pytest.fixture(autouse=True)
def _mock_ucommunications(mockserver):
    @mockserver.json_handler('/ucommunications/user/notification/push')
    def _mock(request):
        body = request.json
        assert body['intent'] == 'cashback.annihilation'
        assert body['data']['repack']['apns']['aps']['alert'] == {
            'body': 'Баллы сгорят 120',
            'title': 'Привет',
        }
        return {}

    return _mock


@pytest.fixture(autouse=True)
def _mock_user_state(mockserver):
    @mockserver.handler('/fast-prices-notify/billing/user/state')
    async def _mock(request, *args, **kwargs):
        return mockserver.make_response(
            json.dumps({'activeIntervals': [], 'uid': 12345567}),
        )

    return _mock


@pytest.mark.pgsql('cashback_annihilator', files=['balances.sql'])
async def test_empty(
        stq_runner, _mock_plus_wallet, _mock_ucommunications, _mock_user_state,
):
    await stq_runner.cashback_annihilation_notify.call(
        task_id='task_id', args=['5555555'], expect_fail=False,
    )

    assert not _mock_user_state.has_calls
    assert not _mock_ucommunications.has_calls


@pytest.mark.experiments3(filename='exp3_push.json')
@pytest.mark.translations(
    client_messages={
        'cashback_annihilator.push_title': {'ru': 'Привет'},
        'cashback_annihilator.push_text': {
            'ru': 'Баллы сгорят %(annihilation_sum)s',
        },
    },
)
@pytest.mark.pgsql('cashback_annihilator', files=['balances.sql'])
async def test_happy_path(
        stq_runner,
        mockserver,
        _mock_plus_wallet,
        _mock_ucommunications,
        _mock_user_state,
):
    await stq_runner.cashback_annihilation_notify.call(
        task_id='task_id', args=['1111111'], expect_fail=False,
    )

    assert _mock_user_state.has_calls
    assert _mock_ucommunications.has_calls


@pytest.mark.pgsql('cashback_annihilator', files=['balances.sql'])
async def test_with_plus(
        stq_runner, mockserver, _mock_plus_wallet, _mock_ucommunications,
):
    @mockserver.handler('/fast-prices-notify/billing/user/state')
    async def _mock_user_state(request, *args, **kwargs):
        return mockserver.make_response(
            json.dumps(
                {
                    'activeIntervals': [
                        {
                            'featureBundle': 'new-plus',
                            'end': '2021-01-07T18:21:26Z',
                            'orderType': 'native-auto-subscription',
                        },
                    ],
                    'uid': 12345567,
                },
            ),
        )

    await stq_runner.cashback_annihilation_notify.call(
        task_id='task_id', args=['1111111'], expect_fail=False,
    )

    assert _mock_user_state.has_calls
    assert not _mock_ucommunications.has_calls
