import pytest

from generated.clients import eats_corp_orders as eats_corp_orders_client

from corp_orders.stq import corp_create_eda_order
from test_corp_orders.stq import stq_test_util as util


@pytest.mark.config(
    TVM_RULES=[
        {'dst': 'personal', 'src': 'corp-orders'},
        {'dst': 'corp-integration-api', 'src': 'corp-orders'},
    ],
)
@pytest.mark.parametrize(
    [
        'external_ref',
        'yandex_uid',
        'user_id',
        'client_id',
        'personal_phone_id',
        'country',
        'is_fetched_ok',
        'expected_stq_fail',
        'expected_order_filename',
        'expected_corp_discount',
    ],
    [
        pytest.param(
            '191015-243801',
            'yandex_uid_1',
            'user_id_1',
            'client_id_1',
            'aaaaaaaaaaaaaaaaaaaaaaaa',
            'rus',
            True,  # fetched_ok
            None,  # expected_stq_fail
            'expected_eats_order.json',
            {},
            id='normal insert',
        ),
        pytest.param(
            '191015-243801',
            'yandex_uid_1',
            'user_id_1',
            'client_id_1',
            'aaaaaaaaaaaaaaaaaaaaaaaa',
            'rus',
            False,  # fetched_ok
            eats_corp_orders_client.GetOrder404,  # expected_stq_fail
            'expected_eats_order.json',
            {},
            id='fail stq if no order fetched',
        ),
        pytest.param(
            '191015-243801',
            'yandex_uid_1',
            'user_id_1',
            'client_id_1',
            'aaaaaaaaaaaaaaaaaaaaaaaa',
            'rus',
            False,  # fetched_ok
            None,  # expected_stq_fail
            'expected_eats_order_version_2.json',
            {},
            marks=pytest.mark.pgsql(
                'corp_orders', files=['insert_eda_order_version_2.sql'],
            ),
            id='no fail stq if no order fetched but found in db',
        ),
        pytest.param(
            '191015-243801',
            'yandex_uid_1',
            'user_id_1',
            'client_id_1',
            'aaaaaaaaaaaaaaaaaaaaaaaa',
            'rus',
            True,  # fetched_ok
            None,  # expected_stq_fail
            'expected_eats_order.json',
            {
                'corp_discount': util.get_sum_with_vat(100),
                'corp_discount_reverted': True,
                'corp_discount_version': 2,
            },
            marks=pytest.mark.pgsql(
                'corp_orders', files=['insert_eda_order_version_2.sql'],
            ),
            id='keep corp discount on conflict',
        ),
    ],
)
async def test_corp_create_eda_order(
        stq3_context,
        mockserver,
        load_json,
        external_ref,
        yandex_uid,
        user_id,
        client_id,
        personal_phone_id,
        country,
        is_fetched_ok,
        expected_stq_fail,
        expected_order_filename,
        expected_corp_discount,
):
    @mockserver.json_handler('/personal/v1/phones/store')
    async def _phones_store(request):
        return {'value': request.json['value'], 'id': 'courier_phone_id'}

    util.mock_fetching_eats_orders(mockserver, load_json, is_fetched_ok)

    @mockserver.json_handler('/taxi-corp-integration/v1/departments/by_user')
    async def _corp_int_api_department_by_user(request):
        return {'departments': [{'_id': 'department_id_1'}]}

    @mockserver.json_handler(
        r'/stq-agent/queues/api/add/(?P<queue_name>\w+)', regex=True,
    )
    async def _queue(request, queue_name):
        pass

    @mockserver.json_handler('/corp-billing-events/v1/topics/full')
    async def _events_journal_full(request):
        return {
            'topics': [
                {
                    'events': [
                        {
                            'type': corp_create_eda_order.ORDER_CREATED_EVENT,
                            'occured_at': '2021-01-01T01:00:00+00:00',
                            'meta': {
                                'passport_uid': yandex_uid,
                                'client_external_ref': client_id,
                                'employee_external_ref': user_id,
                                'personal_phone_id': personal_phone_id,
                                'prices_without_vat': {
                                    'consumer_price': '3990.0000',
                                    'performer_price': '3990.0000',
                                },
                            },
                            'meta_schema_version': 1,
                        },
                        {
                            'type': 'price_changed',
                            'meta_schema_version': 1,
                            'occured_at': '2021-01-02T01:00:00+00:00',
                            'meta': {
                                'reason': '(unknown)',
                                'prices_without_vat': {
                                    'consumer_price': '220.0000',
                                    'performer_price': '0.0000',
                                },
                            },
                        },
                        {
                            'type': 'order_closed',
                            'meta_schema_version': 1,
                            'occured_at': '2021-01-01T01:00:00+00:00',
                            'meta': {'reason': 'order closed'},
                        },
                    ],
                    'namespace': 'corp',
                    'topic': {
                        'external_ref': external_ref,
                        'revision': 3,
                        'type': 'eats/order',
                    },
                },
            ],
        }

    task_awaitable = corp_create_eda_order.task(
        stq3_context, external_ref, yandex_uid, client_id, personal_phone_id,
    )
    try:
        await task_awaitable
    except Exception as exc:  # pylint: disable=broad-except
        assert expected_stq_fail and isinstance(exc, expected_stq_fail), exc
    else:
        assert expected_stq_fail is None, f'expected {expected_stq_fail}'

        order_json_value = await util.fetch_eda_order(
            stq3_context, external_ref,
        )
        expected_json = dict(
            load_json(expected_order_filename), **expected_corp_discount,
        )
        assert expected_json == order_json_value

        assert _queue.times_called == 1  # because order status is not final


@pytest.mark.parametrize(
    ['external_ref', 'expected_event_id'],
    [
        pytest.param('external_ref_1', 'event2', id='basic findind'),
        pytest.param('external_ref_2', None, id='empty search'),
    ],
)
async def test_get_order_events(
        stq3_context, mockserver, load_json, external_ref, expected_event_id,
):
    @mockserver.json_handler('/corp-billing-events/v1/topics/full')
    async def _events_journal_full(request):
        return load_json('topics_full.json')[external_ref]

    _, last_event = await corp_create_eda_order.get_order_events(
        stq3_context, external_ref,
    )
    if last_event is not None:
        # fictional field only for test
        assert last_event.occured_at.isoformat() == '2020-05-03T03:30:33'
    else:
        assert last_event is expected_event_id
