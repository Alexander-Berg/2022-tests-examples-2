# pylint: disable=unused-variable
import pytest

from taxi.clients import zendesk

from support_info import settings
from support_info import stq_task
from support_info.internal import constants


@pytest.mark.config(
    ZENDESK_FEEDBACK_CUSTOM_FIELDS_SPLITTED={
        'yataxi': {
            'city': 27279269,
            'order_id': 38647729,
            'ivr_callsign': 28293405,
            'ivr_driver_fio': 27279109,
            'ivr_park_login': 28145149,
            'ivr_driver_licence': 28143149,
            'ivr_driver_phone': 27392765,
            'ivr_driver_clid': 32328909,
            'ivr_driver_uuid': 38442469,
            'ivr_taximeter_version': 40839449,
        },
    },
    DRIVER_IVR_SOURCE_TAG_ENABLED=True,
)
@pytest.mark.translations(
    zendesk_forms={
        'ivr_ticket_subject': {'ru': 'Заказ звонка из IVR\n'},
        'ivr_ticket_comment': {
            'ru': (
                'Заказ {order_id}\n'
                'Ссылка на заказ в админке: {order_url}\n'
                'Ссылка на заказ в таксометре: {taximeter_url}\n'
                'Номер водителя: {driver_phone}\n'
            ),
        },
    },
)
@pytest.mark.parametrize(
    'phone, ext_id, ticket, driver_source, park_id',
    [
        (
            '+79999999999',
            '579f40e949814a8ea81487b3b637b853',
            {
                'ticket': {
                    'comment': (
                        'Заказ \n'
                        'Ссылка на заказ в админке: \n'
                        'Ссылка на заказ в таксометре: \n'
                        'Номер водителя: +79999999999\n'
                    ),
                    'custom_fields': [
                        {'id': 27279109, 'value': 'Старая Пристарая Швабрэ'},
                        {'id': 27279269, 'value': 'москва'},
                        {'id': 27392765, 'value': '+79999999999'},
                        {'id': 28143149, 'value': '97АВ123457'},
                        {'id': 28145149, 'value': 'Парк'},
                        {'id': 28293405, 'value': 'BigSH'},
                        {'id': 38442469, 'value': '1_1'},
                        {'id': 38647729, 'value': ''},
                        {'id': 40839449, 'value': '8.80 (1073750703)'},
                    ],
                    'external_id': (
                        '579f40e949814a8ea81487b3b637b853_driver_ivr'
                    ),
                    'requester': {
                        'name': '79999999999',
                        'phone': '+79999999999',
                    },
                    'subject': 'Заказ звонка из IVR\n',
                    'tags': [
                        'Заказ_звонка',
                        'Проект_телефон_IVR',
                        'самозанятый',
                    ],
                },
            },
            constants.DRIVER_PARTNER_SOURCE_SELF_ASSIGN,
            'park_moscow',
        ),
        (
            # without callsign
            '+79999999990',
            '579f40e949814a8ea81487b3b637b853',
            {
                'ticket': {
                    'comment': (
                        'Заказ \n'
                        'Ссылка на заказ в админке: \n'
                        'Ссылка на заказ в таксометре: \n'
                        'Номер водителя: +79999999990\n'
                    ),
                    'custom_fields': [
                        {'id': 27279109, 'value': 'Старая Пристарая Швабрэ'},
                        {'id': 27279269, 'value': 'москва'},
                        {'id': 27392765, 'value': '+79999999990'},
                        {'id': 28143149, 'value': '97АВ123457'},
                        {'id': 28145149, 'value': 'Парк'},
                        {'id': 28293405, 'value': ''},
                        {'id': 38442469, 'value': '1_2'},
                        {'id': 38647729, 'value': ''},
                        {'id': 40839449, 'value': ''},
                    ],
                    'external_id': (
                        '579f40e949814a8ea81487b3b637b853_driver_ivr'
                    ),
                    'requester': {
                        'name': '79999999990',
                        'phone': '+79999999990',
                    },
                    'subject': 'Заказ звонка из IVR\n',
                    'tags': [
                        'Заказ_звонка',
                        'Проект_телефон_IVR',
                        'самозанятые_смз',
                    ],
                },
            },
            constants.DRIVER_PARTNER_SOURCE_SELFEMPLOYED,
            'park_moscow',
        ),
        (
            # without car, middle_name
            '+79999999991',
            '579f40e949814a8ea81487b3b637b853',
            {
                'ticket': {
                    'comment': (
                        'Заказ \n'
                        'Ссылка на заказ в админке: \n'
                        'Ссылка на заказ в таксометре: \n'
                        'Номер водителя: +79999999991\n'
                    ),
                    'custom_fields': [
                        {'id': 27279109, 'value': 'Старая Швабрэ'},
                        {'id': 27279269, 'value': 'москва'},
                        {'id': 27392765, 'value': '+79999999991'},
                        {'id': 28143149, 'value': '97АВ123457'},
                        {'id': 28145149, 'value': 'Парк'},
                        {'id': 38442469, 'value': '1_3'},
                        {'id': 38647729, 'value': ''},
                        {'id': 40839449, 'value': ''},
                    ],
                    'external_id': (
                        '579f40e949814a8ea81487b3b637b853_driver_ivr'
                    ),
                    'requester': {
                        'name': '79999999991',
                        'phone': '+79999999991',
                    },
                    'subject': 'Заказ звонка из IVR\n',
                    'tags': [
                        'Заказ_звонка',
                        'Проект_телефон_IVR',
                        'самозанятый',
                    ],
                },
            },
            constants.DRIVER_PARTNER_SOURCE_YANDEX,
            'park_moscow',
        ),
    ],
)
async def test_success_without_order(
        support_info_app_stq,
        patch_aiohttp_session,
        response_mock,
        mockserver,
        patch,
        phone,
        ext_id,
        ticket,
        driver_source,
        park_id,
):
    @patch('taxi.clients.zendesk.ZendeskApiClient.ticket_create')
    async def _ticket_create(data):
        assert data == ticket
        return {'ticket': {'id': 100}}

    @patch('taxi.clients.zendesk.ZendeskApiClient.get_tickets_by_external_id')
    async def _get_tickets_by_external_id(external_id):
        assert external_id == str(ext_id) + '_driver_ivr'
        return {'tickets': []}

    @patch('taxi.stq.client.put')
    async def _put(queue, **kwargs):
        ticket_data, ticket_type = kwargs['args']
        assert queue == settings.STQ_SUPPORT_INFO_ZENDESK_TO_STARTRACK_QUEUE
        assert ticket_data == ticket
        assert ticket_type == 'driver_ivr'

    @mockserver.json_handler('/parks/driver-profiles/list')
    def get_driver_profiles(request):
        assert request.json == {
            'fields': {
                'account': [],
                'car': [],
                'driver_profile': [],
                'park': ['driver_partner_source', 'login', 'city'],
            },
            'limit': 1,
            'query': {'park': {'id': park_id}},
        }
        return {
            'parks': [
                {
                    'driver_partner_source': driver_source,
                    'login': 'Парк',
                    'city': 'Москва',
                },
            ],
            'total': 1,
        }

    await stq_task.create_ivr_ticket(support_info_app_stq, phone, ext_id)

    if ticket:
        assert len(_put.calls) == 1
        assert len(_get_tickets_by_external_id.calls) == 1
    else:
        assert not _put.calls
        assert not _get_tickets_by_external_id.calls


