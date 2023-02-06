import datetime

import pytest


@pytest.mark.parametrize(
    'test',
    [
        {
            'request': {'phone': '81234567890', 'type': 'yandex'},
            'expected': {'created': '2019-09-01T22:00:09.794000+03:00'},
        },
        {
            'request': {'phone': '+71234567890', 'type': 'yandex'},
            'expected': {'created': '2019-09-01T22:00:09.794000+03:00'},
        },
        {
            'request': {'phone': '81234567890', 'type': 'uber'},
            'expected': {'created': '2019-09-02T22:00:09.794000+03:00'},
        },
        {
            'request': {'phone': 'test_phone', 'type': 'yandex'},
            'expected': {'created': '2014-06-26T00:00:00.000000+00:00'},
        },
    ],
)
@pytest.mark.config(TVM_RULES=[{'dst': 'personal', 'src': 'mia'}])
async def test_check_user_by_phone(taxi_mia_web, mockserver, test):
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
                'id': 'personal_phone_id_1',
                'value': '+71234567890',
            },
            'test_phone': {'id': 'personal_phone_id_2', 'value': 'test_phone'},
        }
        phone_doc = personal_mapping.get(request.json['value'])
        if phone_doc:
            return phone_doc
        return mockserver.make_response('Not Found', status=404)

    @mockserver.json_handler('/user_api-api//user_phones/by_personal/retrieve')
    def _user_api_phones_retrieve(request):
        user_api_mapping = {
            'yandex': {
                'personal_phone_id_1': {
                    'id': '1',
                    'created': '2019-09-01T19:00:09.794+0000',
                },
                'personal_phone_id_2': {'id': '2'},
            },
            'uber': {
                'personal_phone_id_1': {
                    'id': '3',
                    'created': '2019-09-02T19:00:09.794+0000',
                },
            },
        }
        user_api_doc = user_api_mapping.get(request.json['type'], {}).get(
            request.json['personal_phone_id'],
        )

        if user_api_doc:
            return user_api_doc
        return mockserver.make_response('Not Found', status=404)

    response = await taxi_mia_web.post(
        '/v1/taxi/check_user_by_phone', test['request'],
    )

    assert response.status == 200

    content = await response.json()
    created = datetime.datetime.fromisoformat(content['created'])
    expected_created = datetime.datetime.fromisoformat(
        test['expected']['created'],
    )
    assert created == expected_created


@pytest.mark.parametrize('phone', ['test_phone_1', 'test_phone_2'])
@pytest.mark.config(TVM_RULES=[{'dst': 'personal', 'src': 'mia'}])
async def test_check_user_by_phone_404(taxi_mia_web, mockserver, phone):
    @mockserver.json_handler('/territories/v1/countries/list')
    def _get_countries_list(request):
        return {'countries': []}

    @mockserver.json_handler('/personal/v1/phones/find')
    def _personal_phones_find(request):
        phone_to_personal_doc = {
            'test_phone_1': {
                'id': 'personal_phone_id_1',
                'value': '+71234567890',
            },
        }
        phone_doc = phone_to_personal_doc.get(request.json['value'])
        if phone_doc:
            return phone_doc
        return mockserver.make_response('Not Found', status=404)

    @mockserver.json_handler('/user_api-api//user_phones/by_personal/retrieve')
    def _user_api_phones_retrieve(request):
        return mockserver.make_response('Not Found', status=404)

    response = await taxi_mia_web.post(
        '/v1/taxi/check_user_by_phone', {'type': 'yandex', 'phone': phone},
    )

    assert response.status == 404

    content = await response.json()
    assert content['code'] == 'user_phone_not_found'
    assert content['message'] == 'User is not found'
