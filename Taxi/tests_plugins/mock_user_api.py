import pymongo
import pytest


def format_time(dt):
    iso = dt.isoformat()
    if dt.utcoffset() is None:
        iso += 'Z'
    return iso


USERS_FIELDS = {
    'uber_id': str,
    'zuser_id': str,
    'created': format_time,
    'updated': format_time,
    'phone_id': str,
    'authorized': bool,
    'application': str,
    'application_version': str,
    'yandex_staff': bool,
    'yandex_uid': str,
    'yandex_uid_type': str,
    'yandex_uuid': str,
    'apns_token': str,
    'gcm_token': str,
    'device_id': str,
    'token_only': bool,
    'has_ya_plus': bool,
    'has_cashback_plus': bool,
    'sourceid': str,
    'dont_ask_name': bool,
    'metrica_device_id': str,
    'given_name': str,
}


class UserApiContext:
    def __init__(self):
        self.user_phones_times_called = 0
        self.users_get_times_called = 0


@pytest.fixture
def mock_user_api(mockserver, db, now):
    user_api_context = UserApiContext()

    @mockserver.json_handler('/user-api/user_phones')
    def _mock_user_phones(request):
        user_api_context.user_phones_times_called += 1
        data = request.json

        type = data['type']
        type_query = {'$in': [type, None]} if type == 'yandex' else type

        phone_doc = db.user_phones.find_one_and_update(
            {'phone': data['phone'], 'type': type_query},
            {
                '$setOnInsert': {
                    'phone': data['phone'],
                    'type': data['type'],
                    'personal_phone_id': 'personal_phone_id',
                    'created': now,
                    'updated': now,
                    'phone_hash': 'hash',
                    'phone_salt': '12!34567dhsakjh218d9iasjd9121923',
                },
            },
            upsert=True,
            return_document=pymongo.collection.ReturnDocument.AFTER,
        )

        stat_doc = phone_doc.get('stat', {})

        stats = {
            'big_first_discounts': 0,
            'complete': 0,
            'complete_card': 0,
            'complete_apple': 0,
            'complete_google': 0,
        }
        stats['complete_apple'] = stat_doc.get('complete_apple', 0)
        stats['complete'] = stat_doc.get('complete', 0)

        created = stat_doc.get('created', now)
        updated = stat_doc.get('updated', now)
        blocked_till = phone_doc.get('blocked_till', None)

        response = {
            'id': str(phone_doc['_id']),
            'phone': phone_doc['phone'],
            'type': phone_doc.get('type', 'yandex'),
            'personal_phone_id': 'personal_phone_id',
            'created': format_time(created),
            'updated': format_time(updated),
            'stat': stats,
            'is_loyal': False,
            'is_yandex_staff': False,
            'is_taxi_staff': False,
        }

        if blocked_till is not None:
            response['blocked_till'] = format_time(blocked_till)

        return response

    @mockserver.json_handler('/user-api/users/get')
    def _mock_users_get(request):
        user_api_context.users_get_times_called += 1

        if request.json.get('lookup_uber', False):
            query = {'_id': request.json['id']}
        else:
            query = {
                '$or': [
                    {'_id': request.json['id']},
                    {'uber_id': request.json['id']},
                ],
            }

        request_fields = request.json.get('fields')
        user_doc = db.users.find_one(query, request_fields)

        if user_doc is None:
            return mockserver.make_response('', 404)

        response = {'id': user_doc['_id']}
        for field, converter in USERS_FIELDS.items():
            if field in user_doc:
                response[field] = converter(user_doc.get(field))

        return response

    return user_api_context
