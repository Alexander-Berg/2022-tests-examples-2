import pytest

from tests_grocery_communications import configs


PERSONAL_PHONE_ID = '1273o182j3e9w'
UNAUTHORIZED_USER = 'z1'
AUTHORIZED_USER = '1'

OPENED_DEPOT_PUSH_INTENT = 'grocery.depot_opened'

GROCERY_COMMUNICATIONS_OPEN_DEPOT_PUSH_DEEPLINK = pytest.mark.experiments3(
    name='grocery_communications_open_depot_push_deeplink',
    consumers=['grocery-communications'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Other',
            'predicate': {'type': 'true'},
            'value': {
                'eda_iphone': 'eda.yandex://external?service=grocery',
                'eda_android': 'eda.yandex://external?service=grocery',
                'taxi_iphone': 'yandextaxi://external?service=grocery',
                'lavka_iphone': 'yandexlavka://external?service=grocery',
                'taxi_android': 'yandextaxi://external?service=grocery',
                'yango_iphone': 'yandexyango://external?service=grocery',
                'lavka_android': 'yandexlavka://external?service=grocery',
                'yango_android': 'yandexyango://external?service=grocery',
                'yangodeli_iphone': 'yangodeli://external?service=grocery',
                'yangodeli_android': 'yangodeli://external?service=grocery',
            },
        },
    ],
    is_config=True,
)


@configs.GROCERY_COMMUNICATIONS_INTENTS_CONFIG
@configs.OPTIONAL_NOTIFICATIONS_SETTINGS
async def test_unauthorized_user_request(
        taxi_grocery_communications, ucommunications, grocery_depots,
):
    depot_id = '123'
    item_id = f'{depot_id}123'
    batch_number = 1
    user_id = 'z1'
    application = 'lavka_iphone'
    op_key = 'depot-opened'
    locale = 'ru'

    grocery_depots.add_depot(depot_test_id=int(depot_id), auto_add_zone=False)

    ucommunications.check_request(
        title='depot_opened_title',
        text='depot_opened_text',
        locale=locale,
        push_intent=OPENED_DEPOT_PUSH_INTENT,
        user_id=user_id,
        idempotency_token=f'{op_key}{item_id}{batch_number}{user_id}',
        application='lavka_iphone',
        deeplink='yandexlavka://external?service=grocery',
    )

    response = await taxi_grocery_communications.post(
        '/processing/v1/depot/opened/notification',
        json={
            'depot_id': depot_id,
            'batch_number': batch_number,
            'item_id': item_id,
            'users': [
                {
                    'taxi_user_id': user_id,
                    'locale': locale,
                    'application': application,
                },
            ],
        },
    )

    assert response.status_code == 200

    assert ucommunications.times_bulk_push_called() == 0
    assert ucommunications.times_unauthorized_push_called() == 1


@configs.GROCERY_COMMUNICATIONS_INTENTS_CONFIG
async def test_authorized_user_request(
        taxi_grocery_communications, ucommunications, grocery_depots,
):
    depot_id = '123'
    item_id = f'{depot_id}123'
    batch_number = 1
    user_id = '1'
    application = 'doesnt_matter'
    op_key = 'depot-opened'
    locale = 'ru'

    grocery_depots.add_depot(depot_test_id=int(depot_id), auto_add_zone=False)

    ucommunications.check_request(
        title='depot_opened_title',
        text='depot_opened_text',
        push_intent=OPENED_DEPOT_PUSH_INTENT,
        idempotency_token=f'{op_key}{item_id}{batch_number}{locale}',
        recipients=[{'user_id': user_id, 'locale': locale}],
    )

    response = await taxi_grocery_communications.post(
        '/processing/v1/depot/opened/notification',
        json={
            'depot_id': depot_id,
            'batch_number': batch_number,
            'item_id': item_id,
            'users': [
                {
                    'taxi_user_id': user_id,
                    'locale': locale,
                    'application': application,
                },
            ],
        },
    )

    assert response.status_code == 200

    assert ucommunications.times_bulk_push_called() == 1
    assert ucommunications.times_unauthorized_push_called() == 0