@pytest.mark.config(
    ZENDESK_FEEDBACK_CUSTOM_FIELDS_SPLITTED={
        'yataxi': {
            'city': 27279269,
            'order_id': 38647729,
            'ivr_callsign': 28293405,
            'ivr_driver_fio': 27279109,
            'ivr_park_login': 28145149,
            'ivr_driver_licence': 28143149,
            'ivr_driver_phone': 27392765,
            'ivr_driver_clid': 32328909,
            'ivr_driver_uuid': 38442469,
            'ivr_taximeter_version': 40839449,
        },
    },
    DRIVER_IVR_SOURCE_TAG_ENABLED=True,
)
@pytest.mark.translations(
    zendesk_forms={
        'ivr_ticket_subject': {'ru': 'Заказ звонка из IVR\n'},
        'ivr_ticket_comment': {
            'ru': (
                'Заказ {order_id}\n'
                'Ссылка на заказ в админке: {order_url}\n'
                'Ссылка на заказ в таксометре: {taximeter_url}\n'
                'Номер водителя: {driver_phone}\n'
            ),
        },
    },
)
@pytest.mark.parametrize(
    'phone, ext_id, ticket, order, park_id',
    [
        (
            '+79999999999',
            '579f40e949814a8ea81487b3b637b853',
            {
                'ticket': {
                    'comment': (
                        'Заказ order_rus\n'
                        'Ссылка на заказ в админке: '
                        'https://ymsh-admin.mobile.yandex-team.ru/'
                        '?order_id=order_rus\n'
                        'Ссылка на заказ в таксометре: '
                        '/redirect/to/order'
                        '?db=park_moscow&order=order_alias_rus\n'
                        'Номер водителя: +79999999999\n'
                    ),
                    'custom_fields': [
                        {'id': 27279109, 'value': 'Старая Пристарая Швабрэ'},
                        {'id': 27279269, 'value': 'москва'},
                        {'id': 27392765, 'value': '+79999999999'},
                        {'id': 28143149, 'value': '97АВ123457'},
                        {'id': 28145149, 'value': 'Парк'},
                        {'id': 28293405, 'value': 'BigSH'},
                        {'id': 32328909, 'value': 'clid'},
                        {'id': 38442469, 'value': '1_1'},
                        {'id': 38647729, 'value': 'order_rus'},
                        {'id': 40839449, 'value': '8.80 (1073750703)'},
                    ],
                    'external_id': (
                        '579f40e949814a8ea81487b3b637b853_driver_ivr'
                    ),
                    'requester': {
                        'name': '79999999999',
                        'phone': '+79999999999',
                    },
                    'subject': 'Заказ звонка из IVR\n',
                    'tags': [
                        'Заказ_звонка',
                        'Проект_телефон_IVR',
                        'самозанятый',
                    ],
                },
            },
            {
                '_id': 'order_rus',
                'alias_id': 'alias',
                'fixed_price': {'price': 1200.0},
                'performer': {
                    'uuid': '1_1',
                    'db_id': 'park_moscow',
                    'taxi_alias': {'id': 'order_alias_rus'},
                    'clid': 'clid',
                },
                'cost': 1000,
                'nz': 'mosсow',
                'city': 'Москва',
                'user_locale': 'ru',
                'user_phone_id': '539eb65be7e5b1f53980dfa8',
            },
            'park_moscow',
        ),
    ],
)
async def test_success_with_order(
        support_info_app_stq,
        patch,
        patch_aiohttp_session,
        response_mock,
        mockserver,
        order_archive_mock,
        phone,
        ext_id,
        ticket,
        order,
        park_id,
):
    @patch(
        'taxi.clients.archive_api._NoCodegenOrderArchive.order_proc_retrieve',
    )
    async def _order_proc_retrieve(order_id, **kwargs):
        assert order_id == order['_id']
        return {'_id': order['_id'], 'order': order}

    @patch('taxi.clients.zendesk.ZendeskApiClient.ticket_create')
    async def _ticket_create(data):
        assert data == ticket
        return {'ticket': {'id': 100}}

    @patch('taxi.clients.zendesk.ZendeskApiClient.get_tickets_by_external_id')
    async def _get_tickets_by_external_id(external_id):
        assert external_id == str(ext_id) + '_driver_ivr'
        return {'tickets': []}

    @patch('taxi.stq.client.put')
    async def _put(queue, **kwargs):
        ticket_data, ticket_type = kwargs['args']
        assert queue == settings.STQ_SUPPORT_INFO_ZENDESK_TO_STARTRACK_QUEUE
        assert ticket_data == ticket
        assert ticket_type == 'driver_ivr'

    @mockserver.json_handler('/parks/driver-profiles/list')
    def get_driver_profiles(request):
        assert request.json == {
            'fields': {
                'account': [],
                'car': [],
                'driver_profile': [],
                'park': ['driver_partner_source', 'login', 'city'],
            },
            'limit': 1,
            'query': {'park': {'id': park_id}},
        }
        driver_source = constants.DRIVER_PARTNER_SOURCE_SELF_ASSIGN
        return {
            'parks': [
                {
                    'driver_partner_source': driver_source,
                    'login': 'Парк',
                    'city': 'Москва',
                },
            ],
            'total': 1,
        }

    await stq_task.create_ivr_ticket(
        support_info_app_stq, phone, ext_id, order_id=order['_id'],
    )

    if ticket:
        assert len(_put.calls) == 1
        assert len(_get_tickets_by_external_id.calls) == 1
    else:
        assert not _put.calls
        assert not _get_tickets_by_external_id.calls


