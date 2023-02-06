import datetime

import pytest

from agent import const

TEST_MOCK_DATETIME_NOW = datetime.datetime(
    2020, 12, 31, 21, 0, tzinfo=datetime.timezone.utc,
)

PROJECT_SETTINGS = {
    'default': {'enable_chatterbox': False},
    'test_taxi_project': {
        'enable_chatterbox': False,
        'wfm_effrat_domain': 'mediaservices',
        'piecework_tariff': 'call-taxi-unified',
        'main_permission': 'user_calltaxi',
    },
}

TRANSLATE = {
    const.ERROR_ACCESS_DENIED: {'ru': 'Ошибка доступа', 'en': 'Access denied'},
    'shop_permissions_conflict': {
        'ru': 'Более 1 пермишена для магазина',
        'en': 'More then 1 permission for shop',
    },
    'subproduct_not_found': {
        'ru': 'Подтовар отсутствует',
        'en': 'Subproduct is missing',
    },
    'address_not_found': {
        'ru': 'Адресс отсутствует',
        'en': 'Address is missing',
    },
    const.KEY_ERROR_MAPPING_PERMISSIONS_PROJECT: {
        'ru': (
            'Пермишен {permission} отсутствует в маппинге '
            'AGENT_PROJECT_SETTINGS'
        ),
        'en': (
            'Permission {permission} is missing from mapping '
            'AGENT_PROJECT_SETTINGS'
        ),
    },
}

GOOD_HEADERS: dict = {
    'X-Yandex-Login': 'mikh-vasily',
    'Accept-Language': 'ru-ru',
}
BAD_HEADERS: dict = {'X-Yandex-Login': 'webalex', 'Accept-Language': 'en-en'}
BAD_HEADERS2: dict = {
    'X-Yandex-Login': 'test_user',
    'Accept-Language': 'en-en',
}
BAD_HEADERS3: dict = {
    'X-Yandex-Login': 'test_user1',
    'Accept-Language': 'en-en',
}


DATA = {'subproduct_id': 1}
ADDRESS_ID_DATA = {'subproduct_id': 1, 'address_id': 1}
ADDRESS_DATA = {
    'subproduct_id': 1,
    'address': {
        'postcode': '111111',
        'country': 'ru',
        'city': 'Москва',
        'street': '1-й Краcногвардейский пр-д',
        'house': '21',
    },
}
ADDRESS_DATA2 = {
    'subproduct_id': 1,
    'address': {
        'postcode': '111111',
        'country': 'ru',
        'city': 'Москва',
        'street': '1-й Краcногвардейский пр-д',
        'house': '21',
        'building': '1',
        'flat': '15',
        'login': 'mikh-vasily',
    },
}


@pytest.mark.config(AGENT_PROJECT_SETTINGS=PROJECT_SETTINGS)
@pytest.mark.now('2021-01-01T00:00:00+0')
@pytest.mark.translations(agent=TRANSLATE)
@pytest.mark.parametrize(
    'input_data, headers, status, response_content, expected_address',
    [
        (DATA, GOOD_HEADERS, 200, {}, None),
        (ADDRESS_ID_DATA, GOOD_HEADERS, 200, {}, {'id': 1}),
        (
            ADDRESS_DATA,
            GOOD_HEADERS,
            200,
            {},
            {
                'id': 2,
                'type': const.USER_ADDRESS_TYPE,
                'created': TEST_MOCK_DATETIME_NOW,
                'updated': TEST_MOCK_DATETIME_NOW,
                'postcode': '111111',
                'country': 'ru',
                'city': 'Москва',
                'street': '1-й Краcногвардейский пр-д',
                'house': '21',
                'building': None,
                'flat': None,
                'login': 'mikh-vasily',
            },
        ),
        (
            ADDRESS_DATA2,
            GOOD_HEADERS,
            200,
            {},
            {
                'id': 2,
                'type': const.USER_ADDRESS_TYPE,
                'created': TEST_MOCK_DATETIME_NOW,
                'updated': TEST_MOCK_DATETIME_NOW,
                'postcode': '111111',
                'country': 'ru',
                'city': 'Москва',
                'street': '1-й Краcногвардейский пр-д',
                'house': '21',
                'building': '1',
                'flat': '15',
                'login': 'mikh-vasily',
            },
        ),
        (
            DATA,
            BAD_HEADERS,
            403,
            {'code': const.ERROR_ACCESS_DENIED, 'message': 'Access denied'},
            {},
        ),
        (
            DATA,
            BAD_HEADERS2,
            403,
            {
                'code': 'shop_permissions_conflict',
                'message': 'More then 1 permission for shop',
            },
            {},
        ),
        (
            DATA,
            BAD_HEADERS3,
            403,
            {'code': const.ERROR_ACCESS_DENIED, 'message': 'Access denied'},
            {},
        ),
        (
            {'subproduct_id': 2},
            BAD_HEADERS3,
            404,
            {
                'code': const.KEY_ERROR_MAPPING_PERMISSIONS_PROJECT,
                'message': (
                    'Permission read_shop_test_lavka is missing from '
                    'mapping AGENT_PROJECT_SETTINGS'
                ),
            },
            {},
        ),
        (
            {'subproduct_id': 10},
            GOOD_HEADERS,
            404,
            {
                'code': 'subproduct_not_found',
                'message': 'Подтовар отсутствует',
            },
            {},
        ),
        (
            {'subproduct_id': 1, 'address_id': 10},
            GOOD_HEADERS,
            404,
            {'code': 'address_not_found', 'message': 'Адресс отсутствует'},
            {},
        ),
    ],
)
async def test_purchase(
        web_context,
        web_app_client,
        stq,
        input_data,
        headers,
        status,
        response_content,
        expected_address,
):
    with stq.flushing():
        response = await web_app_client.post(
            '/shop/goods/purchase', headers=headers, json=input_data,
        )
        response_data = await response.json()

        assert response.status == status
        if response.status >= 400:
            assert response_data == response_content
        else:
            assert len(response_data['purchase_id']) == 32

            assert stq.agent_purchase_queue.times_called == 1
            call = stq.agent_purchase_queue.next_call()
            if expected_address:
                stq_address = expected_address['id']
            else:
                stq_address = expected_address
            assert call == {
                'eta': datetime.datetime(1970, 1, 1, 0, 0),
                'id': response_data['purchase_id'],
                'args': [
                    response_data['purchase_id'],
                    input_data['subproduct_id'],
                    222.33,
                    headers['X-Yandex-Login'],
                    stq_address,
                    'test_taxi_project',
                ],
                'kwargs': {},
                'queue': 'agent_purchase_queue',
            }
            assert stq.is_empty

            if expected_address and input_data.get('address'):
                async with web_context.pg.slave_pool.acquire() as conn:
                    address_query = (
                        'SELECT * FROM agent.addresses '
                        'WHERE id = {}'.format(expected_address['id'])
                    )
                    db_address = await conn.fetchrow(address_query)
                    assert dict(db_address.items()) == expected_address
