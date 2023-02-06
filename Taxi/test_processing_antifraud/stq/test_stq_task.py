# pylint: disable=redefined-outer-name
import json

import pytest

from processing_antifraud import const
from processing_antifraud import exceptions
from processing_antifraud.models import antifraud_proc
from processing_antifraud.models import events
from processing_antifraud.stq import handle_events


UNFINISHED_USER_UID = '083a1650bfa8506f4a7b69fdc3607b46'


@pytest.mark.parametrize(
    'success, expected',
    [
        (
            True,
            {
                'check_card_is_finished': True,
                '_id': '675b9c43fb7a13138a5d61a653d8fecf',
                'main_card_payment_id': 'card-x988b7513b1b4235fb392377a',
                'payment_type': 'card',
                'user_uid': '4020890530',
                'last_known_ip': '::ffff:94.25.170.207',
                'nearest_zone': 'moscow',
            },
        ),
        (
            False,
            {
                '_id': '675b9c43fb7a13138a5d61a653d8fecf',
                'antifraud_finished': True,
                'check_card_is_finished': True,
                'main_card_payment_id': 'card-x988b7513b1b4235fb392377a',
                'need_cvn': True,
                'payment_type': 'card',
                'user_uid': '4020890530',
                'last_known_ip': '::ffff:94.25.170.207',
                'nearest_zone': 'moscow',
            },
        ),
    ],
)
async def test_check_card(
        success,
        expected,
        stq3_context,
        web_app_client,
        patch,
        mock_cardstorage_service,
):
    @patch('taxi.clients.territories.TerritoriesApiClient._request')
    # pylint: disable=unused-variable
    async def territories_request(*args, **kwargs):
        return {'region_id': 5, 'currency': 'RUB'}

    @patch('taxi.clients.user_api.UserApiClient.get_antifraud_doc')
    # pylint: disable=unused-variable
    async def get_antifraud_doc(*args, **kwargs):
        return {'antifraud': {'version': 1, 'group': 1}}

    @patch('taxi.stq.client.put')
    # pylint: disable=unused-variable
    async def put(
            queue, eta=None, task_id=None, args=None, kwargs=None, loop=None,
    ):
        if queue == const.STQ_UPDATE_TRANSACTIONS_EVENTS_QUEUE:
            arg_order_id, args = args
            event = args[0]

            assert arg_order_id == order_id
            assert event == {
                'event_name': const.EVENT_NAME_CHECK_CARD,
                'antifraud_index': 0,
                'processing_index': 0,
                'kwargs': {
                    'owner_uid': '4020890530',
                    'billing_id': 'x988b7513b1b4235fb392377a',
                    'user_ip': '::ffff:94.25.170.207',
                    'region_id': 5,
                    'currency': 'RUB',
                },
            }

    order_id = '675b9c43fb7a13138a5d61a653d8fecf'
    app = stq3_context

    data = {
        'order_id': order_id,
        'payment_method_id': 'card-x988b7513b1b4235fb392377a',
        'nearest_zone': 'moscow',
        'user_uid': '4020890530',
        'payment_type': 'card',
        'source': None,
        'last_known_ip': '::ffff:94.25.170.207',
        'processing_index': 0,
        'user_phone_id': '5b56f0be8d64e6667db1440e',
        'destination_types': [],
        'client_application': 'yango_android',
        'client_version': '3.3.3',
        'source_type': 'other',
    }

    response = await web_app_client.post(
        '/event/processing/order_created', data=json.dumps(data),
    )

    assert response.status == 200

    await handle_events.task(app, order_id, [])

    data = {
        'order_id': order_id,
        'payment_id': 'card-x988b7513b1b4235fb392377a',
        'success': success,
        'region_id': 5,
        'processing_index': 0,
        'antifraud_index': 1,
    }
    response = await web_app_client.post(
        '/event/update_transactions/check_card', data=json.dumps(data),
    )
    assert response.status == 200

    await handle_events.task(app, order_id)

    doc = await antifraud_proc.AntifraudProc.find_one_by_id(
        app.mongo, order_id,
    )
    result = doc.to_dict(use_default=False)
    for key in expected:
        assert expected[key] == result[key]


