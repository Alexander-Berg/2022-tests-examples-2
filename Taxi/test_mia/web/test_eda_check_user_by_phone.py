import datetime

import pytest


@pytest.mark.parametrize(
    'test',
    [
        {
            'request': {'phone': '81234567890'},
            'expected': {
                'created': '2017-01-17T20:50:03+03:00',
                'birthday': '2020-01-01',
                'first_name': 'Ivan',
                'last_name': 'Ivanov',
                'email': 'test_email_1',
                'phone': '+71234567890',
            },
        },
        {
            'request': {'phone': '+71234567890'},
            'expected': {
                'created': '2017-01-17T20:50:03+03:00',
                'birthday': '2020-01-01',
                'first_name': 'Ivan',
                'last_name': 'Ivanov',
                'email': 'test_email_1',
                'phone': '+71234567890',
            },
        },
        {
            'request': {'phone': '+71234567891'},
            'expected': {
                'phone': '+71234567891',
                'created': '2017-01-17T20:50:03+03:00',
            },
        },
    ],
)
@pytest.mark.yt(
    dyn_table_data=['yt_users_personal_phone_id.yaml', 'yt_crm_users.yaml'],
)
@pytest.mark.config(TVM_RULES=[{'dst': 'personal', 'src': 'mia'}])
async def test_eda_check_user_by_phone_200(
        taxi_mia_web, mockserver, test, yt_apply,
):
    @mockserver.json_handler('/territories/v1/countries/list')
    def _get_countries_list(request):
        return {
            'countries': [
                {
                    '_id': 'rus',
                    'national_access_code': '8',
                    'phone_code': '7',
                    'phone_max_length': 11,
                    'phone_min_length': 11,
                },
            ],
        }

    @mockserver.json_handler('/personal/v1/phones/find')
    def _personal_phones_find(request):
        personal_mapping = {
            '+71234567890': {
                'id': 'test_personal_phone_id_1',
                'value': '+71234567890',
            },
            '+71234567891': {
                'id': 'test_personal_phone_id_2',
                'value': '+71234567891',
            },
        }
        phone_doc = personal_mapping.get(request.json['value'])
        if phone_doc:
            return phone_doc
        return mockserver.make_response('Not Found', status=404)

    @mockserver.json_handler('/personal/v1/emails/retrieve')
    def _personal_phones_mock(request):
        personal_mapping = {
            'test_personal_email_id_1': {
                'id': 'test_personal_email_id_1',
                'value': 'test_email_1',
            },
        }
        email_doc = personal_mapping.get(request.json['id'])
        if email_doc:
            return email_doc
        return mockserver.make_response('Not Found', status=404)

    response = await taxi_mia_web.post(
        '/v1/eda/check_user_by_phone', test['request'],
    )
    expected = test['expected']
    assert response.status == 200

    content = await response.json()

    user_created = datetime.datetime.fromisoformat(content.get('created'))
    expected_user_created = datetime.datetime.fromisoformat(
        expected.get('created'),
    )
    assert user_created == expected_user_created
    assert content.get('birthday') == expected.get('birthday')
    assert content.get('first_name') == expected.get('first_name')
    assert content.get('last_name') == expected.get('last_name')
    assert content.get('email') == expected.get('email')
    assert content.get('phone') == expected.get('phone')


@pytest.mark.parametrize(
    'test',
    [
        {'request': {'phone': '+71234567892'}},  # absent in personal
        {'request': {'phone': '+71234567893'}},  # absent in personal_index
        {'request': {'phone': '+71234567894'}},  # absent in users
        {'request': {'phone': '+71234567895'}},  # absent in crm_users
    ],
)
@pytest.mark.yt(
    dyn_table_data=['yt_users_personal_phone_id.yaml', 'yt_crm_users.yaml'],
)
@pytest.mark.config(TVM_RULES=[{'dst': 'personal', 'src': 'mia'}])
async def test_eda_check_user_by_phone_404(
        taxi_mia_web, mockserver, test, yt_apply,
):
    @mockserver.json_handler('/territories/v1/countries/list')
    def _get_countries_list(request):
        return {
            'countries': [
                {
                    '_id': 'rus',
                    'national_access_code': '8',
                    'phone_code': '7',
                    'phone_max_length': 11,
                    'phone_min_length': 11,
                },
            ],
        }

    @mockserver.json_handler('/personal/v1/phones/find')
    def _personal_phones_find_mock(request):
        personal_mapping = {
            '+71234567893': {
                'id': 'test_personal_phone_id_3',
                'value': '+71234567893',
            },
            '+71234567894': {
                'id': 'test_personal_phone_id_4',
                'value': '+71234567894',
            },
            '+71234567895': {
                'id': 'test_personal_phone_id_5',
                'value': '+71234567895',
            },
        }
        phone_doc = personal_mapping.get(request.json['value'])
        if phone_doc:
            return phone_doc
        return mockserver.make_response('Not Found', status=404)

    @mockserver.json_handler('/personal/v1/emails/retrieve')
    def _personal_phones_find(request):
        personal_mapping = {
            'test_personal_email_id_1': {
                'id': 'test_personal_email_id_1',
                'value': 'test_email_1',
            },
        }
        email_doc = personal_mapping.get(request.json['id'])
        if email_doc:
            return email_doc
        return mockserver.make_response('Not Found', status=404)

    response = await taxi_mia_web.post(
        '/v1/eda/check_user_by_phone', test['request'],
    )
    assert response.status == 404
