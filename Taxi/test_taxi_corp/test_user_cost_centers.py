"""Есть четыре типа запросов, которые меняют или создают юзеров

POST - создание по номеру телефона (не должен существовать в базе)
PATCH - создание по номеру телефона (если не существует в базе)
PATCH - редактирование по номеру телефона (если существует в базе)
PUT - редактирование по user_id (должен существовать в базе)

Есть 7 ситуаций, которые нужно проверить (при наличии/отсутствии ЦЗ клиента):

    # в запросе передан существующий cost_centers_id
        200 OK, юзер сохраняется (создаётся) с указанным ЦЗ

    # в запросе передан несуществующий cost_centers_id
        ошибка 400, юзер не сохраняется (не создаётся)

    # в запросе передано значение ЦЗ в старом формате
        если нет ЦЗ - 200 OK, юзер сохраняется (создаётся), старый формат
        если есть ЦЗ:
            если клиента нет в конфиге CORP_COST_CENTERS_OLD_API_CLIENTS:
                - ошибка 400, юзер не создаётся
            если клиент в конфиге old_api:
                если есть подходящий ЦЗ:
                    - 200 OK, юзер сохраняется (создаётся) c найденным ЦЗ
                если нет подходящего ЦЗ:
                    - 200 OK, юзер сохраняется (создаётся) c созданным ЦЗ

Кроме того, есть два начальных варианта в базе: юзер есть или его нет.

Исходя из этого, заданы тестовые наборы TEST_PARAMS и METHOD_TEST_PARAMS,
которые комбинируются для покрытия всех возможных ситуаций.
"""
import uuid

import bson
import pytest

from taxi.util import dictionary

CORP_USER_PHONES_SUPPORTED_79 = [
    {
        'min_length': 11,
        'max_length': 11,
        'prefixes': ['+79'],
        'matches': ['^79'],
    },
]
NEW_FORMAT_OFF = pytest.mark.filldb(corp_cost_center_options='empty')
NEW_FORMAT_EXISTING_ID = dict(
    client_id='client1',
    user_id='user3',
    request_key='new_format',
    expected_user_key='new_format',
    response_code=200,
)
NEW_FORMAT_UNKNOWN_ID = dict(
    client_id='client1',
    user_id='user3',
    request_key='new_format_unknown_cc_id',
    response_key='cost_centers_not_found',
    response_code=400,
)
NEW_FORMAT_CC_TOO_LONG = dict(
    client_id='client1',
    user_id='user3',
    request_key='new_format_cc_too_long',
    response_key='cost_center_too_long',
    response_code=400,
)
OLD_FORMAT_CC_TOO_LONG = dict(
    client_id='client1',
    user_id='user3',
    request_key='old_format_cc_too_long',
    response_key='cost_center_too_long',
    response_code=400,
)
OLD_FORMAT_CHANGED = dict(
    client_id='client1',
    user_id='user3',
    request_key='old_format_cc_changed',
    expected_user_key='old_format_edited',
    response_code=200,
)
OLD_FORMAT_ERROR = dict(
    client_id='client1',
    user_id='user3',
    request_key='old_format_cc_changed',
    # expected_user_key='old_format_edited',
    response_key='old_cost_centers_not_supported',
    response_code=400,
)

PHONE = '+79291112203'
PHONE_ID = bson.ObjectId('AAAAAAAAAAAAA79291112203')
LONG_DEFAULT_CC = 'cc' * 256 + '_'  # 513 symbols

REQUESTS = {
    'new_format': {
        'fullname': 'Joe',
        'phone': PHONE,
        'cost_centers_id': 'other_cc_options_id',
        'role': {'role_id': 'role4'},
        'email': 'joe@mail.com',
        'is_active': True,
    },
    'new_format_cc_too_long': {
        'fullname': 'Joe',
        'phone': PHONE,
        'cost_centers_id': 'other_cc_options_id',
        'cost_center': LONG_DEFAULT_CC,
        'role': {'role_id': 'role4'},
        'email': 'joe@mail.com',
        'is_active': True,
    },
    'new_format_unknown_cc_id': {
        'fullname': 'Joe',
        'phone': PHONE,
        'cost_centers_id': 'unknown_cc_options_id',
        'role': {'role_id': 'role4'},
        'email': 'joe@mail.com',
        'is_active': True,
    },
    'old_format_cc_changed': {
        'fullname': 'Joe',
        'phone': PHONE,
        'cost_center': 'old_cc',
        'cost_centers': {
            'required': True,
            'format': 'select',
            'values': ['123'],
        },
        'role': {'role_id': 'role4'},
        'email': 'joe@mail.com',
        'is_active': True,
    },
    'old_format_cc_too_long': {
        'fullname': 'Joe',
        'phone': PHONE,
        'cost_center': LONG_DEFAULT_CC,
        'cost_centers': {
            'required': True,
            'format': 'select',
            'values': ['123'],
        },
        'role': {'role_id': 'role4'},
        'email': 'joe@mail.com',
        'is_active': True,
    },
}

