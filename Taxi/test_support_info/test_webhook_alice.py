# pylint: disable=redefined-outer-name, too-many-arguments
import datetime

import pytest

from taxi.clients import archive_api
from taxi.clients import chatterbox
from taxi.clients import support_chat


NOW = datetime.datetime(2018, 6, 15, 12, 34)


@pytest.fixture
def mock_order_proc_retrieve(monkeypatch, mock):
    @mock
    async def _order_proc_retrieve(order_id, *args, **kwargs):
        return {
            '_id': order_id,
            'performer': {'driver_id': 'some_driver_id'},
            'order': {
                'city': 'Moscow',
                'user_id': 'some_user_id',
                'user_locale': 'ru',
                'request': {
                    'due': datetime.datetime(2019, 1, 2, 3, 4, 5),
                    'comment': 'some_precomment',
                },
                'performer': {
                    'tariff': {'class': 'econom'},
                    'driver_id': 'some_driver_id',
                    'driver_license': 'some_driver_license',
                    'car_number': 'some_car_number',
                    'db_id': 'some_db_id',
                    'clid': 'some_clid',
                    'uuid': 'some_driver_uuid',
                    'taxi_alias': {'id': 'some_alias_id'},
                },
                'cashback_cost': 15,
            },
        }

    # pylint: disable=protected-access
    monkeypatch.setattr(
        archive_api._NoCodegenOrderArchive,
        'order_proc_retrieve',
        _order_proc_retrieve,
    )
    return _order_proc_retrieve


@pytest.fixture
def mock_get_order_by_id(support_info_app, monkeypatch, mock):
    @mock
    async def _dummy_get_order_by_id(order_id, by_alias=False):
        return {'_id': order_id, 'payment_tech': {'type': 'cash'}}

    monkeypatch.setattr(
        archive_api.ArchiveApiClient,
        'get_order_by_id',
        _dummy_get_order_by_id,
    )
    return _dummy_get_order_by_id


@pytest.fixture
def mock_create_chat(support_info_app, monkeypatch, mock):
    @mock
    async def _dummy_create_chat(**kwargs):
        return {'id': 'some_chat_id'}

    monkeypatch.setattr(
        support_chat.SupportChatApiClient, 'create_chat', _dummy_create_chat,
    )
    return _dummy_create_chat


