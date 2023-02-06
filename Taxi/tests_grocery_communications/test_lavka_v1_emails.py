import copy

import pytest

from tests_grocery_communications import models


async def test_email_add_basic(taxi_grocery_communications, personal, pgsql):
    yandex_uid = 'yandex_uid'
    email = 'email@example.com'
    personal_email_id = 'personal_email_id'

    email_db = models.Emails(pgsql, yandex_uid=yandex_uid)

    personal.check_request(email=email, email_id=personal_email_id)

    response = await taxi_grocery_communications.post(
        '/lavka/v1/communications/v1/email/add',
        json={'email': email},
        headers={'X-Yandex-UID': yandex_uid, 'X-YaTaxi-Session': 'taxi:1234'},
    )

    assert response.status_code == 200
    assert personal.times_emails_store_called() == 1

    email_db.update()

    assert email_db.yandex_uid == yandex_uid
    assert email_db.personal_email_id == personal_email_id
    assert email_db.source == 'user'


@pytest.mark.parametrize('deleted', [False, True])
@pytest.mark.parametrize('source', ['user', 'personal', 'passport'])
async def test_email_replace_existing(
        taxi_grocery_communications, personal, pgsql, deleted, source,
):
    yandex_uid = 'yandex_uid'
    email = 'email@example.com'

    old_personal_email_id = 'old_personal_email_id'
    new_personal_email_id = 'new_personal_email_id'

    email_db = models.Emails(
        pgsql,
        yandex_uid=yandex_uid,
        personal_email_id=old_personal_email_id,
        deleted=deleted,
        source=source,
    )
    email_db.insert()

    grocery_email_id = copy.deepcopy(email_db.grocery_email_id)

    personal.check_request(email=email, email_id=new_personal_email_id)

    response = await taxi_grocery_communications.post(
        '/lavka/v1/communications/v1/email/add',
        json={'email': email},
        headers={'X-Yandex-UID': yandex_uid, 'X-YaTaxi-Session': 'taxi:1234'},
    )

    assert response.status_code == 200
    assert personal.times_emails_store_called() == 1

    email_db.update()

    assert email_db.grocery_email_id == grocery_email_id
    assert email_db.yandex_uid == yandex_uid
    assert email_db.personal_email_id == new_personal_email_id
    assert email_db.source == 'user'
    assert not email_db.deleted


async def test_email_invalid_email(
        taxi_grocery_communications, personal, pgsql,
):
    yandex_uid = 'yandex_uid'
    email = 'email@example.com'

    email_db = models.Emails(pgsql, yandex_uid=yandex_uid)

    personal.check_request(error_code=400, email=email)

    response = await taxi_grocery_communications.post(
        '/lavka/v1/communications/v1/email/add',
        json={'email': email},
        headers={'X-Yandex-UID': yandex_uid, 'X-YaTaxi-Session': 'taxi:1234'},
    )

    assert response.status_code == 400
    assert personal.times_emails_store_called() == 1

    email_db.update()

    assert email_db.yandex_uid == yandex_uid
    assert email_db.personal_email_id is None


@pytest.mark.parametrize('source', ['user', 'personal', 'passport'])
async def test_email_get_from_db(
        taxi_grocery_communications, personal, pgsql, passport, source,
):
    yandex_uid = 'yandex_uid'
    email = 'email@example.com'

    personal_email_id = 'personal_email_id'

    email_db = models.Emails(
        pgsql,
        yandex_uid=yandex_uid,
        personal_email_id=personal_email_id,
        source=source,
    )
    email_db.insert()

    personal.check_request(email=email, email_id=personal_email_id)

    response = await taxi_grocery_communications.post(
        '/lavka/v1/communications/v1/email/get',
        json={},
        headers={'X-Yandex-UID': yandex_uid, 'X-YaTaxi-Session': 'taxi:1234'},
    )

    assert response.status_code == 200
    assert personal.times_emails_retrieve_called() == 1
    assert passport.times_mock_blackbox_called() == 0

    body = response.json()
    assert body['email'] == email
    assert body['source'] == source


async def test_deleted_email_get_from_db(
        taxi_grocery_communications, personal, pgsql, passport,
):
    yandex_uid = 'yandex_uid'
    personal_email_id = 'personal_email_id'

    email_db = models.Emails(
        pgsql,
        yandex_uid=yandex_uid,
        personal_email_id=personal_email_id,
        deleted=True,
    )
    email_db.insert()

    response = await taxi_grocery_communications.post(
        '/lavka/v1/communications/v1/email/get',
        json={},
        headers={'X-Yandex-UID': yandex_uid, 'X-YaTaxi-Session': 'taxi:1234'},
    )

    assert response.status_code == 200
    assert response.json() == {}
    assert personal.times_emails_retrieve_called() == 0
    assert passport.times_mock_blackbox_called() == 0


