import pytest

from tests_grocery_communications import models

MAILLIST_SLUG_RU = 'slug'

MOSCOW_LOCATION = [37.620963, 55.737982]

GROCERY_EMAIL_SUBSCRIPTION_MAILLIST_SLUG = pytest.mark.experiments3(
    name='grocery_communications_email_subscription_maillist_slug',
    consumers=['grocery-communications'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'RUS',
            'predicate': {
                'type': 'eq',
                'init': {
                    'value': 213,
                    'arg_name': 'city_id',
                    'arg_type': 'int',
                },
            },
            'value': {'maillist_slug': MAILLIST_SLUG_RU},
        },
    ],
    is_config=True,
)


@GROCERY_EMAIL_SUBSCRIPTION_MAILLIST_SLUG
async def test_email_subscribe(
        taxi_grocery_communications, pgsql, sender, personal,
):
    yandex_uid = 'yandex_uid'
    email = 'email@example.com'
    personal_email_id = 'personal_email_id'

    email_db = models.Emails(
        pgsql, yandex_uid=yandex_uid, personal_email_id=personal_email_id,
    )
    email_db.insert()

    personal.check_request(email=email, email_id=personal_email_id)

    sender.check_request(email=email, args='{}')
    sender.request_method = 'PUT'

    response = await taxi_grocery_communications.post(
        '/lavka/v1/communications/v1/email/subscribe',
        json={'location': MOSCOW_LOCATION},
        headers={'X-Yandex-UID': yandex_uid, 'X-YaTaxi-Session': 'taxi:1234'},
    )

    assert response.status_code == 200
    assert sender.times_mock_subscription_called() == 1

    email_db.update()
    assert email_db.maillist_slug == MAILLIST_SLUG_RU


@GROCERY_EMAIL_SUBSCRIPTION_MAILLIST_SLUG
async def test_email_subscribe_sender_error(
        taxi_grocery_communications, pgsql, sender, personal,
):
    yandex_uid = 'yandex_uid'
    email = 'email@example.com'
    personal_email_id = 'personal_email_id'

    email_db = models.Emails(
        pgsql, yandex_uid=yandex_uid, personal_email_id=personal_email_id,
    )
    email_db.insert()

    personal.check_request(email=email, email_id=personal_email_id)

    sender.check_request(email=email, args='{}')
    sender.request_method = 'PUT'
    sender.error_code = 400

    response = await taxi_grocery_communications.post(
        '/lavka/v1/communications/v1/email/subscribe',
        json={'location': MOSCOW_LOCATION},
        headers={'X-Yandex-UID': yandex_uid, 'X-YaTaxi-Session': 'taxi:1234'},
    )

    assert response.status_code == 400
    assert sender.times_mock_subscription_called() == 1

    email_db.update()
    assert not email_db.maillist_slug


async def test_email_subscribe_already_subscribed(
        taxi_grocery_communications, pgsql, sender, personal,
):
    yandex_uid = 'yandex_uid'
    email = 'email@example.com'
    personal_email_id = 'personal_email_id'

    email_db = models.Emails(
        pgsql,
        yandex_uid=yandex_uid,
        personal_email_id=personal_email_id,
        maillist_slug=MAILLIST_SLUG_RU,
    )
    email_db.insert()

    personal.check_request(email=email, email_id=personal_email_id)

    response = await taxi_grocery_communications.post(
        '/lavka/v1/communications/v1/email/subscribe',
        json={'location': MOSCOW_LOCATION},
        headers={'X-Yandex-UID': yandex_uid, 'X-YaTaxi-Session': 'taxi:1234'},
    )

    assert response.status_code == 200
    assert sender.times_mock_subscription_called() == 0


async def test_email_subscribe_without_email(
        taxi_grocery_communications, sender,
):
    yandex_uid = 'yandex_uid'

    response = await taxi_grocery_communications.post(
        '/lavka/v1/communications/v1/email/subscribe',
        json={'location': MOSCOW_LOCATION},
        headers={'X-Yandex-UID': yandex_uid, 'X-YaTaxi-Session': 'taxi:1234'},
    )

    assert response.status_code == 400
    assert sender.times_mock_subscription_called() == 0


async def test_email_subscribe_with_deleted_email(
        taxi_grocery_communications, sender, pgsql, personal,
):
    yandex_uid = 'yandex_uid'
    email = 'email@example.com'
    personal_email_id = 'personal_email_id'

    email_db = models.Emails(
        pgsql,
        yandex_uid=yandex_uid,
        personal_email_id=personal_email_id,
        deleted=True,
    )
    email_db.insert()

    personal.check_request(email=email, email_id=personal_email_id)

    response = await taxi_grocery_communications.post(
        '/lavka/v1/communications/v1/email/subscribe',
        json={'location': MOSCOW_LOCATION},
        headers={'X-Yandex-UID': yandex_uid, 'X-YaTaxi-Session': 'taxi:1234'},
    )

    assert response.status_code == 400
    assert sender.times_mock_subscription_called() == 0


