# pylint: disable=redefined-outer-name
import copy
import datetime

import pytest

from taxi.clients import parks
from taxi.clients import startrack

from support_info import config
from support_info import stq_task
from support_info.internal import stq_utils
from test_support_info import helpers as support_info_helpers


STARTRACK_QUEUE = config.Config.STARTRACK_ACCEPT_TICKET_PARAMS['queue']


@pytest.fixture
async def mock_get_driver_profiles(monkeypatch):
    """ Mock getting parks"""
    search_patcher = support_info_helpers.BaseAsyncPatcher(
        target=parks.ParksClient,
        method='get_driver_profiles',
        response_body={
            'parks': [
                {
                    'contacts': {
                        'example_contact_id': {'email': 'park.milo@milo.park'},
                        'second_contact_id': {'email': 'park2@milo.park'},
                        'third_contact_id': {'email': ''},
                    },
                },
            ],
        },
    )
    search_patcher.patch(monkeypatch)
    return search_patcher


FULL_FILLED_ORDER = {
    '_id': 'order_aze',
    'cost': 150,
    'user_phone_id': '539eb65be7e5b1f53980dfa9',
    'feedback': {'rating': 4},
    'payment_tech': {'need_accept': True, 'type': 'card'},
    'performer': {
        'uuid': 'performer_uuid',
        'driver_license': 'driver_license_1',
        'tariff': {'currency': 'AZN', 'class': 'premium'},
        'db_id': 'best_of_the_bests_park',
        'taxi_alias': {'id': 'order_alias_aze'},
    },
    'request': {
        'due': datetime.datetime(
            year=2019, month=5, day=29, hour=16, minute=53,
        ),
        'payment': {'type': 'card'},
    },
    'pricing_data': {
        'driver': {'price': {'total': 1500}},
        'user': {'price': {'total': 1500}},
    },
    'nz': 'baku',
    'city': 'Баку',
    'user_locale': 'en',
}