@pytest.mark.config(DEFAULT_ANTIFRAUD_CONFIG={'enabled': True, 'personal': []})
async def test_proc_fallback(
        stq3_context, web_app_client, patch, response_mock,
):
    @patch('taxi.stq.client.put')
    # pylint: disable=unused-variable
    async def put(
            queue, eta=None, task_id=None, args=None, kwargs=None, loop=None,
    ):
        pass

    @patch('taxi.clients.user_api.UserApiClient.get_antifraud_doc')
    # pylint: disable=unused-variable
    async def get_antifraud_doc(*args, **kwargs):
        return {'antifraud': {'version': 1, 'group': 1}}

    @patch('taxi.clients.experiments3.Experiments3Client.get_values')
    # pylint: disable=unused-variable
    async def get_values(*args, **kwargs):
        return []

    app = stq3_context
    order_id = '675b9c43fb7a13138a5d61a653d8fecf'

    data = {
        'order_id': order_id,
        'processing_index': 0,
        'tariff_class': 'econom',
        'transporting_time': '2019-04-18T16:04:56.845082+03:00',
        'fixed_price': True,
        'category_id': 'e9200a728aa8133f8814a9cbdaf5090a',
        'alias_id': 'e9200a728aa8133f8814a9cbdaf5090a',
        'db_id': 'e9200a728aa8133f8814a9cbdaf5090a',
        'surge': {'surge': 1.0, 'alpha': 2, 'beta': 2.2, 'surcharge': 1.0},
        'coupon': {'value': 2, 'percent': 10, 'limit': 500},
        'discount_multiplier': 1.5,
    }

    response = await web_app_client.post(
        '/event/processing/driver_transporting', data=json.dumps(data),
    )

    assert response.status == 200

    await handle_events.task(app, order_id)


async def test_finish_antifraud(stq3_context, web_app_client, patch):
    @patch('taxi.stq.client.put')
    # pylint: disable=unused-variable
    async def put(
            queue, eta=None, task_id=None, args=None, kwargs=None, loop=None,
    ):
        pass

    app = stq3_context
    order_id = '17f3b5c46deb42099f4e95b8aafd69fa'

    data = {'order_id': order_id, 'processing_index': 0}

    response = await web_app_client.post(
        '/event/processing/order_finished', data=json.dumps(data),
    )
    assert response.status == 200

    await handle_events.task(app, order_id)

    with pytest.raises(exceptions.NotFound):
        await antifraud_proc.AntifraudProc.find_one_by_id(app.mongo, order_id)


async def test_finish_without_doc(stq3_context, web_app_client):
    order_id = '675b9c43fb7a13138a5d61a653d8fecf'
    app = stq3_context

    data = {'order_id': order_id, 'processing_index': 0}

    response = await web_app_client.post(
        '/event/processing/order_finished', data=json.dumps(data),
    )
    assert response.status == 200

    await handle_events.task(app, order_id)

    with pytest.raises(exceptions.NotFound):
        await antifraud_proc.AntifraudProc.find_one_by_id(app.mongo, order_id)


async def test_archive_request(stq3_context, order_archive_mock):
    order_id = 'already_finished_order'
    order_archive_mock.set_order_proc({'status': 'finished', '_id': order_id})
    app = stq3_context

    await handle_events.task(app, order_id)

    unfinished_events = await events.Events.get_unfinished_events(
        app.mongo, order_id, secondary=False,
    )
    assert unfinished_events == []


@pytest.mark.parametrize(
    'order_id',
    ['unfinished_order_without_afd', 'unfinished_archive_order_without_afd'],
)
async def test_create_afd_context_from_proc(
        stq3_context, patch, order_id, order_archive_mock,
):
    order_archive_mock.set_order_proc(
        {
            '_id': order_id,
            'status': 'assinged',
            'payment_tech': {'debt': True},
            'order': {
                'user_uid': UNFINISHED_USER_UID,
                'application': 'yango_android',
                'performer': {'tariff': {'class': 'econom'}},
                'request': {
                    'source': {'object_type': 'аэропорт'},
                    'destinations': [{'object_type': 'аэропорт'}],
                },
            },
        },
    )

    @patch(
        'processing_antifraud.modules.events_handler.module.do_handle_events',
    )
    # pylint: disable=unused-variable
    async def _mock_do_handle_events(app, event_list, context, **kwargs):
        assert context.antifraud.user_uid == UNFINISHED_USER_UID
        assert context.antifraud.client_application == 'yango_android'

    app = stq3_context
    await handle_events.task(app, order_id)