async def test_email_unsubscribe(
        taxi_grocery_communications, pgsql, sender, personal,
):
    yandex_uid = 'yandex_uid'
    email = 'email@example.com'
    personal_email_id = 'personal_email_id'

    email_db = models.Emails(
        pgsql,
        yandex_uid=yandex_uid,
        personal_email_id=personal_email_id,
        maillist_slug=MAILLIST_SLUG_RU,
    )
    email_db.insert()

    personal.check_request(email=email, email_id=personal_email_id)

    sender.check_request(email=email)
    sender.request_method = 'DELETE'

    response = await taxi_grocery_communications.post(
        '/lavka/v1/communications/v1/email/unsubscribe',
        json={},
        headers={'X-Yandex-UID': yandex_uid, 'X-YaTaxi-Session': 'taxi:1234'},
    )

    assert response.status_code == 200
    assert sender.times_mock_subscription_called() == 1

    email_db.update()
    assert not email_db.maillist_slug


async def test_email_unsubscribe_sender_error(
        taxi_grocery_communications, pgsql, sender, personal,
):
    yandex_uid = 'yandex_uid'
    email = 'email@example.com'
    personal_email_id = 'personal_email_id'

    email_db = models.Emails(
        pgsql,
        yandex_uid=yandex_uid,
        personal_email_id=personal_email_id,
        maillist_slug=MAILLIST_SLUG_RU,
    )
    email_db.insert()

    personal.check_request(email=email, email_id=personal_email_id)

    sender.check_request(email=email)
    sender.request_method = 'DELETE'
    sender.error_code = 400

    response = await taxi_grocery_communications.post(
        '/lavka/v1/communications/v1/email/unsubscribe',
        json={},
        headers={'X-Yandex-UID': yandex_uid, 'X-YaTaxi-Session': 'taxi:1234'},
    )

    assert response.status_code == 400
    assert sender.times_mock_subscription_called() == 1

    email_db.update()
    assert email_db.maillist_slug == MAILLIST_SLUG_RU


async def test_email_unsubscribe_without_email(
        taxi_grocery_communications, sender,
):
    yandex_uid = 'yandex_uid'

    response = await taxi_grocery_communications.post(
        '/lavka/v1/communications/v1/email/unsubscribe',
        json={},
        headers={'X-Yandex-UID': yandex_uid, 'X-YaTaxi-Session': 'taxi:1234'},
    )

    assert response.status_code == 400
    assert sender.times_mock_subscription_called() == 0


async def test_email_unsubscribe_deleted_email(
        taxi_grocery_communications, pgsql, sender, personal,
):
    yandex_uid = 'yandex_uid'
    email = 'email@example.com'
    personal_email_id = 'personal_email_id'

    email_db = models.Emails(
        pgsql,
        yandex_uid=yandex_uid,
        personal_email_id=personal_email_id,
        deleted=True,
    )
    email_db.insert()

    personal.check_request(email=email, email_id=personal_email_id)

    response = await taxi_grocery_communications.post(
        '/lavka/v1/communications/v1/email/unsubscribe',
        json={},
        headers={'X-Yandex-UID': yandex_uid, 'X-YaTaxi-Session': 'taxi:1234'},
    )

    assert response.status_code == 400
    assert sender.times_mock_subscription_called() == 0


async def test_email_unsubscribe_without_subscription(
        taxi_grocery_communications, pgsql, sender, personal,
):
    yandex_uid = 'yandex_uid'
    email = 'email@example.com'
    personal_email_id = 'personal_email_id'

    email_db = models.Emails(
        pgsql, yandex_uid=yandex_uid, personal_email_id=personal_email_id,
    )
    email_db.insert()

    personal.check_request(email=email, email_id=personal_email_id)

    response = await taxi_grocery_communications.post(
        '/lavka/v1/communications/v1/email/unsubscribe',
        json={},
        headers={'X-Yandex-UID': yandex_uid, 'X-YaTaxi-Session': 'taxi:1234'},
    )

    assert response.status_code == 200
    assert sender.times_mock_subscription_called() == 0


@pytest.mark.parametrize('maillist_slug', [MAILLIST_SLUG_RU, None])
async def test_email_subscription(
        taxi_grocery_communications, pgsql, personal, maillist_slug,
):
    yandex_uid = 'yandex_uid'
    email = 'email@example.com'
    personal_email_id = 'personal_email_id'

    email_db = models.Emails(
        pgsql,
        yandex_uid=yandex_uid,
        personal_email_id=personal_email_id,
        maillist_slug=maillist_slug,
    )
    email_db.insert()

    personal.check_request(email=email, email_id=personal_email_id)

    response = await taxi_grocery_communications.post(
        '/lavka/v1/communications/v1/email/subscription',
        json={},
        headers={'X-Yandex-UID': yandex_uid, 'X-YaTaxi-Session': 'taxi:1234'},
    )

    assert response.status_code == 200
    assert response.json()['subscribed'] == bool(maillist_slug)