@pytest.mark.translations(
    zendesk_forms={
        'accept_ticket_subject': {'ru': 'Акцепт по заказу {order_id}'},
        'accept_ticket_comment': {
            'ru': (
                'Заказ {order_id}\n'
                'Телефон водителя {driver_phone}\n'
                'Предварительная стоимость: {fixed_price} {currency}\n'
                'Сумма на акцепте: {order_cost} {currency}\n'
                'Способ оплаты: {payment_type}\n'
                'Ссылка на заказ в админке: {order_url}\n'
                'Ссылка на заказ в таксометре: {taximeter_url}\n'
                'Ссылка на заказ в платежах: {payment_url}\n'
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
                'fixed_price': {'price': 1200.0},
                'payment_tech': {'need_accept': True, 'type': 'card'},
                'performer': {
                    'tariff': {'currency': 'RUB', 'class': 'econom'},
                    'db_id': 'park_id',
                    'taxi_alias': {'id': 'order_alias_rus'},
                },
                'cost': 1000,
                'nz': 'mosсow',
                'city': 'Ростов-на-Дону',
                'user_locale': 'ru',
                'request': {'payment': {'type': 'card'}},
            },
            {
                'description': (
                    'Заказ order_rus\n'
                    'Телефон водителя ---\n'
                    'Предварительная стоимость: 1200.0 RUB\n'
                    'Сумма на акцепте: 1000 RUB\n'
                    'Способ оплаты: card\n'
                    'Ссылка на заказ в админке: '
                    'https://ymsh-admin.mobile.yandex-team.ru/?order_id'
                    '=order_rus\n'
                    'Ссылка на заказ в таксометре: '
                    '/redirect/to/order?db=park_id&order=order_alias_rus\n'
                    'Ссылка на заказ в платежах: '
                    'https://ymsh-admin.mobile.yandex-team.ru'
                    '/?payments_order_id=order_rus\n'
                ),
                'clid': 'park_id',
                'city': 'ростов_на_дону',
                'tariff': 'econom',
                'paymentType': 'card',
                'OrderId': 'order_rus',
                'orderCost': 1000,
                'fixedPrice': 1200.0,
                'country': 'rus',
                'unique': 'order_rus_accept_ticket',
                'summary': 'Акцепт по заказу order_rus',
                'tags': [
                    'ручной_акцепт',
                    'свежий_акцепт_из_админки',
                    'dr_payment_not_received_flagged_trip',
                ],
                'parkEmail': 'park.milo@milo.park park2@milo.park',
                'queue': {'key': STARTRACK_QUEUE},
                'type': {'key': 'task'},
            },
        ),
        (
            {
                '_id': 'order_aze',
                'payment_tech': {'need_accept': True, 'type': 'card'},
                'performer': {
                    'tariff': {'currency': 'AZN', 'class': 'premium'},
                    'db_id': 'park_aze_id',
                    'taxi_alias': {'id': 'order_alias_aze'},
                },
                'cost': 150,
                'nz': 'baku',
                'city': 'Баку',
                'user_locale': 'en',
                'request': {'payment': {'type': 'card'}},
            },
            {
                'description': (
                    'Заказ order_aze\n'
                    'Телефон водителя ---\n'
                    'Предварительная стоимость:  AZN\n'
                    'Сумма на акцепте: 150 AZN\n'
                    'Способ оплаты: card\n'
                    'Ссылка на заказ в админке: '
                    'https://ymsh-admin.mobile.yandex-team.ru/?order_id'
                    '=order_aze\n'
                    'Ссылка на заказ в таксометре: '
                    '/redirect/to/order?db=park_aze_id&order=order_alias_aze\n'
                    'Ссылка на заказ в платежах: '
                    'https://ymsh-admin.mobile.yandex-team.ru'
                    '/?payments_order_id=order_aze\n'
                ),
                'city': 'баку',
                'clid': 'park_aze_id',
                'tariff': 'premium',
                'paymentType': 'card',
                'OrderId': 'order_aze',
                'orderCost': 150,
                'fixedPrice': '',
                'country': 'aze',
                'unique': 'order_aze_accept_ticket',
                'summary': 'Акцепт по заказу order_aze',
                'tags': [
                    'ручной_акцепт',
                    'свежий_акцепт_из_админки',
                    'dr_payment_not_received_flagged_trip',
                ],
                'parkEmail': 'park.milo@milo.park park2@milo.park',
                'queue': {'key': STARTRACK_QUEUE},
                'type': {'key': 'task'},
            },
        ),
        (
            {
                '_id': 'order_not_accept',
                'fixed_price': {'price': 500.0},
                'payment_tech': {'type': 'card'},
                'request': {'payment': {'type': 'card'}},
            },
            None,
        ),
        (
            FULL_FILLED_ORDER,
            {
                'description': (
                    'Заказ order_aze\n'
                    'Телефон водителя +79999999999\n'
                    'Предварительная стоимость:  AZN\n'
                    'Сумма на акцепте: 150 AZN\n'
                    'Способ оплаты: card\n'
                    'Ссылка на заказ в админке: '
                    'https://ymsh-admin.mobile.yandex-team.ru/'
                    '?order_id=order_aze\n'
                    'Ссылка на заказ в таксометре: '
                    '/redirect/to/order'
                    '?db=best_of_the_bests_park&order=order_alias_aze\n'
                    'Ссылка на заказ в платежах: '
                    'https://ymsh-admin.mobile.yandex-team.ru'
                    '/?payments_order_id=order_aze\n'
                ),
                'city': 'баку',
                'clid': 'best_of_the_bests_park',
                'tariff': 'premium',
                'paymentType': 'card',
                'OrderId': 'order_aze',
                'orderDate': '29.05.19',
                'orderTime': '19:53',
                'orderCost': 150,
                'orderPreCost': 1500.0,
                'fixedPrice': '',
                'driverLicense': 'driver_license_1',
                'driverPhone': '+79999999999',
                'country': 'aze',
                'unique': 'order_aze_accept_ticket',
                'summary': 'Акцепт по заказу order_aze',
                'tags': [
                    'ручной_акцепт',
                    'свежий_акцепт_из_админки',
                    'dr_payment_not_received_flagged_trip',
                ],
                'parkEmail': 'park.milo@milo.park park2@milo.park',
                'queue': {'key': STARTRACK_QUEUE},
                'type': {'key': 'task'},
                'userPhone': '+7999999999',
            },
        ),
    ],
)
async def test_success(
        support_info_app_stq,
        patch,
        mock_get_driver_profiles,
        mock_get_user_phones,
        mock_personal,
        order,
        ticket,
        patch_get_order_by_id,
        patch_get_startrack_tickets,
        patch_created_startrack_ticket,
):

    patch_get_order_by_id(order)
    patch_created_startrack_ticket({'key': 'TAXITEST-1'}, ticket_data=ticket)
    patch_get_startrack_tickets([])

    await stq_task.accept_ticket(support_info_app_stq, order['_id'])


