import bson
import pytest

from taxi_shared_payments.stq import owner_notify
from test_taxi_shared_payments.stq import conftest


@conftest.CHECK_FETCH_USER_LOCALE
@pytest.mark.parametrize(
    'params, expected_text',
    [
        pytest.param(
            {
                'event_key': 'handle_driving',
                'account_id': 'family-0000',
                'tariff_class': 'econom',
                'cost': None,
                'currency': 'RUB',
                'locale': 'eu',
                'phone_id': bson.ObjectId('00aaaaaaaaaaaaaaaaaaaa02'),
            },
            {
                'ru': (
                    'Участник семейного аккаунта Superman '
                    'оформил заказ по тарифу Эконом.'
                ),
                'eu': 'stub for eu: Superman//Econom',
            },
            id='driving',
        ),
        pytest.param(
            {
                'event_key': 'handle_complete',
                'account_id': 'family-0000',
                'tariff_class': 'econom',
                'cost': 120.0,
                'currency': 'RUB',
                'locale': 'eu',
                'phone_id': bson.ObjectId('00aaaaaaaaaaaaaaaaaaaa02'),
            },
            {
                'ru': (
                    'Участник семейного аккаунта Superman сделал заказ '
                    'по тарифу Эконом. Стоимость 120руб.'
                ),
                'eu': 'stub for eu: Superman//Econom//120rub',
            },
            id='complete',
        ),
    ],
)
@pytest.mark.translations(
    tariff={
        'name.econom': {'ru': 'Эконом', 'eu': 'Econom'},
        'currency.rub': {'ru': 'руб.', 'eu': 'rub'},
    },
    client_messages={
        'shared_payments.handle_driving.family_owner_notify': {
            'ru': (
                'Участник семейного аккаунта %(nickname)s '
                'оформил заказ по тарифу %(tariff)s.'
            ),
            'eu': 'stub for eu: %(nickname)s//%(tariff)s',
        },
        'shared_payments.handle_complete.family_owner_notify': {
            'ru': (
                'Участник семейного аккаунта %(nickname)s сделал заказ '
                'по тарифу %(tariff)s. Стоимость %(cost)s'
            ),
            'eu': 'stub for eu: %(nickname)s//%(tariff)s//%(cost)s',
        },
    },
)
async def test_owner_notify(
        stq3_context,
        mockserver,
        mock_yt_locale_fetch,
        order_archive_mock,
        load_json,
        params,
        expected_text,
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
        assert (
            request.json['data']['payload']['msg'] == expected_text[exp_locale]
        )
        return {}

    archive_api_mock = mock_yt_locale_fetch(
        '00aaaaaaaaaaaaaaaaaaaa01', select_rows_resp, archive_api_error,
    )
    order_archive_mock.set_order_proc(order_archive_resp)

    await owner_notify.task(stq3_context, **params)

    assert _search.times_called == 1
    assert archive_api_mock.times_called == 1 + 3 * archive_api_error
    assert _push.times_called == 1
    assert order_archive_mock.order_proc_retrieve.times_called == bool(
        order_archive_resp,
    )
