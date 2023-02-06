import pytest

from taxi_shared_payments.stq import members_notify
from test_taxi_shared_payments.stq import conftest

DEFAULT_NOW = '2019-06-06T01:00:00.0'


@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            {
                'phone_id': '5bfd3733030553e658b68df5',
                'account_type': 'family',
                'locale': 'eu',
            },
            marks=pytest.mark.now(DEFAULT_NOW),
            id='ok',
        ),
    ],
)
@conftest.CHECK_FETCH_USER_LOCALE
@pytest.mark.config(
    COOP_ACCOUNT_ENABLE_PUSH=True,
    COOP_ACCOUNT_PUSH_INFO={
        'family': {
            'need_update': {
                'deeplinks': {'yango': 'test_yango', 'yataxi': 'test_yataxi'},
                'push_tanker_key': (
                    'shared_payments.family_invite_push_text_need_update'
                ),
            },
            'up_to_date': {
                'deeplinks': {'paymentmethods': 'test_paymentmethods'},
                'push_tanker_key': 'shared_payments.family_invite_push_text',
            },
        },
    },
)
@pytest.mark.translations(
    client_messages={
        'shared_payments.family_invite_push_text': {
            'ru': 'push текст',
            'eu': 'stub',
        },
        'shared_payments.family_invite_push_text_need_update': {
            'ru': 'push текст - обновись',
            'eu': 'stub',
        },
    },
)
async def test_members_notify(
        stq3_context,
        mockserver,
        mock_yt_locale_fetch,
        order_archive_mock,
        load_json,
        params,
        archive_api_error,
        select_rows_resp,
        order_archive_resp,
        exp_locale,
):
    @mockserver.json_handler('/user_api-api/users/search')
    def _search(request):
        return load_json('users.json')

    @mockserver.json_handler('/ucommunications/user/notification/push')
    def _push(request):
        assert request.json['locale'] == exp_locale

        return {}

    archive_api_mock = mock_yt_locale_fetch(
        '5bfd3733030553e658b68df5', select_rows_resp, archive_api_error,
    )
    order_archive_mock.set_order_proc(order_archive_resp)

    await members_notify.task(stq3_context, **params)

    assert _search.times_called == 1
    assert archive_api_mock.times_called == 1 + 3 * archive_api_error
    assert _push.times_called == 1
    assert order_archive_mock.order_proc_retrieve.times_called == bool(
        order_archive_resp,
    )
