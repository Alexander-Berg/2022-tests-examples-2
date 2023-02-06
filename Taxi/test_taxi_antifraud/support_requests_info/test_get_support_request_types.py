import pytest


_REQUEST_TYPES_LIST = [
    {'tanker_id': 'some_tanker_id', 'request_type': 'some_type_id'},
    {'tanker_id': 'another_tanker_id', 'request_type': 'some_type_id1'},
]


_TRANSLATIONS = {
    'some_tanker_id': {'ru': 'Текст', 'en': 'Text'},
    'another_tanker_id': {'ru': 'Другой текст', 'en': 'Another text'},
}


@pytest.mark.translations(antifraud_orders_admin=_TRANSLATIONS)
@pytest.mark.config(AFS_SUPPORT_REQUEST_TYPE_IDS=_REQUEST_TYPES_LIST)
@pytest.mark.parametrize('locale', ['ru', 'en'])
async def test_get_support_request_types(web_app_client, locale):
    response = await web_app_client.get(
        '/v1/get_support_request_types', headers={'Accept-Language': locale},
    )
    assert response.status == 200

    expected_response = [
        {
            'request_type_name': _TRANSLATIONS[request_type_info['tanker_id']][
                locale
            ],
            'request_type_id': request_type_info['request_type'],
        }
        for request_type_info in _REQUEST_TYPES_LIST
    ]

    assert await response.json() == expected_response