@pytest.fixture
def mock_chatterbox_tasks(support_info_app, monkeypatch, mock):
    @mock
    async def _dummy_tasks(**kwargs):
        return {'id': 'some_task_id'}

    monkeypatch.setattr(chatterbox.ChatterboxApiClient, 'tasks', _dummy_tasks)
    return _dummy_tasks


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'data,headers,expected_status,expected_select_rows,expected_create_chat,'
    'expected_chatterbox_tasks',
    [
        (
            {'user_phone': '+71234567890', 'text': 'ZOMG AAA MONSTERS!'},
            {
                'Content-Type': 'application/json',
                'X-Ya-Service-Ticket': 'TVM_key',
            },
            200,
            {
                'query_string': (
                    'id, request_due FROM %t '
                    'WHERE (user_id IN %p) '
                    'ORDER BY request_due LIMIT 1'
                ),
                'query_params': [
                    '//home/taxi/unstable/replica/mongo/indexes/'
                    'order_proc/user_id_request_due',
                    ['some_user_id'],
                ],
                'replication_rules': [
                    {'name': 'order_proc_phone_id_request_due_index'},
                ],
            },
            {
                'owner_id': 'alice_ticket_+71234567890',
                'owner_role': 'sms_client',
                'platform': 'alice',
                'metadata': {
                    'user_application': 'alice',
                    'owner_phone': '+71234567890',
                },
                'message_text': 'ZOMG AAA MONSTERS!',
                'message_sender_id': 'alice_ticket_+71234567890',
                'message_sender_role': 'sms_client',
                'message_metadata': {
                    'order_id': 'some_order_id',
                    'order_alias_id': 'some_alias_id',
                    'park_db_id': 'some_db_id',
                    'driver_uuid': 'some_driver_uuid',
                    'driver_id': 'some_driver_id',
                },
            },
            {
                'external_id': 'some_chat_id',
                'add_fields': {
                    'user_phone': '+71234567890',
                    'user_phone_id': '000000000000000000000001',
                    'user_id': 'some_user_id',
                    'user_type': 'general',
                    'user_locale': 'ru',
                    'order_id': 'some_order_id',
                    'order_alias_id': 'some_alias_id',
                    'order_date': '02.01',
                    'order_time': '06:04',
                    'driver_license': 'some_driver_license',
                    'car_number': 'some_car_number',
                    'door_to_door': False,
                    'driver_arrived': False,
                    'driver_uuid': 'some_driver_uuid',
                    'driver_id': 'some_driver_id',
                    'driver_name': 'Турбургаев Ербол',
                    'driver_phone': '+71234567890',
                    'city': 'moscow',
                    'clid': 'some_clid',
                    'country': 'rus',
                    'coupon': False,
                    'coupon_used': False,
                    'created': '2018-06-15T12:34:00+0000',
                    'park_db_id': 'some_db_id',
                    'precomment': 'some_precomment',
                    'payment_type': 'cash',
                    'tariff': 'econom',
                    'tariff_currency': 'RUB',
                    'app_version': '1.0beta',
                    'user_platform': 'alice',
                    'phone_type': 'yandex',
                    'taximeter_version': '2.0',
                    'baby_seat_services': False,
                    'cancel_distance_raw': 0,
                    'complete_rides': 0,
                    'cost_paid_supply': 0,
                    'coupon_use_value': 0,
                    'dif_ordercost_surge_surgecharge': 0.0,
                    'discount_ya_plus': False,
                    'driver_late_time': 0.0,
                    'driver_waiting_time': 0,
                    'final_ride_duration': 0.0,
                    'final_transaction_status': 'no_transactions',
                    'fixed_price_order_flg': False,
                    'order_cost': 0,
                    'order_currency': 'RUB',
                    'order_date_ymd': '2019-01-02',
                    'order_distance_raw': 0,
                    'order_due_time': 1546387445,
                    'order_pre_distance_raw': 0,
                    'order_pre_time_raw': 0,
                    'order_pre_time_raw_minutes': 0.0,
                    'order_tips': False,
                    'paid_supply': False,
                    'payment_decisions': False,
                    'point_b_changed': False,
                    'success_order_flg': False,
                    'surge_order_flg': False,
                    'transportation_animals': False,
                    'waiting': 'Нет',
                    'waiting_bool': False,
                    'waiting_cost': 0,
                    'waiting_time_raw': 0,
                    'waiting_time_raw_minutes': 0.0,
                    'is_compensation': False,
                    'is_refund': False,
                    'moved_to_cash_by_antifraud': False,
                    'payment_type_changed_to_cash': False,
                    'performer_car_number': 'some_car_number',
                    'performer_clid': 'some_clid',
                    'performer_driver_license': 'some_driver_license',
                    'performer_driver_name': 'Турбургаев Ербол',
                    'performer_driver_phone': '+71234567890',
                    'performer_driver_uuid': 'some_driver_uuid',
                    'performer_park_db_id': 'some_db_id',
                    'performer_taximeter_version': '2.0',
                    'several_ride_transactions': False,
                    'priority_list': {},
                    'time_request': 0.0,
                    'multipoints': False,
                    'multiorder': False,
                    'amount_cashback': 15,
                    'driver_first_name': 'Ербол',
                },
                'add_tags': ['sms_task', 'тикет_от_алисы'],
            },
        ),
    ],
)
@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.config(SERVICE_ROLES_ENABLED=True)
@pytest.mark.config(
    SERVICE_ROLES={'support_info': {'alice': ['noname_service']}},
)
async def test_request(
        support_info_client,
        support_info_app,
        mock_select_rows,
        mock_order_proc_retrieve,
        mock_get_order_by_id,
        mock_create_chat,
        mock_chatterbox_tasks,
        mock_get_user_phones,
        mock_get_users,
        mock_driver_trackstory,
        mock_driver_priority,
        data,
        headers,
        expected_status,
        expected_select_rows,
        expected_create_chat,
        expected_chatterbox_tasks,
        mock_tvm_get_service_name,
):
    response = await support_info_client.post(
        '/v1/webhook/alice', json=data, headers=headers,
    )
    assert response.status == expected_status
    if expected_status != 200:
        return

    if expected_select_rows is not None:
        select_rows_call = mock_select_rows.calls[0]
        select_rows_call['kwargs'].pop('log_extra', None)
        assert select_rows_call['kwargs'] == expected_select_rows

    if expected_create_chat is not None:
        create_chat_call = mock_create_chat.calls[0]
        create_chat_call['kwargs'].pop('log_extra', None)
        assert create_chat_call['kwargs'] == expected_create_chat

    if expected_chatterbox_tasks is not None:
        chatterbox_tasks_call = mock_chatterbox_tasks.calls[0]
        chatterbox_tasks_call['kwargs'].pop('log_extra', None)
        assert chatterbox_tasks_call['kwargs'] == expected_chatterbox_tasks


@pytest.mark.parametrize(
    'data,headers,expected_status',
    [
        (
            {'user_phone': '+71234567890', 'text': 'ZOMG AAA MONSTERS!'},
            {'Content-Type': 'application/json'},
            403,
        ),
        (
            {'user_phone': '+71234567890', 'text': 'ZOMG AAA MONSTERS!'},
            {
                'Content-Type': 'application/json',
                'YaTaxi-Api-Key': 'idriver-api-key',
            },
            403,
        ),
        (
            {'text': 'ZOMG AAA MONSTERS!'},
            {
                'Content-Type': 'application/json',
                'X-Ya-Service-Ticket': 'TVM_key',
            },
            400,
        ),
    ],
)
@pytest.mark.config(TVM_ENABLED=True)
async def test_bad_request(
        support_info_client, support_info_app, data, headers, expected_status,
):
    response = await support_info_client.post(
        '/v1/webhook/alice', json=data, headers=headers,
    )
    assert response.status == expected_status


@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.config(SERVICE_ROLES_ENABLED=True)
@pytest.mark.config(SERVICE_ROLES={'support_info': {}})
async def test_bad_tvm_role(
        support_info_client, support_info_app, mock_tvm_get_service_name,
):
    response = await support_info_client.post(
        '/v1/webhook/alice',
        json={'user_phone': '+71234567890', 'text': 'ZOMG AAA MONSTERS!'},
        headers={
            'Content-Type': 'application/json',
            'X-Ya-Service-Ticket': 'TVM_key',
        },
    )
    assert response.status == 403
