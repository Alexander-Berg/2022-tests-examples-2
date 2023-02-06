import pytest

from taxi.clients import zendesk

from support_info import settings
from support_info import stq_task


@pytest.mark.translations(
    zendesk_forms={
        'road_accident_ticket_subject': {
            'ru': 'ДТП. Телеметрия по заказу {order_id}',
        },
        'road_accident_ticket_comment': {
            'ru': (
                'Заказ {order_id}\n'
                'Ссылка на заказ в админке: {order_url}\n'
                'Ссылка на заказ в таксометре: {taximeter_url}\n'
                'Номер водителя: {driver_phone}\n'
                'Номер клиента: {user_phone}\n'
            ),
        },
    },
)
@pytest.mark.parametrize(
    'order,ticket',
    [
        (
            {
                '_id': 'order_rus',
                'alias_id': 'alias',
                'fixed_price': {'price': 1200.0},
                'performer': {
                    'driver_id': '1',
                    'db_id': '2',
                    'taxi_alias': {'id': 'order_alias_rus'},
                },
                'cost': 1000,
                'nz': 'mosсow',
                'city': 'Москва',
                'user_locale': 'ru',
                'user_phone_id': '539eb65be7e5b1f53980dfa8',
            },
            {
                'ticket': {
                    'comment': (
                        'Заказ order_rus\n'
                        'Ссылка на заказ в админке: '
                        'https://ymsh-admin.mobile.yandex-team.ru/?order_id'
                        '=order_rus\n'
                        'Ссылка на заказ в таксометре: '
                        '/redirect/to/order?db=2&order=order_alias_rus\n'
                        'Номер водителя: +79888888888\n'
                        'Номер клиента: +79099999999\n'
                    ),
                    'custom_fields': [
                        {'id': 27279269, 'value': 'москва'},
                        {'id': 32670029, 'value': '+79099999999'},
                        {'id': 38647729, 'value': 'order_rus'},
                        {'id': 45234829, 'value': '+79888888888'},
                        {'id': 360000337709, 'value': 'россия'},
                        {'id': 360000382858, 'value': '1500.5'},
                        {'id': 360000383898, 'value': '100.53'},
                        {'id': 360000392817, 'value': '1548315234'},
                        {'id': 360000392977, 'value': '150.5'},
                        {'id': 360000393577, 'value': '1500.51'},
                        {'id': 360000393597, 'value': '1500.52'},
                        {'id': 360000407417, 'value': '50.35'},
                    ],
                    'external_id': 'order_rus_road_accident',
                    'form_id': '360000041169',
                    'group_id': '360000066049',
                    'recipient': 'robot-support-taxi@yandex-team.ru',
                    'requester': {
                        'name': '79099999999',
                        'phone': '+79099999999',
                    },
                    'subject': 'ДТП. Телеметрия по заказу order_rus',
                    'tags': ['rd_irt_accident'],
                },
            },
        ),
        (
            {
                '_id': 'order_aze',
                'alias_id': 'alias_aze',
                'performer': {
                    'driver_id': '1',
                    'db_id': '2',
                    'taxi_alias': {'id': 'order_alias_aze'},
                },
                'cost': 150,
                'nz': 'baku',
                'city': 'Баку',
                'user_locale': 'en',
                'user_phone_id': '539eb65be7e5b1f53980dfa8',
                'user_phone': '+79099999999',
            },
            {
                'ticket': {
                    'comment': (
                        'Заказ order_aze\n'
                        'Ссылка на заказ в админке: '
                        'https://ymsh-admin.mobile.yandex-team.ru/?order_id'
                        '=order_aze\n'
                        'Ссылка на заказ в таксометре: '
                        '/redirect/to/order?'
                        'db=2&order=order_alias_aze\n'
                        'Номер водителя: +79888888888\n'
                        'Номер клиента: +79099999999\n'
                    ),
                    'custom_fields': [
                        {'id': 27279269, 'value': 'Баку'},
                        {'id': 32670029, 'value': '+79099999999'},
                        {'id': 38647729, 'value': 'order_aze'},
                        {'id': 45234829, 'value': '+79888888888'},
                        {'id': 360014610712, 'value': 'азербайджан'},
                        {'id': 360016168772, 'value': '1548315234'},
                        {'id': 360016214811, 'value': '150.5'},
                        {'id': 360016214831, 'value': '1500.5'},
                        {'id': 360016214851, 'value': '1500.51'},
                        {'id': 360016214871, 'value': '1500.52'},
                        {'id': 360016214891, 'value': '100.53'},
                        {'id': 360016250411, 'value': '50.35'},
                    ],
                    'external_id': 'order_aze_road_accident',
                    'form_id': '360000037772',
                    'group_id': '114095165511',
                    'recipient': 'robot-support-taxi@yandex-team.ru',
                    'requester': {
                        'name': '79099999999',
                        'phone': '+79099999999',
                    },
                    'subject': 'ДТП. Телеметрия по заказу order_aze',
                    'tags': ['rd_irt_accident'],
                },
            },
        ),
    ],
)
async def test_success(
        support_info_app_stq,
        patch,
        mock_get_user_phones,
        order,
        ticket,
        mock_personal,
):
    @patch(
        'taxi.clients.archive_api._NoCodegenOrderArchive.order_proc_retrieve',
    )
    async def _order_proc_retrieve(alias_id, **kwargs):
        assert alias_id == order['alias_id']
        return {'_id': order['_id'], 'order': order}

    @patch('taxi.clients.zendesk.ZendeskApiClient.ticket_create')
    async def _ticket_create(data):
        assert data == ticket
        return {'ticket': {'id': 100}}

    @patch('taxi.clients.zendesk.ZendeskApiClient.get_tickets_by_external_id')
    async def _get_tickets_by_external_id(external_id):
        assert external_id == str(order['_id']) + '_road_accident'
        return {'tickets': []}

    @patch('taxi.stq.client.put')
    async def _put(queue, **kwargs):
        ticket_data, ticket_type = kwargs['args']
        assert queue == settings.STQ_SUPPORT_INFO_ZENDESK_TO_STARTRACK_QUEUE
        assert ticket_data == ticket
        assert ticket_type == 'road_accident'

    road_accident_data = {
        'alias_id': order['alias_id'],
        'driver_id': '1',
        'park_id': '2',
        'timestamp': '1548315234',
        'max_acceleration': '150.5',
        'accident_speed': '1500.5',
        'latitide': '1500.51',
        'longitude': '1500.52',
        'bearing': '100.53',
        'probability': '50.35',
    }

    await stq_task.create_road_accident_ticket(
        support_info_app_stq, road_accident_data,
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
        'road_accident_ticket_subject': {'ru': 'subject'},
        'road_accident_ticket_comment': {'ru': 'comment'},
    },
)
@pytest.mark.parametrize(
    'order',
    [
        (
            {
                '_id': 'order_rus',
                'alias_id': 'alias',
                'fixed_price': {'price': 1200.0},
                'performer': {
                    'driver_id': '1',
                    'db_id': '2',
                    'taxi_alias': {'id': 'order_alias_rus'},
                },
                'cost': 1000,
                'nz': 'mosсow',
                'city': 'Москва',
                'user_locale': 'ru',
                'user_phone_id': '539eb65be7e5b1f53980dfa8',
            }
        ),
    ],
)
async def test_zendesk_exception_raises(
        support_info_app_stq,
        mock_get_user_phones,
        patch,
        order,
        mock_personal,
):
    @patch(
        'taxi.clients.archive_api._NoCodegenOrderArchive.order_proc_retrieve',
    )
    async def _order_proc_retrieve(alias_id, **kwargs):
        return {'_id': order['_id'], 'order': order}

    @patch('taxi.clients.zendesk.ZendeskApiClient.ticket_create')
    async def _ticket_create(data):
        raise zendesk.BaseError

    @patch('taxi.clients.zendesk.ZendeskApiClient.get_tickets_by_external_id')
    async def _get_tickets_by_external_id(external_id):
        return {'tickets': []}

    @patch('taxi.stq.client.put')
    async def _put(queue, **kwargs):
        pass

    road_accident_data = {
        'alias_id': order['alias_id'],
        'driver_id': '1',
        'park_id': '2',
        'timestamp': '1548315234',
        'max_acceleration': '150.5',
        'accident_speed': '1500.5',
        'latitide': '1500.51',
        'longitude': '1500.52',
        'bearing': '100.53',
        'probability': '50.35',
    }
    with pytest.raises(zendesk.BaseError):
        await stq_task.create_road_accident_ticket(
            support_info_app_stq, road_accident_data,
        )


