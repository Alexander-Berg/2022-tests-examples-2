# import datetime


import pytest

from tests_cargo_corp import utils


CARD_ID = 'card_id_001'
DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S+00:00'
MOCK_NOW = '2021-05-31T19:00:00+00:00'
MOCK_NOW_PLUS_MINUTE = '2021-05-31T19:01:00+00:00'
HANDLER_CARD_LIST = '/cargo-corp/internal/cargo-corp/v1/client/card/list'
HANDLER_BOUND_NTFN = '/cargo-crm/internal/cargo-crm/notification/card-bound'
# datetime.datetime.utcnow().strftime(DATETIME_FORMAT)


def get_task_kwargs(started_at=MOCK_NOW):
    return {
        'corp_client_id': utils.CORP_CLIENT_ID,
        'yandex_uid': utils.YANDEX_UID,
        'card_id': CARD_ID,
        'started_at': started_at,
    }


def _mock_handler_card_list(
        mockserver, request, card_exist=True, card_list_code=200,
):
    assert request.headers['X-B2B-Client-Id'] == utils.CORP_CLIENT_ID
    assert request.headers['X-Yandex-Uid'] == utils.YANDEX_UID
    body = None
    if card_list_code == 200:
        body = {
            'bound_cards': [
                {
                    'card_id': CARD_ID if card_exist else 'other_card',
                    'yandex_uid': utils.YANDEX_UID,
                },
            ],
        }
    if card_list_code == 404:
        body = {'message': 'Not found', 'code': 'NOT_FOUND'}
    return mockserver.make_response(status=card_list_code, json=body)


@pytest.mark.now(MOCK_NOW)
@pytest.mark.parametrize(
    'card_exist,card_list_code',
    (
        pytest.param(True, 200, id='all ok'),
        pytest.param(False, 200, id='no card'),
        pytest.param(None, 404, id='no user'),
    ),
)
async def test_stq_run(
        mockserver, stq_runner, stq, card_exist, card_list_code,
):
    @mockserver.json_handler(HANDLER_CARD_LIST)
    def mock_handler_card_list(request):
        return _mock_handler_card_list(
            mockserver, request, card_exist, card_list_code,
        )

    @mockserver.json_handler(HANDLER_BOUND_NTFN)
    def mock_handler_bound_ntfn(request):
        assert request.json == {
            'corp_client_id': utils.CORP_CLIENT_ID,
            'yandex_uid': utils.YANDEX_UID,
            'card_id': CARD_ID,
        }
        return mockserver.make_response(status=200, json={})

    await stq_runner.cargo_corp_bound_card_notifier.call(
        task_id='id', kwargs=get_task_kwargs(),
    )

    assert mock_handler_card_list.times_called == 1
    assert mock_handler_bound_ntfn.times_called == bool(card_exist)
    assert stq.cargo_corp_bound_card_notifier.times_called == (
        card_exist is False
    )


@pytest.mark.now(MOCK_NOW_PLUS_MINUTE)
async def test_stq_late_run(mockserver, stq_runner, stq):
    @mockserver.json_handler(HANDLER_CARD_LIST)
    def mock_handler_card_list(request):
        return _mock_handler_card_list(mockserver, request, card_exist=False)

    await stq_runner.cargo_corp_bound_card_notifier.call(
        task_id='id', kwargs=get_task_kwargs(),
    )

    assert mock_handler_card_list.times_called == 1
    assert stq.cargo_corp_bound_card_notifier.times_called == 0  # late


@pytest.mark.config(CARGO_CORP_BOUND_CARD_NOTIFIER_SETTINGS={'enabled': False})
async def test_stq_disabled(stq_runner, stq):
    await stq_runner.cargo_corp_bound_card_notifier.call(
        task_id='id', kwargs=get_task_kwargs(),
    )

    # handler_card_list is not mocked & no error, so it was not called
    assert stq.cargo_corp_bound_card_notifier.times_called == 0


@pytest.mark.config(
    CARGO_CORP_BOUND_CARD_NOTIFIER_SETTINGS={
        'enabled': True,
        'reschedule_immediately': True,
    },
)
async def test_stq_delayed(mockserver, stq_runner, stq):
    await stq_runner.cargo_corp_bound_card_notifier.call(
        task_id='id', kwargs=get_task_kwargs(),
    )

    # handler_card_list is not mocked & no error, so it was not called
    assert stq.cargo_corp_bound_card_notifier.times_called == 1  # ??
