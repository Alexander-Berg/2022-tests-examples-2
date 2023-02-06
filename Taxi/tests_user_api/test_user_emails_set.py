import copy

import bson
import pytest


ENDPOINT = 'user_emails/set'


@pytest.mark.parametrize(
    'request_body',
    [
        {'email': 'foo@bar.org'},
        {'email': 'foo@bar.org', 'bound_yandex_uids': ['4004000001']},
        {'email': 'foo@bar.org', 'brand_name': 'yataxi'},
        {'email': 'foo@bar.org', 'phone_id': 'invalid_oid'},
    ],
)
async def test_user_emails_set_bad_request(taxi_user_api, request_body):
    response = await taxi_user_api.post(ENDPOINT, json=request_body)
    assert response.status_code == 400


@pytest.mark.parametrize(
    'request_data, expected_response, expected_user_email_doc',
    [
        (
            {'phone_id': '666777e7ed2c89a5e0300001'},
            {'phone_id': '666777e7ed2c89a5e0300001'},
            {'phone_id': bson.ObjectId('666777e7ed2c89a5e0300001')},
        ),
        (
            {'yandex_uid': '4004000002'},
            {'yandex_uid': '4004000002'},
            {'yandex_uid': '4004000002'},
        ),
        (
            {'yandex_uid': '4004000002', 'bound_yandex_uids': ['4004100500']},
            {'yandex_uid': '4004000002'},
            {'yandex_uid': '4004000002'},
        ),
        (
            {'yandex_uid': '4004000002', 'bound_yandex_uids': ['4004000003']},
            {
                'phone_id': '666777e7ed2c89a5e0300003',
                'yandex_uid': '4004000002',
            },
            {
                'phone_id': bson.ObjectId('666777e7ed2c89a5e0300003'),
                'yandex_uid': '4004000002',
            },
        ),
        (
            {'phone_id': '666777e7ed2c89a5e0300004'},
            {
                'phone_id': '666777e7ed2c89a5e0300004',
                'yandex_uid': '4004000004',
            },
            {
                'phone_id': bson.ObjectId('666777e7ed2c89a5e0300004'),
                'yandex_uid': '4004000004',
            },
        ),
        (
            {'yandex_uid': '4004000004'},
            {
                'phone_id': '666777e7ed2c89a5e0300004',
                'yandex_uid': '4004000004',
            },
            {
                'phone_id': bson.ObjectId('666777e7ed2c89a5e0300004'),
                'yandex_uid': '4004000004',
            },
        ),
        (
            {'yandex_uid': '4004000004', 'bound_yandex_uids': ['4004100500']},
            {
                'phone_id': '666777e7ed2c89a5e0300004',
                'yandex_uid': '4004000004',
            },
            {
                'phone_id': bson.ObjectId('666777e7ed2c89a5e0300004'),
                'yandex_uid': '4004000004',
            },
        ),
        (
            {'phone_id': '666777e7ed2c89a5e0300005'},
            {'phone_id': '666777e7ed2c89a5e0300005'},
            {'phone_id': bson.ObjectId('666777e7ed2c89a5e0300005')},
        ),
        (
            {'yandex_uid': '4004000006'},
            {'yandex_uid': '4004000006'},
            {'yandex_uid': '4004000006'},
        ),
        (
            {'phone_id': '666777e7ed2c89a5e0300001', 'brand_name': 'yataxi'},
            {'phone_id': '666777e7ed2c89a5e0300001', 'brand_name': 'yataxi'},
            {
                'phone_id': bson.ObjectId('666777e7ed2c89a5e0300001'),
                'brand_name': 'yataxi',
            },
        ),
        (
            {'phone_id': '666777e7ed2c89a5e0300007', 'brand_name': 'yataxi'},
            {'phone_id': '666777e7ed2c89a5e0300007'},
            {
                'phone_id': bson.ObjectId('666777e7ed2c89a5e0300007'),
                'brand_name': None,
            },
        ),
    ],
)
async def test_user_emails_set(
        taxi_user_api,
        mongodb,
        mockserver,
        request_data,
        expected_response,
        expected_user_email_doc,
):
    email = 'new_foo@new_bar.org'
    email_domain = 'new_bar.org'
    personal_email_id = '123456dcba77777'

    @mockserver.json_handler('/personal/v1/emails/store')
    def _emails_store(emails_store_request):
        assert emails_store_request.json == {'value': email, 'validate': True}
        return {'id': personal_email_id, 'value': email}

    request_data['email'] = email

    expected_response.update(
        {'personal_email_id': personal_email_id, 'confirmed': False},
    )

    mongo_query = copy.deepcopy(expected_user_email_doc)

    expected_user_email_doc.update(
        {
            'personal_email_id': personal_email_id,
            'email': email,
            'email_domain': email_domain,
            'confirmed': False,
        },
    )

    response = await taxi_user_api.post(ENDPOINT, json=request_data)
    assert response.status_code == 200
    assert _except_uncertains(response.json()) == expected_response
    user_email_doc = mongodb.user_emails.find_one(mongo_query)
    assert (
        _except_uncertains(user_email_doc, from_mongo=True)
        == expected_user_email_doc
    )


def _except_uncertains(doc, from_mongo=False):
    res_doc = copy.deepcopy(doc)
    for uncertain in (
            '_id' if from_mongo else 'id',
            'confirmation_code',
            'updated',
            'created',
    ):
        res_doc.pop(uncertain)
    return res_doc