@pytest.mark.parametrize(
    'item_id, batch_number, enabled',
    [
        ('666777-123', 1, False),
        ('666777-12', 5, False),
        ('666777-12', 1, True),
    ],
)
@configs.GROCERY_COMMUNICATIONS_INTENTS_CONFIG
@configs.GROCERY_NEED_TO_HANDLE_OPENED_DEPOT_OFF
async def test_off_by_config(
        taxi_grocery_communications,
        ucommunications,
        grocery_depots,
        item_id,
        batch_number,
        enabled,
):
    depot_id = '666777'
    user_id = '1'
    application = 'doesnt_matter'
    op_key = 'depot-opened'
    locale = 'ru'

    grocery_depots.add_depot(depot_test_id=int(depot_id), auto_add_zone=False)

    ucommunications.check_request(
        title='depot_opened_title',
        text='depot_opened_text',
        push_intent=OPENED_DEPOT_PUSH_INTENT,
        idempotency_token=f'{op_key}{item_id}{batch_number}{locale}',
        recipients=[{'user_id': user_id, 'locale': locale}],
    )

    response = await taxi_grocery_communications.post(
        '/processing/v1/depot/opened/notification',
        json={
            'depot_id': depot_id,
            'batch_number': batch_number,
            'item_id': item_id,
            'users': [
                {
                    'taxi_user_id': user_id,
                    'locale': locale,
                    'application': application,
                },
            ],
        },
    )

    assert response.status_code == 200

    assert ucommunications.times_bulk_push_called() == (1 if enabled else 0)


@configs.GROCERY_COMMUNICATIONS_INTENTS_CONFIG
@configs.OPTIONAL_NOTIFICATIONS_SETTINGS
async def test_number_of_calls(
        taxi_grocery_communications, ucommunications, grocery_depots,
):
    depot_id = '123'
    grocery_depots.add_depot(depot_test_id=int(depot_id), auto_add_zone=False)

    response = await taxi_grocery_communications.post(
        '/processing/v1/depot/opened/notification',
        json={
            'depot_id': depot_id,
            'batch_number': 5,
            'item_id': 'lavka_proccesing_depot',
            'users': [
                {'taxi_user_id': '1', 'locale': 'ru', 'application': 'any'},
                {'taxi_user_id': '2', 'locale': 'ru', 'application': 'any'},
                {'taxi_user_id': '3', 'locale': 'is', 'application': 'any'},
                {'taxi_user_id': '4', 'locale': 'fr', 'application': 'any'},
                {'taxi_user_id': '5', 'locale': 'is', 'application': 'any'},
                {'taxi_user_id': 'z1', 'locale': 'ca', 'application': 'any'},
                {'taxi_user_id': 'z2', 'locale': 'ca', 'application': 'any'},
            ],
        },
    )

    assert response.status_code == 200

    assert ucommunications.times_bulk_push_called() == 3
    assert ucommunications.times_unauthorized_push_called() == 2


@pytest.mark.parametrize(
    'ucommunications_code,depot_opened_response',
    [(400, 500), (404, 500), (429, 500), (502, 500)],
)
@configs.GROCERY_COMMUNICATIONS_INTENTS_CONFIG
async def test_default_error_from_ucommunication(
        taxi_grocery_communications,
        ucommunications,
        ucommunications_code,
        depot_opened_response,
):
    ucommunications.set_error_code(ucommunications_code)

    for user_id in ['1', 'z1']:
        response = await taxi_grocery_communications.post(
            '/processing/v1/depot/opened/notification',
            json={
                'depot_id': 'test',
                'batch_number': 1,
                'item_id': 'test',
                'users': [
                    {
                        'taxi_user_id': user_id,
                        'locale': 'test',
                        'application': 'test',
                    },
                ],
            },
        )
        assert response.status_code == depot_opened_response

    response = await taxi_grocery_communications.post(
        '/processing/v1/depot/opened/notification',
        json={
            'depot_id': 'test',
            'batch_number': 1,
            'item_id': 'test',
            'users': [
                {
                    'taxi_user_id': '1',
                    'locale': 'test',
                    'application': 'test',
                    'personal_phone_id': PERSONAL_PHONE_ID,
                },
            ],
        },
    )
    assert response.status_code == depot_opened_response