@pytest.mark.parametrize(
    'expected_data',
    [
        {
            'city': 'Баку',
            'country': 'rus',
            'currency': 'AZN',
            'driver_id': 'performer_uuid',
            'driver_license': 'driver_license_1',
            'driver_phone': '+79999999999',
            'fixed_price': '',
            'order_cost': 150,
            'order_date': '29.05.19',
            'order_time': '19:53',
            'user_phone': '+7999999999',
            'phone_number_trips': 100500,
            'order_id': 'order_aze',
            'order_url': (
                'https://ymsh-admin.mobile.yandex-team.ru/'
                '?order_id=order_aze'
            ),
            'clid': 'best_of_the_bests_park',
            'park_email': 'park.milo@milo.park park2@milo.park',
            'alias_id': 'order_alias_aze',  # park order id
            'payment_type': 'card',
            'payment_url': (
                'https://ymsh-admin.mobile.yandex-team.ru/'
                '?payments_order_id=order_aze'
            ),
            'order_pre_cost': 1500.0,
            'rating': 4,
            'taximeter_url': (
                '/redirect/to/order?'
                'db=best_of_the_bests_park&order=order_alias_aze'
            ),
            'tariff': 'premium',
            'contract_id': 'contract_id',
        },
    ],
)
async def test_gather_data(
        support_info_app_stq,
        mock_get_driver_profiles,
        mock_get_user_phones,
        mock_personal,
        expected_data,
):
    ticket_data = await stq_utils.gather_order_data(
        app=support_info_app_stq,
        order=FULL_FILLED_ORDER,
        country={'_id': 'rus'},
        contract_id='contract_id',
    )
    assert ticket_data == expected_data
    mock_get_driver_profiles.assert_called()


@pytest.mark.translations(
    zendesk_forms={
        'accept_ticket_subject': {'ru': 'subject'},
        'accept_ticket_comment': {'ru': 'comment'},
    },
)
@pytest.mark.parametrize(
    'order',
    [
        (
            {
                '_id': 'order_rus',
                'fixed_price': {'price': 1200.0},
                'payment_tech': {'need_accept': True, 'type': 'card'},
                'performer': {
                    'tariff': {'currency': 'RUB', 'class': 'econom'},
                    'db_id': 'park_id',
                    'taxi_alias': {'id': 'order_alias_rus'},
                },
                'cost': 1000,
                'nz': 'mosсow',
                'city': 'Ростов-на-Дону',
                'user_locale': 'ru',
                'request': {'payment': {'type': 'card'}},
            }
        ),
    ],
)
async def test_startrack_exception_raises(
        support_info_app_stq,
        patch,
        mock_get_driver_profiles,
        order,
        patch_get_order_by_id,
        patch_aiohttp_session,
        response_mock,
        patch_get_startrack_tickets,
        patch_created_startrack_ticket,
):

    patch_get_order_by_id(order)
    patch_created_startrack_ticket({'key': 'TAXITEST-1'}, status=400)
    patch_get_startrack_tickets([])

    with pytest.raises(startrack.QueryError):
        await stq_task.accept_ticket(support_info_app_stq, order['_id'])


@pytest.mark.translations(
    zendesk_forms={
        'accept_ticket_subject': {'ru': 'Акцепт по заказу {order_id}'},
        'accept_ticket_comment': {'ru': 'Заказ {order_id}'},
    },
)
@pytest.mark.config(
    STARTRACK_CUSTOM_FIELDS_MAP={
        'support-taxi': {'contract_id': 'ContractId', 'order_id': 'OrderId'},
    },
)
async def test_add_contract_id_to_ticket_data(
        support_info_app_stq,
        patch,
        patch_aiohttp_session,
        response_mock,
        mock_get_driver_profiles,
        mock_get_user_phones,
        patch_get_order_by_id,
        patch_get_startrack_tickets,
        patch_created_startrack_ticket,
        mockserver,
        mock_personal,
):

    client_id = '9638b1c2d4004bb5b42f5f5c668c0319'
    contract_id = '73734/17'

    order = copy.deepcopy(FULL_FILLED_ORDER)
    order['request']['payment']['type'] = 'corp'
    order['request']['corp'] = dict(client_id=client_id)

    patch_get_order_by_id(order)
    patch_created_startrack_ticket(
        {'key': 'TAXITEST-1'}, contract_id=contract_id,
    )
    patch_get_startrack_tickets([])

    @mockserver.json_handler('/corp-int-api/v1/client')
    def _get_corp_contract(*args, **kwargs):
        return {'client_id': client_id, 'contract_id': contract_id}

    await stq_task.accept_ticket(support_info_app_stq, order['_id'])

    mock_get_driver_profiles.assert_called()
    assert _get_corp_contract.has_calls


async def test_ticket_already_created(
        support_info_app_stq,
        patch,
        patch_get_order_by_id,
        patch_get_startrack_tickets,
):
    order = copy.deepcopy(FULL_FILLED_ORDER)

    patch_get_order_by_id(order)
    patch_get_startrack_tickets([{'id': 'test_id', 'key': 'TAXI-123'}])

    @patch('taxi.clients.startrack.StartrackAPIClient.create_ticket_from_data')
    async def _ticket_create(*args, **kwargs):
        pass

    await stq_task.accept_ticket(support_info_app_stq, order['_id'])

    assert not _ticket_create.calls