EXPECTED_USERS = {
    'new_format': {
        'fullname': 'Joe',
        'phone_id': PHONE_ID,
        'cost_centers_id': 'other_cc_options_id',
        'role': {'role_id': 'role4'},
        'email': 'joe@mail.com',
        'is_active': True,
        'department_id': None,
    },
    'old_format_edited': {
        'fullname': 'Joe',
        'phone_id': PHONE_ID,
        'cost_center': 'old_cc',
        'cost_centers': {
            'required': True,
            'format': 'select',
            'values': ['123'],
        },
        'role': {'role_id': 'role4'},
        'email': 'joe@mail.com',
        'is_active': True,
        'department_id': None,
    },
}
OLD_FORMAT_NOT_SUPPORTED = (
    'old cost centers format no longer supported, use cost_centers_id'
)
COST_CENTERS_NOT_FOUND = 'client does not have such cost_centers_id'
LONGER_THAN_512 = 'Longer than maximum length 512.'


def not_found_errors(field):
    return [
        {
            'code': 'CLIENT_COST_CENTERS_NOT_FOUND',
            field: COST_CENTERS_NOT_FOUND,
        },
    ]


def old_format_errors(field):
    return [
        {
            'code': 'CLIENT_OLD_FORMAT_COST_CENTERS_NO_MORE_SUPPORTED',
            field: OLD_FORMAT_NOT_SUPPORTED,
        },
    ]


def _err400(text, path=None):
    code = 'REQUEST_VALIDATION_ERROR'
    details_field = {'message': text, 'code': code}
    if path is not None:
        details_field['path'] = path
    return {
        'code': code,
        'errors': [{'code': 'GENERAL', 'text': text}],
        'details': {'fields': [details_field]},
        'message': 'Invalid input',
    }


EXPECTED_RESPONSES = {
    'cost_centers_not_found': {
        'code': 'CLIENT_COST_CENTERS_NOT_FOUND',
        'errors': not_found_errors('text'),
        'message': COST_CENTERS_NOT_FOUND,
    },
    'old_cost_centers_not_supported': {
        'code': 'CLIENT_OLD_FORMAT_COST_CENTERS_NO_MORE_SUPPORTED',
        'errors': old_format_errors('text'),
        'message': OLD_FORMAT_NOT_SUPPORTED,
    },
    'cost_center_too_long': _err400(LONGER_THAN_512, ['cost_center']),
}

TEST_PARAMS = [
    # в запросе передан существующий cost_centers_id (удачно)
    pytest.param(NEW_FORMAT_EXISTING_ID, id='new-format-existing-cc-id'),
    # в запросе передан несуществующий cost_centers_id (ошибка 400)
    pytest.param(
        NEW_FORMAT_UNKNOWN_ID,
        id='new-format-unknown-cc-id',
        marks=NEW_FORMAT_OFF,
    ),
    # слишком длинный ЦЗ по умолчанию (новый формат ЦЗ) (ошибка 400)
    pytest.param(NEW_FORMAT_CC_TOO_LONG, id='new-format-cc-too-long'),
    # слишком длинный ЦЗ по умолчанию (старый формат ЦЗ) (ошибка 400)
    pytest.param(OLD_FORMAT_CC_TOO_LONG, id='old-format-cc-too-long'),
    # в запросе передан старый формат ЦЗ при наличии ЦЗ (ошибка 400)
    pytest.param(OLD_FORMAT_ERROR, id='old-format-cc-new-default'),
    # в запросе передан старый формат ЦЗ при наличии ЦЗ, клиент в конфиге
    # при этом нет подходящего ЦЗ (юзер ок, и новый ЦЗ создаётся)
    pytest.param(
        dict(OLD_FORMAT_CHANGED, auto_option_id=uuid.uuid4().hex),
        id='old-format-cc-new-default-old-api-fix-new',
        marks=pytest.mark.config(
            CORP_COST_CENTERS_OLD_API_CLIENTS=['client1'],
        ),
    ),
    # в запросе передан старый формат ЦЗ при наличии ЦЗ, клиент в конфиге
    # при этом есть подходящий ЦЗ (юзер ок, и этот ЦЗ используется)
    pytest.param(
        dict(OLD_FORMAT_CHANGED, used_option_id='old_api_cc_options_id'),
        id='old-format-cc-new-default-old-api-fix-existing',
        marks=[
            pytest.mark.config(CORP_COST_CENTERS_OLD_API_CLIENTS=['client1']),
            pytest.mark.filldb(corp_cost_center_options='api_fix'),
        ],
    ),
    # сохранение ЦЗ в старом формате при отсутствии ЦЗ (удачно)
    pytest.param(
        dict(
            OLD_FORMAT_CHANGED,
            response_key='old_format_edited',
            response_code=200,
        ),
        id='old-format-cc-edited',
        marks=NEW_FORMAT_OFF,
    ),
]