@pytest.mark.config(ZENDESK_IGNORE_EXCEPTION=False)
@pytest.mark.translations(
    zendesk_forms={
        'ivr_ticket_subject': {'ru': 'subject'},
        'ivr_ticket_comment': {'ru': 'comment'},
    },
)
@pytest.mark.parametrize(
    'phone, ext_id', [('+79999999999', '579f40e949814a8ea81487b3b637b853')],
)
async def test_zendesk_exception_raises(
        support_info_app_stq, patch, phone, ext_id,
):
    @patch('taxi.clients.zendesk.ZendeskApiClient.ticket_create')
    async def _ticket_create(data):
        raise zendesk.BaseError

    @patch('taxi.clients.zendesk.ZendeskApiClient.get_tickets_by_external_id')
    async def _get_tickets_by_external_id(external_id):
        return {'tickets': []}

    @patch('taxi.stq.client.put')
    async def _put(queue, **kwargs):
        pass

    with pytest.raises(zendesk.BaseError):
        await stq_task.create_ivr_ticket(support_info_app_stq, phone, ext_id)


@pytest.mark.config(ZENDESK_IGNORE_EXCEPTION=True)
@pytest.mark.translations(
    zendesk_forms={
        'ivr_ticket_subject': {'ru': 'subject'},
        'ivr_ticket_comment': {'ru': 'comment'},
    },
)
@pytest.mark.parametrize(
    'phone, ext_id', [('+79999999999', '579f40e949814a8ea81487b3b637b853')],
)
async def test_zendesk_exception_ignored(
        support_info_app_stq, patch, phone, ext_id,
):
    @patch('taxi.clients.zendesk.ZendeskApiClient.ticket_create')
    async def _ticket_create(data):
        raise zendesk.BaseError

    @patch('taxi.clients.zendesk.ZendeskApiClient.get_tickets_by_external_id')
    async def _get_tickets_by_external_id(external_id):
        return {'tickets': []}

    @patch('taxi.stq.client.put')
    async def _put(queue, **kwargs):
        pass

    await stq_task.create_ivr_ticket(support_info_app_stq, phone, ext_id)