@pytest.mark.disable_config_check
@pytest.mark.config(GROCERY_COMMUNICATIONS_OPEN_DEPOT_PUSH_INFO=True)
@configs.GROCERY_COMMUNICATIONS_OPEN_DEPOT_NOTIFICATION_INFO
@configs.GROCERY_COMMUNICATIONS_INTENTS_CONFIG
@configs.OPTIONAL_NOTIFICATIONS_SETTINGS
@pytest.mark.parametrize(
    'country_iso3, text, title',
    [
        pytest.param(
            'RUS', 'Лавка открылась!', 'Сделайте первый заказ!', id='RUS',
        ),
        pytest.param(
            'FRA',
            'Le magasin est ouvert!',
            'Faites la première commande!',
            id='FRA',
        ),
        pytest.param(
            'ISR', 'החנות נפתחה!', 'בצע את ההזמנה הראשונה!', id='ISR',
        ),
        pytest.param(
            '', 'The shop has opened!', 'Make your first order!', id='',
        ),
    ],
)
async def test_open_depot_notification_info_config(
        taxi_grocery_communications,
        ucommunications,
        grocery_depots,
        country_iso3,
        text,
        title,
):
    depot_id = '123'
    item_id = f'{depot_id}123'
    batch_number = 1
    user_id = 'z1'
    application = 'lavka_iphone'
    op_key = 'depot-opened'
    locale = 'ru'
    # locale = 'ru, en, is, fr?'

    grocery_depots.add_depot(
        depot_test_id=int(depot_id),
        country_iso3=country_iso3,
        auto_add_zone=False,
    )

    ucommunications.check_request(
        title=title,
        text=text,
        locale=locale,
        push_intent=OPENED_DEPOT_PUSH_INTENT,
        user_id=user_id,
        idempotency_token=f'{op_key}{item_id}{batch_number}{user_id}',
        application='lavka_iphone',
        deeplink='yandexlavka://external?service=grocery',
    )

    response = await taxi_grocery_communications.post(
        '/processing/v1/depot/opened/notification',
        json={
            'depot_id': depot_id,
            'batch_number': batch_number,
            'item_id': item_id,
            'users': [
                {
                    'taxi_user_id': user_id,
                    'locale': locale,
                    'application': application,
                },
            ],
        },
    )

    assert response.status_code == 200

    assert ucommunications.times_bulk_push_called() == 0
    assert ucommunications.times_unauthorized_push_called() == 1


@pytest.mark.parametrize('user_id', [UNAUTHORIZED_USER, AUTHORIZED_USER])
@configs.GROCERY_COMMUNICATIONS_INTENTS_CONFIG
@configs.GROCERY_COMMUNICATIONS_OPEN_DEPOT_NOTIFICATION_INFO
async def test_opened_depot_sms_notification(
        taxi_grocery_communications, ucommunications, grocery_depots, user_id,
):
    depot_id = '123'
    item_id = f'{depot_id}123'
    batch_number = 1
    application = 'lavka_iphone'
    locale = 'ru'
    op_key = 'depot-opened'

    grocery_depots.add_depot(
        depot_test_id=int(depot_id), country_iso3='RUS', auto_add_zone=False,
    )

    ucommunications.check_request(
        text='Лавка открылась',
        phone_id=PERSONAL_PHONE_ID,
        sms_intent=configs.OPENED_DEPOT_NOTIFICATION_INTENT,
        idempotency_token=f'{op_key}{item_id}{batch_number}{user_id}',
    )

    response = await taxi_grocery_communications.post(
        '/processing/v1/depot/opened/notification',
        json={
            'depot_id': depot_id,
            'batch_number': batch_number,
            'item_id': item_id,
            'users': [
                {
                    'taxi_user_id': user_id,
                    'locale': locale,
                    'application': application,
                    'personal_phone_id': PERSONAL_PHONE_ID,
                },
            ],
        },
    )

    assert response.status_code == 200
    assert ucommunications.times_bulk_push_called() == 0
    assert ucommunications.times_unauthorized_push_called() == 0
    assert ucommunications.times_user_sms_send_called() == 1