@pytest.mark.config(ZENDESK_IGNORE_EXCEPTION=True)
@pytest.mark.translations(
    zendesk_forms={
        'road_accident_ticket_subject': {'ru': 'subject'},
        'road_accident_ticket_comment': {'ru': 'comment'},
    },
)
@pytest.mark.parametrize(
    'order',
    [
        (
            {
                '_id': 'order_rus',
                'alias_id': 'alias',
                'fixed_price': {'price': 1200.0},
                'performer': {
                    'driver_id': '1',
                    'db_id': '2',
                    'taxi_alias': {'id': 'order_alias_rus'},
                },
                'cost': 1000,
                'nz': 'mosсow',
                'city': 'Москва',
                'user_locale': 'ru',
                'user_phone_id': '539eb65be7e5b1f53980dfa8',
            }
        ),
    ],
)
async def test_zendesk_exception_ignored(
        support_info_app_stq,
        mock_get_user_phones,
        patch,
        order,
        mock_personal,
):
    @patch(
        'taxi.clients.archive_api._NoCodegenOrderArchive.order_proc_retrieve',
    )
    async def _order_proc_retrieve(alias_id, **kwargs):
        return {'_id': order['_id'], 'order': order}

    @patch('taxi.clients.zendesk.ZendeskApiClient.ticket_create')
    async def _ticket_create(data):
        raise zendesk.BaseError

    @patch('taxi.clients.zendesk.ZendeskApiClient.get_tickets_by_external_id')
    async def _get_tickets_by_external_id(external_id):
        return {'tickets': []}

    @patch('taxi.stq.client.put')
    async def _put(queue, **kwargs):
        pass

    road_accident_data = {
        'alias_id': order['alias_id'],
        'driver_id': '1',
        'park_id': '2',
        'timestamp': '1548315234',
        'max_acceleration': '150.5',
        'accident_speed': '1500.5',
        'latitide': '1500.51',
        'longitude': '1500.52',
        'bearing': '100.53',
        'probability': '50.35',
    }
    await stq_task.create_road_accident_ticket(
        support_info_app_stq, road_accident_data,
    )
