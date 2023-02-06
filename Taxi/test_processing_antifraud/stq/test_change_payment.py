# pylint: disable=redefined-outer-name
import json

import pytest

from processing_antifraud import const
from processing_antifraud.stq import handle_events
from test_processing_antifraud.stq import common


@pytest.mark.parametrize(
    'regions_checked, antifraud_group, expected_status',
    [
        (['225'], const.ANTIFRAUD_GROUP_LOYAL, const.CHANGE_STATUS_APPLYING),
        (['225'], const.ANTIFRAUD_GROUP_NEWBIE, const.STATUS_PENDING),
        ([], const.ANTIFRAUD_GROUP_LOYAL, const.STATUS_PENDING),
        (['123'], const.ANTIFRAUD_GROUP_LOYAL, const.STATUS_PENDING),
    ],
)
@common.mark_check_card_settings_experiment()
async def test_change_payment(
        stq3_context,
        web_app_client,
        territories_mock,
        mock_cardstorage_service,
        mockserver,
        regions_checked,
        antifraud_group,
        expected_status,
):
    mock_cardstorage_service.cards = [
        mock_cardstorage_service.mock_card(
            card_id='card-x6666', regions_checked=regions_checked,
        ),
    ]

    @mockserver.json_handler('/user_api-api/user_phones/get_antifraud_doc')
    def _mock_get_antifraud_doc(request, log_extra=None):
        return {'antifraud': {'group': antifraud_group}}

    order_id = 'order_id'
    data = {
        'order_id': order_id,
        'payment_id': 'card-x6666',
        'payment_type': const.CARD,
        'taxi_status': const.TAXI_STATUS_WAITING,
        'processing_index': 55,
    }
    response = await web_app_client.post(
        '/event/processing/change_payment', data=json.dumps(data),
    )
    assert response.status == 200

    event_id = (await response.json())['id']

    await handle_events.task(stq3_context, order_id)

    response = await web_app_client.post(
        '/event', data=json.dumps({'event_id': event_id}),
    )
    result_json = await response.json()

    assert result_json['status'] == expected_status


async def test_google_pay(stq3_context, web_app_client):
    order_id = 'order_id'
    data = {
        'order_id': order_id,
        'payment_id': 'google_pay_payment_id',
        'payment_type': const.GOOGLE,
        'taxi_status': const.TAXI_STATUS_WAITING,
        'processing_index': 55,
    }
    response = await web_app_client.post(
        '/event/processing/change_payment', data=json.dumps(data),
    )
    assert response.status == 200

    event_id = (await response.json())['id']

    await handle_events.task(stq3_context, order_id)

    response = await web_app_client.post(
        '/event', data=json.dumps({'event_id': event_id}),
    )
    result_json = await response.json()

    assert result_json['status'] == const.CHANGE_STATUS_APPLYING


@pytest.mark.filldb(antifraud_events='checkcard')
@pytest.mark.parametrize(
    'check_card_success, expected_status',
    [
        (True, const.CHANGE_STATUS_APPLYING),
        (False, const.CHANGE_STATUS_REJECTING),
    ],
)
async def test_check_card_result(
        stq3_context,
        web_app_client,
        mock_cardstorage_service,
        check_card_success,
        expected_status,
):
    order_id = 'order_id'
    event_id = 'event_id'

    data = {
        'order_id': order_id,
        'region_id': 225,
        'success': check_card_success,
        'payment_id': 'card-x988b7513b1b4235fb392377a',
        'processing_index': 0,
        'antifraud_index': 3,
    }
    response = await web_app_client.post(
        '/event/update_transactions/check_card', data=json.dumps(data),
    )
    assert response.status == 200

    await handle_events.task(stq3_context, order_id)

    response = await web_app_client.post(
        '/event', data=json.dumps({'event_id': event_id}),
    )
    result_json = await response.json()

    assert result_json['status'] == expected_status


@pytest.mark.filldb(antifraud_events='checkcard')
@common.mark_move_to_cash_settings_experiment(reason='INVALID_CARD')
async def test_check_card_reason(
        stq3_context, web_app_client, db, mock_cardstorage_service,
):
    order_id = 'order_id'
    event_id = 'event_id'

    data = {
        'order_id': order_id,
        'region_id': 225,
        'success': False,
        'payment_id': 'card-x988b7513b1b4235fb392377a',
        'processing_index': 0,
        'antifraud_index': 3,
    }
    response = await web_app_client.post(
        '/event/update_transactions/check_card', data=json.dumps(data),
    )
    assert response.status == 200

    await handle_events.task(stq3_context, order_id)

    response = await web_app_client.post(
        '/event', data=json.dumps({'event_id': event_id}),
    )
    result_json = await response.json()

    assert result_json['status'] == const.CHANGE_STATUS_REJECTING