@configs.GROCERY_COMMUNICATIONS_INTENTS_CONFIG
@configs.OPTIONAL_NOTIFICATIONS_SETTINGS
async def test_opened_depot_several_types(
        taxi_grocery_communications, ucommunications, grocery_depots,
):
    depot_id = '123'
    item_id = f'{depot_id}123'
    batch_number = 1
    application = 'lavka_iphone'
    locale = 'ru'

    grocery_depots.add_depot(
        depot_test_id=int(depot_id), country_iso3='RUS', auto_add_zone=False,
    )

    response = await taxi_grocery_communications.post(
        '/processing/v1/depot/opened/notification',
        json={
            'depot_id': depot_id,
            'batch_number': batch_number,
            'item_id': item_id,
            'users': [
                {
                    'taxi_user_id': AUTHORIZED_USER,
                    'locale': locale,
                    'application': application,
                    'personal_phone_id': PERSONAL_PHONE_ID,
                },
                {
                    'taxi_user_id': UNAUTHORIZED_USER,
                    'locale': locale,
                    'application': application,
                    'personal_phone_id': PERSONAL_PHONE_ID,
                },
                {
                    'taxi_user_id': AUTHORIZED_USER,
                    'locale': locale,
                    'application': application,
                },
                {
                    'taxi_user_id': UNAUTHORIZED_USER,
                    'locale': locale,
                    'application': application,
                },
            ],
        },
    )

    assert response.status_code == 200
    assert ucommunications.times_bulk_push_called() == 1
    assert ucommunications.times_unauthorized_push_called() == 1
    assert ucommunications.times_user_sms_send_called() == 2


@configs.GROCERY_COMMUNICATIONS_INTENTS_CONFIG
@GROCERY_COMMUNICATIONS_OPEN_DEPOT_PUSH_DEEPLINK
@configs.GROCERY_COMMUNICATIONS_OPEN_DEPOT_NOTIFICATION_INFO
@configs.OPTIONAL_NOTIFICATIONS_SETTINGS
async def test_opened_depot_deeplinks(
        taxi_grocery_communications, ucommunications, grocery_depots,
):
    depot_id = '123'
    item_id = f'{depot_id}123'
    batch_number = 1
    application = 'lavka_iphone'
    locale = 'ru'

    grocery_depots.add_depot(
        depot_test_id=int(depot_id), country_iso3='RUS', auto_add_zone=False,
    )

    ucommunications.check_request(
        text='Лавка открылась!',
        title='Сделайте первый заказ!',
        recipients=[
            {
                'user_id': AUTHORIZED_USER,
                'locale': 'ru',
                'data': {
                    'payload': {
                        'deeplink': 'yandexlavka://external?service=grocery',
                    },
                },
            },
        ],
        idempotency_token='depot-opened{}1231ru'.format(depot_id),
        push_intent=OPENED_DEPOT_PUSH_INTENT,
    )

    response = await taxi_grocery_communications.post(
        '/processing/v1/depot/opened/notification',
        json={
            'depot_id': depot_id,
            'batch_number': batch_number,
            'item_id': item_id,
            'users': [
                {
                    'taxi_user_id': AUTHORIZED_USER,
                    'locale': locale,
                    'application': application,
                },
            ],
        },
    )

    assert response.status_code == 200
    assert ucommunications.times_bulk_push_called() == 1

    ucommunications.check_request(
        text='Лавка открылась!',
        title='Сделайте первый заказ!',
        locale=locale,
        application=application,
        user_id=UNAUTHORIZED_USER,
        push_intent=OPENED_DEPOT_PUSH_INTENT,
        idempotency_token='depot-opened{}1231z1'.format(depot_id),
        deeplink='yandexlavka://external?service=grocery',
    )

    response = await taxi_grocery_communications.post(
        '/processing/v1/depot/opened/notification',
        json={
            'depot_id': depot_id,
            'batch_number': batch_number,
            'item_id': item_id,
            'users': [
                {
                    'taxi_user_id': UNAUTHORIZED_USER,
                    'locale': locale,
                    'application': application,
                },
            ],
        },
    )

    assert response.status_code == 200
    assert ucommunications.times_unauthorized_push_called() == 1
