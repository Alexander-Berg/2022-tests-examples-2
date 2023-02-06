import pytest

from . import models


@pytest.mark.now(models.NOW)
async def test_get_user_info(taxi_grocery_support, pgsql, now):
    now = now.replace(tzinfo=models.UTC_TZ)
    support_login = 'superSupport'
    phone_id = 'phone_id'
    yandex_uid = '838101'
    personal_phone_id = 'p_phone_id'
    comment_user = 'Mama, I killed a man'
    proper_comment = {
        'comment': comment_user,
        'support_login': support_login,
        'timestamp': now.isoformat(),
    }

    request_json = {'personal_phone_id': personal_phone_id}
    headers = {'X-Yandex-Login': support_login}

    user = models.Customer(
        pgsql,
        personal_phone_id=personal_phone_id,
        comments=[proper_comment],
        phone_id=phone_id,
        yandex_uid=yandex_uid,
    )

    user.update_db()

    response = await taxi_grocery_support.post(
        '/v1/api/compensation/get-user-info',
        json=request_json,
        headers=headers,
    )

    assert response.status_code == 200

    assert response.json() == user.json()


async def test_save_without_compensation(taxi_grocery_support):
    support_login = 'superSupport'
    personal_phone_id = 'p_phone_id'

    request_json = {'personal_phone_id': personal_phone_id}
    headers = {'X-Yandex-Login': support_login}

    response = await taxi_grocery_support.post(
        '/v1/api/compensation/get-user-info',
        json=request_json,
        headers=headers,
    )

    assert response.status_code == 200


@pytest.mark.now(models.NOW)
@pytest.mark.parametrize('phone_id', ['phone_id', None])
async def test_save_user_info(taxi_grocery_support, pgsql, now, phone_id):
    now = now.replace(tzinfo=models.UTC_TZ)
    support_login = 'superSupport'
    yandex_uid = '838101'
    personal_phone_id = 'p_phone_id'
    comment_user = 'Mama, I killed a man'
    proper_comment = {
        'comment': comment_user,
        'support_login': support_login,
        'timestamp': now.isoformat(),
    }

    request_json = {
        'personal_phone_id': personal_phone_id,
        'comment': comment_user,
        'yandex_uid': yandex_uid,
        'phone_id': phone_id,
    }
    headers = {'X-Yandex-Login': support_login}

    user = models.Customer(
        pgsql,
        personal_phone_id=personal_phone_id,
        comments=[proper_comment],
        phone_id=phone_id,
        yandex_uid=yandex_uid,
    )

    response = await taxi_grocery_support.post(
        '/v1/api/compensation/save-user-info',
        json=request_json,
        headers=headers,
    )

    assert response.status_code == 200

    user.compare_with_db()


@pytest.mark.parametrize(
    'comment_number, support_login, edited',
    [
        (1, 'superSupport', True),
        (2, 'superSupport', True),
        (1, 'fakeSupport', False),
    ],
)
async def test_correct_user_info_comment(
        taxi_grocery_support, pgsql, comment_number, support_login, edited,
):
    phone_id = 'phone_id'
    yandex_uid = '838101'
    personal_phone_id = 'p_phone_id'
    user_comments = ['first user comment', 'second user comment']
    proper_comments = [
        {
            'comment': user_comments[0],
            'support_login': 'superSupport',
            'timestamp': models.NOW,
        },
        {
            'comment': user_comments[1],
            'support_login': 'superSupport',
            'timestamp': models.NOT_NOW,
        },
    ]
    new_comment = 'new user comment'

    request_json = {
        'personal_phone_id': personal_phone_id,
        'comment': new_comment,
        'comment_number': comment_number,
        'yandex_uid': yandex_uid,
        'phone_id': phone_id,
    }
    headers = {'X-Yandex-Login': support_login}

    user = models.Customer(
        pgsql,
        personal_phone_id=personal_phone_id,
        comments=proper_comments,
        phone_id=phone_id,
        yandex_uid=yandex_uid,
    )
    user.update_db()

    response = await taxi_grocery_support.post(
        '/v1/api/compensation/save-user-info',
        json=request_json,
        headers=headers,
    )

    assert response.status_code == 200

    if edited:
        user.comments[comment_number - 1]['comment'] = new_comment
    user.compare_with_db()


@pytest.mark.now(models.NOW)
async def test_save_user_info_bad_request(taxi_grocery_support):
    support_login = 'superSupport'
    phone_id = 'phone_id'
    personal_phone_id = 'p_phone_id'
    comment_user = 'Mama, I killed a man'

    request_json = {
        'personal_phone_id': personal_phone_id,
        'comment': comment_user,
        'phone_id': phone_id,
    }
    headers = {'X-Yandex-Login': support_login}

    response = await taxi_grocery_support.post(
        '/v1/api/compensation/save-user-info',
        json=request_json,
        headers=headers,
    )

    assert response.status_code == 400  # no yandex_uid
