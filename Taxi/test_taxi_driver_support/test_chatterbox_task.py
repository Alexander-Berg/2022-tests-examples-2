# pylint: disable=redefined-outer-name,unused-variable
# pylint: disable=inconsistent-return-statements, too-many-arguments
import pytest

from taxi import discovery

from taxi_driver_support import stq_task
from taxi_driver_support.internal import constants


@pytest.fixture
def mock_search(taxi_driver_support_app_stq, monkeypatch, mock):
    @mock
    async def _dummy_search(*args, **kwargs):
        return {
            'chats': [
                {
                    'id': '5bcdb13084b5976d23aa01bb',
                    'participants': [],
                    'status': {'is_open': True, 'is_visible': True},
                    'metadata': {
                        'ticket_id': 'ticket_id',
                        'author_id': 'author_id',
                    },
                },
            ],
        }

    monkeypatch.setattr(
        taxi_driver_support_app_stq.support_chat_client,
        'search',
        _dummy_search,
    )
    return _dummy_search


@pytest.mark.config(
    DRIVER_SUPPORT_ALLOW_DRIVER_PROFILES=True,
    DRIVER_SUPPORT_ADDITIONAL_META_QUERY=True,
    USE_NEW_RESTRICTIONS_FOR_CONTRACTOR=True,
)
@pytest.mark.parametrize(
    (
        'chat_id',
        'task_id',
        'unique_driver_id',
        'driver_uuid',
        'db_id',
        'order_proc_data',
        'driver_tags',
        'extra_tags',
        'extra_fields',
        'expected_update_meta',
        'support_info_metadata',
    ),
    [
        (
            '5bd8249c779fb33f90e2b45a',
            '5bd824b4779fb309e07b501b',
            '5bc702f995572fa0df26e0e2',
            '9dcc7f3a81c94e528176c4aa4a6d22e2',
            'ee6aad2097104bde9a5debbf2d814171',
            {
                '_id': 'some_id',
                'order': {
                    'performer': {'tariff': {'class': 'econom'}},
                    'nz': 'moscow',
                },
            },
            None,
            None,
            {},
            {
                'update_tags': [
                    {'change_type': 'add', 'tag': 'chat_driver'},
                    {'change_type': 'add', 'tag': 'самозанятый'},
                ],
                'update_meta': [
                    {
                        'change_type': 'set',
                        'field_name': 'park_name',
                        'value': 'ЯЕстьПарк',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'park_db_id',
                        'value': 'ee6aad2097104bde9a5debbf2d814171',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'unique_driver_id',
                        'value': '5bc702f995572fa0df26e0e2',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'driver_uuid',
                        'value': '9dcc7f3a81c94e528176c4aa4a6d22e2',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'deaf',
                        'value': False,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'driver_name',
                        'value': 'Федя Безлошадный',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'driver_license',
                        'value': 'some_license_1',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'driver_phone',
                        'value': '+79001231234',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'locale',
                        'value': 'ru',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'clid',
                        'value': 'some_clid100500',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'taximeter_version',
                        'value': '8.69(1100)',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'device_model',
                        'value': 'ModelX',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'city',
                        'value': 'Москва',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'country',
                        'value': 'rus',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'driver_points',
                        'value': 95,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'order_id',
                        'value': 'some_id',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'ticket_subject',
                        'value': 'ticket subject',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'tariff',
                        'value': 'econom',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'grade_branding',
                        'value': False,
                    },
                ],
            },
            {},
        ),
        (
            '5bd8249c779fb33f90e2b45a',
            '5bd824b4779fb309e07b501b',
            '5bc702f995572fa0df26e0e2',
            '9dcc7f3a81c94e528176c4aa4a6d22e0',
            'ee6aad2097104bde9a5debbf2d814171',
            {
                '_id': 'some_id',
                'order': {
                    'performer': {'tariff': {'class': 'econom'}},
                    'nz': 'moscow',
                    'request': {'corp': {'client_id': 'test_client_id'}},
                },
            },
            None,
            None,
            {},
            {
                'update_tags': [
                    {'change_type': 'add', 'tag': 'chat_driver'},
                    {'change_type': 'add', 'tag': 'самозанятый'},
                ],
                'update_meta': [
                    {
                        'change_type': 'set',
                        'field_name': 'park_name',
                        'value': 'ЯЕстьПарк',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'park_db_id',
                        'value': 'ee6aad2097104bde9a5debbf2d814171',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'unique_driver_id',
                        'value': '5bc702f995572fa0df26e0e2',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'driver_uuid',
                        'value': '9dcc7f3a81c94e528176c4aa4a6d22e0',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'deaf',
                        'value': True,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'driver_name',
                        'value': 'Иван Петров',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'driver_license',
                        'value': 'some_license',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'eats_courier_id',
                        'value': (
                            '9dcc7f3a81c94e528176c4aa4a6d22e0_some_eats_uuid'
                        ),
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'driver_phone',
                        'value': '+79001231234',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'locale',
                        'value': 'ru',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'clid',
                        'value': 'some_clid100500',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'car_number',
                        'value': 'test_number',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'tariffs',
                        'value': True,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'taximeter_version',
                        'value': '8.69(1100)',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'device_model',
                        'value': 'ModelX',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'city',
                        'value': 'Ростов',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'driver_points',
                        'value': 95,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'order_id',
                        'value': 'some_id',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'ticket_subject',
                        'value': 'ticket subject',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'tariff',
                        'value': 'econom',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'country',
                        'value': 'rus',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'corp_client_id',
                        'value': 'test_client_id',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'grade_branding',
                        'value': False,
                    },
                ],
            },
            {},
        ),
        (
            '5bd8249c779fb33f90e2b45a',
            '5bd824b4779fb309e07b501b',
            '5bc702f995572fa0df26e0e3',
            '9dcc7f3a81c94e528176c4aa4a6d22e1',
            'ee6aad2097104bde9a5debbf2d814171',
            {},
            ['some', 'tags', 'gold', 'grade_for_branding'],
            None,
            {},
            {
                'update_tags': [
                    {'change_type': 'add', 'tag': 'chat_driver'},
                    {'change_type': 'add', 'tag': 'самозанятый'},
                    {'change_type': 'add', 'tag': 'some'},
                    {'change_type': 'add', 'tag': 'tags'},
                    {'change_type': 'add', 'tag': 'gold'},
                    {'change_type': 'add', 'tag': 'grade_for_branding'},
                ],
                'update_meta': [
                    {
                        'change_type': 'set',
                        'field_name': 'driver_points',
                        'value': 95,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'payment_type',
                        'value': 'card',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'park_name',
                        'value': 'ЯЕстьПарк',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'park_db_id',
                        'value': 'ee6aad2097104bde9a5debbf2d814171',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'unique_driver_id',
                        'value': '5bc702f995572fa0df26e0e3',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'driver_uuid',
                        'value': '9dcc7f3a81c94e528176c4aa4a6d22e1',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'deaf',
                        'value': True,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'driver_name',
                        'value': 'Иван Петров',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'driver_license',
                        'value': 'some_license_1',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'eats_courier_id',
                        'value': (
                            '9dcc7f3a81c94e528176c4aa4a6d22e1_some_eats_uuid'
                        ),
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'driver_phone',
                        'value': '+79001231234',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'locale',
                        'value': 'ru',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'clid',
                        'value': 'some_clid100500',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'taximeter_version',
                        'value': '8.69(1100)',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'device_model',
                        'value': 'ModelX',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'city',
                        'value': 'Москва',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'country',
                        'value': 'rus',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'order_id',
                        'value': 'some_id',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'ticket_subject',
                        'value': 'ticket subject',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'status_loyalty',
                        'value': 'gold',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'grade_branding',
                        'value': True,
                    },
                ],
            },
            {'driver_points': 80, 'payment_type': 'card'},
        ),
        (
            '5bd8249c779fb33f90e2b45a',
            '5bd824b4779fb309e07b501b',
            '5bc702f995572fa0df26e0e3',
            '9dcc7f3a81c94e528176c4aa4a6d22e1',
            'ee6aad2097104bde9a5debbf2d814171',
            {},
            None,
            ['more', 'extra'],
            {},
            {
                'update_tags': [
                    {'change_type': 'add', 'tag': 'chat_driver'},
                    {'change_type': 'add', 'tag': 'самозанятый'},
                    {'change_type': 'add', 'tag': 'more'},
                    {'change_type': 'add', 'tag': 'extra'},
                ],
                'update_meta': [
                    {
                        'change_type': 'set',
                        'field_name': 'driver_points',
                        'value': 95,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'payment_type',
                        'value': 'card',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'park_name',
                        'value': 'ЯЕстьПарк',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'park_db_id',
                        'value': 'ee6aad2097104bde9a5debbf2d814171',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'unique_driver_id',
                        'value': '5bc702f995572fa0df26e0e3',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'driver_uuid',
                        'value': '9dcc7f3a81c94e528176c4aa4a6d22e1',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'deaf',
                        'value': True,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'driver_name',
                        'value': 'Иван Петров',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'driver_license',
                        'value': 'some_license_1',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'eats_courier_id',
                        'value': (
                            '9dcc7f3a81c94e528176c4aa4a6d22e1_some_eats_uuid'
                        ),
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'driver_phone',
                        'value': '+79001231234',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'locale',
                        'value': 'ru',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'clid',
                        'value': 'some_clid100500',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'taximeter_version',
                        'value': '8.69(1100)',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'device_model',
                        'value': 'ModelX',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'city',
                        'value': 'Москва',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'country',
                        'value': 'rus',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'order_id',
                        'value': 'some_id',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'ticket_subject',
                        'value': 'ticket subject',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'grade_branding',
                        'value': False,
                    },
                ],
            },
            {'driver_points': 80, 'payment_type': 'card'},
        ),
        (
            '5bd8249c779fb33f90e2b45a',
            '5bd824b4779fb309e07b501b',
            '5bc702f995572fa0df26e0e3',
            '9dcc7f3a81c94e528176c4aa4a6d22e1',
            'ee6aad2097104bde9a5debbf2d814171',
            {},
            ['some', 'tags'],
            ['more', 'extra'],
            {},
            {
                'update_tags': [
                    {'change_type': 'add', 'tag': 'chat_driver'},
                    {'change_type': 'add', 'tag': 'самозанятый'},
                    {'change_type': 'add', 'tag': 'some'},
                    {'change_type': 'add', 'tag': 'tags'},
                    {'change_type': 'add', 'tag': 'more'},
                    {'change_type': 'add', 'tag': 'extra'},
                ],
                'update_meta': [
                    {
                        'change_type': 'set',
                        'field_name': 'driver_points',
                        'value': 95,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'payment_type',
                        'value': 'card',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'park_name',
                        'value': 'ЯЕстьПарк',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'park_db_id',
                        'value': 'ee6aad2097104bde9a5debbf2d814171',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'unique_driver_id',
                        'value': '5bc702f995572fa0df26e0e3',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'driver_uuid',
                        'value': '9dcc7f3a81c94e528176c4aa4a6d22e1',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'deaf',
                        'value': True,
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'driver_name',
                        'value': 'Иван Петров',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'driver_license',
                        'value': 'some_license_1',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'eats_courier_id',
                        'value': (
                            '9dcc7f3a81c94e528176c4aa4a6d22e1_some_eats_uuid'
                        ),
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'driver_phone',
                        'value': '+79001231234',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'locale',
                        'value': 'ru',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'clid',
                        'value': 'some_clid100500',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'taximeter_version',
                        'value': '8.69(1100)',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'device_model',
                        'value': 'ModelX',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'city',
                        'value': 'Москва',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'country',
                        'value': 'rus',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'order_id',
                        'value': 'some_id',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'ticket_subject',
                        'value': 'ticket subject',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'grade_branding',
                        'value': False,
                    },
                ],
            },
            {'driver_points': 80, 'payment_type': 'card'},
        ),
        (
            '5bd8249c779fb33f90e2b45a',
            '5bd824b4779fb309e07b501b',
            None,
            None,
            None,
            {
                '_id': 'some_id',
                'order': {
                    'performer': {'tariff': {'class': 'econom'}},
                    'nz': 'moscow',
                },
            },
            None,
            None,
            {'some': 'fields'},
            {
                'update_meta': [
                    {
                        'change_type': 'set',
                        'field_name': 'order_id',
                        'value': 'some_id',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'driver_uuid',
                        'value': 'some_driver_uuid',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'some',
                        'value': 'fields',
                    },
                ],
                'update_tags': [],
            },
            {},
        ),
    ],
)
async def test_chatterbox_task(
        taxi_driver_support_app_stq,
        mock_get_tags,
        patch_aiohttp_session,
        response_mock,
        mockserver,
        mock_driver_profiles,
        mock_personal,
        order_archive_mock,
        chat_id,
        task_id,
        unique_driver_id,
        driver_uuid,
        db_id,
        order_proc_data,
        driver_tags,
        extra_tags,
        extra_fields,
        expected_update_meta,
        patch_additional_meta,
        support_info_metadata,
        patch,
):
    additional_meta_calls = patch_additional_meta(
        metadata=support_info_metadata,
    )

    if order_proc_data:
        order_archive_mock.set_order_proc(order_proc_data)

    mocked_get_tags = mock_get_tags(driver_tags, 'driver-tags')
    archive_api_url = taxi_driver_support_app_stq.settings.ARCHIVE_API_URL

    @patch('taxi.clients.tvm.TVMClient.get_ticket')
    async def get_ticket(*args, **kwargs):
        return 'Ticket 123'

    @patch_aiohttp_session(archive_api_url, 'POST')
    def _dummy_archive_api_request(method, url, **kwargs):
        return response_mock(status=404)

    @mockserver.json_handler('/parks/driver-profiles/list')
    def _dummy_profiles_url(request):
        assert request.json == {
            'fields': {
                'account': [],
                'car': [],
                'driver_profile': [],
                'park': ['driver_partner_source', 'provider_config', 'name'],
            },
            'limit': 1,
            'query': {'park': {'id': 'ee6aad2097104bde9a5debbf2d814171'}},
        }
        driver_source = constants.DRIVER_PARTNER_SOURCE_SELF_ASSIGN
        return {
            'parks': [
                {
                    'driver_partner_source': driver_source,
                    'provider_config': {'yandex': {'clid': 'some_clid100500'}},
                    'name': 'ЯЕстьПарк',
                },
            ],
            'total': 1,
        }

    @patch_aiohttp_session(
        discovery.find_service('driver_protocol').url, 'GET',
    )
    def patch_driver_protocol_request(method, url, **kwargs):
        assert method == 'get'
        assert kwargs['params'] == {
            'complete_check': 'true',
            'db': db_id,
            'driver': driver_uuid,
        }
        return response_mock(
            json={
                'reasons': [
                    {'message': 'bust', 'code': 'DriverStatusNotFree'},
                    {'message': 'blocked', 'code': 'DriverGradeBlock'},
                ],
            },
        )

    @patch_aiohttp_session(discovery.find_service('chatterbox').url, 'POST')
    def patch_request(method, url, **kwargs):
        assert method == 'post'
        if 'update_meta' in url:
            assert url.split('/')[5] == task_id
            assert kwargs['json'] == expected_update_meta
            return response_mock(json={})
        if 'tasks' in url:
            data = {'id': task_id}
            assert kwargs['json']['metadata'] == expected_update_meta
            return response_mock(json=data)

    stq_kwargs = {
        'db_id': db_id,
        'driver_uuid': driver_uuid,
        'message': {
            'metadata': {
                'order_id': 'some_id',
                'ticket_subject': 'ticket subject',
            },
        },
        'metadata': {
            'order_id': 'some_id',
            'driver_uuid': 'some_driver_uuid',
            **extra_fields,
        },
    }
    if extra_tags is not None:
        stq_kwargs['tags'] = extra_tags

    await stq_task.chatterbox_task(
        taxi_driver_support_app_stq, chat_id, unique_driver_id, **stq_kwargs,
    )

    assert additional_meta_calls

    if db_id is not None and driver_uuid is not None:
        assert mocked_get_tags.next_call()['args'][0].json == {
            'dbid': db_id,
            'uuid': driver_uuid,
        }
