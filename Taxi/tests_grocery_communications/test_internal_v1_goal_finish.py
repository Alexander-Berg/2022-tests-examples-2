import pytest

from tests_grocery_communications import configs
from tests_grocery_communications import consts

GROCERY_COMMUNICATIONS_GOAL_DEEPLINK_PREFIX = pytest.mark.experiments3(
    name='grocery_communications_goals_deeplink_prefix',
    consumers=['grocery-communications'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Other',
            'predicate': {'type': 'true'},
            'value': {
                'deeplink_prefix': 'yandexlavka://external?service=grocery',
            },
        },
    ],
    is_config=True,
)


@GROCERY_COMMUNICATIONS_GOAL_DEEPLINK_PREFIX
@configs.OPTIONAL_NOTIFICATIONS_SETTINGS
async def test_basic(taxi_grocery_communications, ucommunications):
    idempotency_token = 'idempotency_token'
    locale = 'ru'

    ucommunications.check_request(
        user_id='user_id',
        title='Цель достигнута test',
        text='Ваш подарок уже в приложении',
        deeplink='yandexlavka://external?service=grocery?goal=1',
        idempotency_token=idempotency_token,
        push_intent='grocery.goal_finish',
    )

    response = await taxi_grocery_communications.post(
        '/internal/communications/v1/goal/finish',
        json={
            'title_tanker_key': 'title_tanker_key',
            'text_tanker_key': 'text_tanker_key',
            'goal_id': '1',
            'taxi_user_id': 'user_id',
            'locale': locale,
            'idempotency_token': idempotency_token,
            'application': consts.APP_IPHONE,
            'push_args': {'goal_name': 'test'},
        },
    )

    assert response.status_code == 200
    assert ucommunications.times_notification_push_called() == 1


@GROCERY_COMMUNICATIONS_GOAL_DEEPLINK_PREFIX
@configs.OPTIONAL_NOTIFICATIONS_SETTINGS
async def test_eats_push(
        taxi_grocery_communications, eats_notifications, eats_eaters,
):
    idempotency_token = 'idempotency_token'
    locale = 'ru'
    eats_user_id = 'eats_user_id'
    eats_eaters.check_request(eats_id=eats_user_id)

    response = await taxi_grocery_communications.post(
        '/internal/communications/v1/goal/finish',
        json={
            'title_tanker_key': 'title_tanker_key',
            'text_tanker_key': 'text_tanker_key',
            'goal_id': '1',
            'locale': locale,
            'idempotency_token': idempotency_token,
            'application': consts.EDA_IPHONE,
            'push_args': {'goal_name': 'test'},
            'eats_user_id': eats_user_id,
        },
    )

    assert response.status_code == 200
    assert eats_eaters.times_find_by_id_called() == 1
    assert eats_notifications.times_notification_called() == 1


@GROCERY_COMMUNICATIONS_GOAL_DEEPLINK_PREFIX
@configs.OPTIONAL_NOTIFICATIONS_SETTINGS
@pytest.mark.parametrize(
    'application, error_code',
    [
        (consts.EDA_IPHONE, 'missing_eats_user_id'),
        (consts.APP_IPHONE, 'missing_taxi_user_id'),
        (consts.MARKET_IPHONE, 'missing_yandex_uid'),
    ],
)
async def test_missing_user_id(
        taxi_grocery_communications, application, error_code,
):
    idempotency_token = 'idempotency_token'
    locale = 'ru'

    response = await taxi_grocery_communications.post(
        '/internal/communications/v1/goal/finish',
        json={
            'title_tanker_key': 'title_tanker_key',
            'text_tanker_key': 'text_tanker_key',
            'goal_id': '1',
            'locale': locale,
            'idempotency_token': idempotency_token,
            'application': application,
            'push_args': {'goal_name': 'test'},
        },
    )

    assert response.status_code == 400
    assert response.json()['code'] == error_code