METHOD_TEST_PARAMS = [
    pytest.param('PUT', id='PUT-db-not-empty', marks=pytest.mark.filldb()),
    pytest.param('PATCH', id='PATCH-db-not-empty', marks=pytest.mark.filldb()),
    pytest.param(
        'PATCH',
        id='PATCH-db-empty',
        marks=pytest.mark.filldb(corp_users='empty'),
    ),
    pytest.param(
        'POST',
        id='POST-db-empty',
        marks=pytest.mark.filldb(corp_users='empty'),
    ),
]


@pytest.mark.parametrize(['case_params'], TEST_PARAMS)
@pytest.mark.parametrize(['method'], METHOD_TEST_PARAMS)
@pytest.mark.config(CORP_USER_PHONES_SUPPORTED=CORP_USER_PHONES_SUPPORTED_79)
async def test_put_cost_centers(
        taxi_corp_auth_client, pd_patch, db, patch, method, case_params,
):
    @patch('taxi_corp.api.common.v1_users.update.generate_user_id')
    def _generate_user_id():
        return case_params['user_id']

    if 'auto_option_id' in case_params:

        @patch(
            'taxi_corp.api.common.v1_users.update._generate_cost_centers_id',
        )
        def _generate_cost_centers_id():
            return case_params['auto_option_id']

    await taxi_corp_auth_client.server.app.phones.refresh_cache()

    request_data = REQUESTS[case_params['request_key']]
    client_id = case_params['client_id']
    user_id = case_params['user_id']
    response_code = case_params['response_code']

    expected_user_key = case_params.get('expected_user_key')
    expected_user = EXPECTED_USERS.get(expected_user_key)
    if expected_user is None:
        expected_user = await db.corp_users.find_one({'_id': user_id})

    response_keys = case_params.get('response_keys', {})
    response_key = response_keys.get(method) or case_params.get('response_key')

    expected_response = EXPECTED_RESPONSES.get(response_key)

    if method == 'PUT':
        response = await taxi_corp_auth_client.put(
            '/1.0/client/{}/user/{}'.format(client_id, user_id),
            json=request_data,
        )
        ok_response = {}
    elif method == 'PATCH':
        response = await taxi_corp_auth_client.patch(
            '/1.0/client/{}/user'.format(client_id), json=request_data,
        )
        ok_response = {'_id': user_id}
    elif method == 'POST':
        response = await taxi_corp_auth_client.post(
            '/1.0/client/{}/user'.format(client_id), json=request_data,
        )
        ok_response = {'_id': user_id}
    else:
        raise ValueError('method should be PUT or PATCH')

    response_json = await response.json()
    assert response.status == response_code, response_json

    if expected_response:
        assert response_json == expected_response
    else:
        assert response_json == ok_response

    if expected_user:
        db_item = await db.corp_users.find_one({'_id': user_id})
        for key, value in expected_user.items():
            assert db_item[key] == value

        # check old api fix
        used_option = None
        if 'auto_option_id' in case_params:
            # check that cc was created
            used_option = await db.corp_cost_center_options.find_one(
                {'_id': case_params['auto_option_id'], 'client_id': client_id},
            )
            assert used_option is not None
        elif 'used_option_id' in case_params:
            # check that cc was found
            used_option = await db.corp_cost_center_options.find_one(
                {'_id': case_params['used_option_id'], 'client_id': client_id},
            )
            assert used_option is not None

        # if any was used, check that it matches old format cost_centers
        if used_option is not None:
            fields = ['required', 'format', 'values']
            used_field = next(
                field
                for field in used_option['field_settings']
                if not field.get('hidden')
            )
            partial_field = dictionary.partial_dict(used_field, fields)
            assert partial_field == expected_user['cost_centers']
            # and check new format field
            assert db_item['cost_centers_id'] == used_option['_id']
