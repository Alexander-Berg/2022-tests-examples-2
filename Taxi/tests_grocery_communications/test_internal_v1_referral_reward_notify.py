import pytest

from tests_grocery_communications import configs
from tests_grocery_communications import consts

GROCERY_COMMUNICATIONS_REFERRAL_REWARD_PUSH = pytest.mark.experiments3(
    name='grocery_communications_referral_reward_push',
    consumers=['grocery-communications'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Other',
            'predicate': {'type': 'true'},
            'value': {
                'push_text': 'push_text',
                'push_title': 'push_title',
                'intent': 'grocery_referral_reward',
                'deeplink': 'yandexlavka://external?service=grocery',
            },
        },
    ],
    is_config=True,
)


@GROCERY_COMMUNICATIONS_REFERRAL_REWARD_PUSH
@pytest.mark.parametrize(
    'application', [consts.APP_IPHONE, consts.MARKET_ANDROID],
)
@configs.OPTIONAL_NOTIFICATIONS_SETTINGS
async def test_basic(
        taxi_grocery_communications,
        ucommunications,
        grocery_market_gw,
        application,
):
    idempotency_token = 'idempotency_token'
    yandex_uid = 'user_yandex_uid'
    locale = 'ru'
    country = 'RUS'

    ucommunications.check_request(
        user_id='user_id',
        text='Ваш промокод уже в приложении',
        title='Ваш реферал использовал промокод',
        deeplink='yandexlavka://external?service=grocery',
        idempotency_token=idempotency_token,
        push_intent='grocery.referral',
    )

    grocery_market_gw.set_v1_notify(
        expected_json={
            'yandex_uid': yandex_uid,
            'translated_push_title': 'Ваш реферал использовал промокод',
            'translated_push_message': 'Ваш промокод уже в приложении',
            'idempotency_token': idempotency_token,
            'push_deeplink': 'yandexlavka://external?service=grocery',
        },
        response_code=200,
    )

    response = await taxi_grocery_communications.post(
        '/internal/communications/v1/referral-reward-notify',
        json={
            'yandex_uid': yandex_uid,
            'taxi_user_id': 'user_id',
            'application': application,
            'locale': locale,
            'country': country,
            'idempotency_token': idempotency_token,
        },
    )

    assert response.status_code == 200

    if application == 'lavka_android':
        assert ucommunications.times_notification_push_called() == 1
        assert grocery_market_gw.times_gw_v1_notify_called() == 0
    if application == 'mobileweb_market_android':
        assert ucommunications.times_notification_push_called() == 0
        assert grocery_market_gw.times_gw_v1_notify_called() == 1


@GROCERY_COMMUNICATIONS_REFERRAL_REWARD_PUSH
@pytest.mark.parametrize(
    'application, code', [(consts.APP_WEB, 200), (consts.EDA_IPHONE, 400)],
)
async def test_error_codes_by_application(
        taxi_grocery_communications,
        eats_notifications,
        ucommunications,
        application,
        code,
):
    locale = 'ru'
    country = 'RUS'
    idempotency_token = 'idempotency_token'

    response = await taxi_grocery_communications.post(
        '/internal/communications/v1/referral-reward-notify',
        json={
            'taxi_user_id': 'user_id',
            'application': application,
            'locale': locale,
            'country': country,
            'idempotency_token': idempotency_token,
        },
    )

    assert response.status_code == code
    assert ucommunications.times_notification_push_called() == 0
    assert eats_notifications.times_notification_called() == 0


@GROCERY_COMMUNICATIONS_REFERRAL_REWARD_PUSH
@pytest.mark.parametrize(
    'err_code, expected_code', [(400, 400), (404, 400), (409, 409)],
)
@configs.OPTIONAL_NOTIFICATIONS_SETTINGS
async def test_error_codes_from_ucommunications(
        taxi_grocery_communications, ucommunications, err_code, expected_code,
):
    locale = 'ru'
    country = 'RUS'
    idempotency_token = 'idempotency_token'

    ucommunications.set_error_code(code=err_code)

    response = await taxi_grocery_communications.post(
        '/internal/communications/v1/referral-reward-notify',
        json={
            'taxi_user_id': 'user_id',
            'application': consts.APP_IPHONE,
            'locale': locale,
            'country': country,
            'idempotency_token': idempotency_token,
        },
    )

    assert response.status_code == expected_code
    assert ucommunications.times_notification_push_called() == 1


@GROCERY_COMMUNICATIONS_REFERRAL_REWARD_PUSH
async def test_error_codes_from_market_gw(
        taxi_grocery_communications, grocery_market_gw,
):
    idempotency_token = 'idempotency_token'
    locale = 'ru'
    country = 'RUS'
    yandex_uid = 'user_yandex_uid'

    grocery_market_gw.set_v1_notify(
        expected_json={
            'yandex_uid': yandex_uid,
            'translated_push_title': 'Ваш реферал использовал промокод',
            'translated_push_message': 'Ваш промокод уже в приложении',
            'idempotency_token': idempotency_token,
            'push_deeplink': 'yandexlavka://external?service=grocery',
        },
        response_code=406,
    )

    response = await taxi_grocery_communications.post(
        '/internal/communications/v1/referral-reward-notify',
        json={
            'yandex_uid': yandex_uid,
            'taxi_user_id': 'user_id',
            'application': consts.MARKET_ANDROID,
            'locale': locale,
            'country': country,
            'idempotency_token': idempotency_token,
        },
    )

    assert response.status_code == 200
    assert grocery_market_gw.times_gw_v1_notify_called() == 1
