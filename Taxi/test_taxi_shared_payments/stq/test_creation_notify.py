import pytest

from taxi_shared_payments.stq import creation_notify
from test_taxi_shared_payments.stq import conftest

PHONE_ID = '5bfd3733030553e658b68df5'
LAST_USER_ID = 'fab8f16fbbf31f8b1ee47de958397682'
USER_LOCALE = 'ru'

NOTIFICATION_PARAMS = {
    'enabled_applications': ['light_business'],
    'intent': 'test_intent',
    'sms_text': {
        'keyset': 'notify',
        'key': 'business_account.creation.sms',
        'params': {'link': 'http://testlink.com'},
    },
    'notification': {
        'deeplink': (
            'yandextaxi://coopaccount?type=business&screen=payment_method'
        ),
        'title': {
            'keyset': 'notify',
            'key': 'business_account.creation.push.title',
        },
        'text': {
            'keyset': 'notify',
            'key': 'business_account.creation.push.text',
        },
    },
    'sender': 'taxi',
}

EXPECTED_UCOMMUNICATIONS_REQUEST = {
    'intent': NOTIFICATION_PARAMS['intent'],
    'user_id': LAST_USER_ID,
    'text': NOTIFICATION_PARAMS['sms_text'],
    'notification': NOTIFICATION_PARAMS['notification'],
    'sender': NOTIFICATION_PARAMS['sender'],
}


@conftest.CHECK_FETCH_USER_LOCALE
@pytest.mark.parametrize('params', [{'phone_id': PHONE_ID, 'locale': 'eu'}])
@pytest.mark.parametrize(
    'application,app_enabled',
    [('light_business', True), ('android', False), ('iphone', False)],
)
@pytest.mark.config(
    COOP_ACCOUNT_CREATED_NOTIFICATION_PARAMS=[NOTIFICATION_PARAMS],
)
async def test_creation_notify(
        stq3_context,
        mockserver,
        mock_yt_locale_fetch,
        order_archive_mock,
        load_json,
        params,
        application,
        app_enabled,
        archive_api_error,
        select_rows_resp,
        order_archive_resp,
        exp_locale,
):
    completed_params = {'application': application, **params}

    @mockserver.json_handler('/user_api-api/users/search')
    def _search(request):
        return load_json('users.json')

    @mockserver.json_handler('/ucommunications/user/sms/send')
    def _push(request):
        assert request.json == {
            **EXPECTED_UCOMMUNICATIONS_REQUEST,
            **{'locale': exp_locale},
        }
        return {'code': 'code', 'message': 'message'}

    archive_api_mock = mock_yt_locale_fetch(
        PHONE_ID, select_rows_resp, archive_api_error,
    )
    order_archive_mock.set_order_proc(order_archive_resp)

    await creation_notify.task(stq3_context, **completed_params)

    calls_count = 1 if app_enabled else 0
    assert _search.times_called == calls_count
    assert _push.times_called == calls_count
    assert (
        archive_api_mock.times_called
        == (1 + 3 * archive_api_error) * app_enabled
    )
    assert (
        order_archive_mock.order_proc_retrieve.times_called
        == bool(order_archive_resp) * app_enabled
    )