async def test_email_update_in_db_by_bound_uid(
        taxi_grocery_communications, personal, pgsql, passport,
):
    yandex_uid = 'yandex_uid'
    bound_uid = 'bound_uid'
    email = 'email@example.com'

    personal_email_id = 'personal_email_id'
    source = 'passport'

    email_db = models.Emails(
        pgsql,
        yandex_uid=bound_uid,
        personal_email_id=personal_email_id,
        source=source,
    )
    email_db.insert()

    personal.check_request(email=email, email_id=personal_email_id)

    response = await taxi_grocery_communications.post(
        '/lavka/v1/communications/v1/email/get',
        json={},
        headers={
            'X-Yandex-UID': yandex_uid,
            'X-YaTaxi-Session': 'taxi:1234',
            'X-YaTaxi-Bound-Uids': bound_uid,
        },
    )

    assert response.status_code == 200
    assert personal.times_emails_retrieve_called() == 1
    assert passport.times_mock_blackbox_called() == 0

    body = response.json()
    assert body['email'] == email
    assert body['source'] == source

    email_db.yandex_uid = yandex_uid
    email_db.update()

    assert email_db.yandex_uid == yandex_uid
    assert email_db.personal_email_id == personal_email_id


async def test_deleted_email_update_in_db_by_bound_uid(
        taxi_grocery_communications, personal, pgsql, passport,
):
    yandex_uid = 'yandex_uid'
    bound_uid = 'bound_uid'
    email = 'email@example.com'

    personal_email_id = 'personal_email_id'

    email_db = models.Emails(
        pgsql,
        yandex_uid=bound_uid,
        personal_email_id=personal_email_id,
        deleted=True,
    )
    email_db.insert()

    personal.check_request(email=email, email_id=personal_email_id)

    response = await taxi_grocery_communications.post(
        '/lavka/v1/communications/v1/email/get',
        json={},
        headers={
            'X-Yandex-UID': yandex_uid,
            'X-YaTaxi-Session': 'taxi:1234',
            'X-YaTaxi-Bound-Uids': bound_uid,
        },
    )

    assert response.status_code == 200
    assert response.json() == {}
    assert personal.times_emails_retrieve_called() == 0
    assert passport.times_mock_blackbox_called() == 0

    email_db.yandex_uid = yandex_uid
    email_db.update()

    assert email_db.yandex_uid == yandex_uid
    assert email_db.personal_email_id == personal_email_id
    assert email_db.deleted


async def test_email_update_in_db_from_auth_context(
        taxi_grocery_communications, personal, pgsql, passport,
):
    yandex_uid = 'yandex_uid'
    email = 'email@example.com'

    personal_email_id = 'personal_email_id'
    expected_source = 'personal'

    email_db = models.Emails(
        pgsql, yandex_uid=yandex_uid, personal_email_id=personal_email_id,
    )

    personal.check_request(email=email, email_id=personal_email_id)

    response = await taxi_grocery_communications.post(
        '/lavka/v1/communications/v1/email/get',
        json={},
        headers={
            'X-Yandex-UID': yandex_uid,
            'X-YaTaxi-Session': 'taxi:1234',
            'X-YaTaxi-User': f' personal_email_id={personal_email_id}',
        },
    )

    assert response.status_code == 200
    assert personal.times_emails_retrieve_called() == 1
    assert passport.times_mock_blackbox_called() == 0

    body = response.json()
    assert body['email'] == email
    assert body['source'] == expected_source

    email_db.update()

    assert email_db.yandex_uid == yandex_uid
    assert email_db.personal_email_id == personal_email_id
    assert email_db.source == expected_source


async def test_email_update_in_db_from_passport(
        taxi_grocery_communications, personal, pgsql, passport,
):
    yandex_uid = 'yandex_uid'
    email = 'email@example.com'

    personal_email_id = 'personal_email_id'
    expected_source = 'passport'

    email_db = models.Emails(
        pgsql, yandex_uid=yandex_uid, personal_email_id=personal_email_id,
    )

    personal.check_request(email=email, email_id=personal_email_id)

    passport_email_response = copy.deepcopy(passport.response)
    passport_email_response['users'][0]['emails'][0]['attributes']['1'] = email
    passport.response = passport_email_response

    response = await taxi_grocery_communications.post(
        '/lavka/v1/communications/v1/email/get',
        json={},
        headers={'X-Yandex-UID': yandex_uid, 'X-YaTaxi-Session': 'taxi:1234'},
    )

    assert response.status_code == 200
    body = response.json()
    assert body['email'] == email
    assert body['source'] == expected_source

    assert personal.times_emails_store_called() == 1
    assert passport.times_mock_blackbox_called() == 1

    email_db.update()

    assert email_db.yandex_uid == yandex_uid
    assert email_db.personal_email_id == personal_email_id
    assert email_db.source == expected_source


async def test_email_not_found(
        taxi_grocery_communications, personal, pgsql, passport,
):
    yandex_uid = 'yandex_uid'
    email = 'email@example.com'

    personal_email_id = 'personal_email_id'

    personal.check_request(email=email, email_id=personal_email_id)

    passport_email_response = copy.deepcopy(passport.response)
    del passport_email_response['users'][0]['emails'][0]['attributes']['1']
    passport.response = passport_email_response

    response = await taxi_grocery_communications.post(
        '/lavka/v1/communications/v1/email/get',
        json={},
        headers={'X-Yandex-UID': yandex_uid, 'X-YaTaxi-Session': 'taxi:1234'},
    )

    assert response.status_code == 200
    assert response.json() == {}

    assert passport.times_mock_blackbox_called() == 1

    email_db = models.Emails(
        pgsql, yandex_uid=yandex_uid, personal_email_id=personal_email_id,
    )

    email_db.update()

    assert email_db.grocery_email_id is None
    assert email_db.personal_email_id is None


async def test_email_delete_basic(taxi_grocery_communications, pgsql):
    yandex_uid = 'yandex_uid'
    personal_email_id = 'personal_email_id'

    email_db = models.Emails(
        pgsql, yandex_uid=yandex_uid, personal_email_id=personal_email_id,
    )
    email_db.insert()

    response = await taxi_grocery_communications.post(
        '/lavka/v1/communications/v1/email/delete',
        json={},
        headers={'X-Yandex-UID': yandex_uid, 'X-YaTaxi-Session': 'taxi:1234'},
    )

    assert response.status_code == 200

    email_db.update()

    assert email_db.yandex_uid == yandex_uid
    assert email_db.personal_email_id == personal_email_id
    assert email_db.deleted


async def test_email_delete_with_subscription(
        taxi_grocery_communications, pgsql, sender, personal,
):
    yandex_uid = 'yandex_uid'
    email = 'email@example.com'
    personal_email_id = 'personal_email_id'

    sender.check_request(email=email)
    sender.request_method = 'DELETE'

    email_db = models.Emails(
        pgsql,
        yandex_uid=yandex_uid,
        personal_email_id=personal_email_id,
        maillist_slug='slug',
    )
    email_db.insert()

    personal.check_request(email=email, email_id=personal_email_id)

    response = await taxi_grocery_communications.post(
        '/lavka/v1/communications/v1/email/delete',
        json={},
        headers={'X-Yandex-UID': yandex_uid, 'X-YaTaxi-Session': 'taxi:1234'},
    )

    assert response.status_code == 200

    email_db.update()

    assert email_db.yandex_uid == yandex_uid
    assert email_db.personal_email_id == personal_email_id
    assert email_db.deleted
    assert not email_db.maillist_slug

    assert sender.times_mock_subscription_called() == 1


async def test_email_delete_sender_error(
        taxi_grocery_communications, pgsql, sender, personal,
):
    yandex_uid = 'yandex_uid'
    email = 'email@example.com'
    personal_email_id = 'personal_email_id'
    maillist_slug = 'slug'

    sender.check_request(email=email)
    sender.request_method = 'DELETE'
    sender.error_code = 400

    email_db = models.Emails(
        pgsql,
        yandex_uid=yandex_uid,
        personal_email_id=personal_email_id,
        maillist_slug=maillist_slug,
    )
    email_db.insert()

    personal.check_request(email=email, email_id=personal_email_id)

    response = await taxi_grocery_communications.post(
        '/lavka/v1/communications/v1/email/delete',
        json={},
        headers={'X-Yandex-UID': yandex_uid, 'X-YaTaxi-Session': 'taxi:1234'},
    )

    assert response.status_code == 500

    email_db.update()

    assert email_db.yandex_uid == yandex_uid
    assert email_db.personal_email_id == personal_email_id
    assert not email_db.deleted
    assert email_db.maillist_slug == maillist_slug

    assert sender.times_mock_subscription_called() == 1
