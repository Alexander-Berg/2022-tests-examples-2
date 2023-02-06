import dataclasses
from typing import Optional

import pytest

from tests_grocery_eats_gateway import headers

ORDER_ID = '123456-grocery'
DEPOT_ID = '777'


@dataclasses.dataclass
class ParametrizeData:
    order_id: str = ORDER_ID
    depot_id: str = DEPOT_ID
    order_status: Optional[str] = None
    cargo_status: Optional[str] = None
    promised_delivery_ts: Optional[str] = None
    finished_at: Optional[str] = None
    user_phone_number: Optional[str] = None
    courier_phone_number: Optional[str] = None
    cancel_reason: Optional[str] = None

    result_eta_fact: Optional[str] = None
    result_eta_est: Optional[str] = None
    result_delay: Optional[str] = None
    result_delay_type: Optional[str] = None
    result_cancel_type: Optional[str] = None
    result_status: Optional[str] = None


TRACKING_LINK = 'eda.yandex://tracking?orderNr={}'
NOW = '2020-03-13T07:30:00+00:00'


@pytest.mark.now(NOW)
@pytest.mark.parametrize(
    'data',
    [
        ParametrizeData(
            order_status='delivering',
            promised_delivery_ts='2020-03-13T07:05:00+00:00',
            user_phone_number='+79139999999',
            courier_phone_number='+79138888888',
            result_eta_est='10:05',
            result_delay='yes',
            result_delay_type='small',
            result_status='ready_for_delivery',
        ),
        ParametrizeData(
            order_status='assembled',
            promised_delivery_ts='2020-03-13T06:45:00+00:00',
            user_phone_number='+79139999999',
            courier_phone_number='+79138888888',
            result_eta_est='09:45',
            result_delay='yes',
            result_delay_type='high',
            result_status='ready_for_delivery',
        ),
        ParametrizeData(
            order_status='checked_out',
            promised_delivery_ts='2020-03-13T07:35:00+00:00',
            user_phone_number='+79139999999',
            result_eta_est='10:35',
            result_delay='no',
            result_status='unconfirmed',
        ),
        ParametrizeData(
            order_status='canceled',
            promised_delivery_ts='2020-03-13T07:35:00+00:00',
            finished_at='2020-03-13T07:35:00+00:00',
            cancel_reason='fraud',
            courier_phone_number='+79138888888',
            result_eta_est='10:35',
            result_eta_fact='10:35',
            result_delay='no',
            result_status='rejected',
            result_cancel_type='error_0',
        ),
        ParametrizeData(
            order_status='pending_cancel',
            promised_delivery_ts='2020-03-13T07:35:00+00:00',
            finished_at='2020-03-13T07:55:00+00:00',
            cancel_reason='dispatch_failure',
            result_eta_est='10:35',
            result_eta_fact='10:55',
            result_delay='yes',
            result_delay_type='small',
            result_status='rejected',
            result_cancel_type='no_free_courier',
        ),
        ParametrizeData(
            order_status='closed',
            promised_delivery_ts='2020-03-13T07:35:00+00:00',
            finished_at='2020-03-13T08:15:00+00:00',
            result_eta_est='10:35',
            result_eta_fact='11:15',
            result_delay='yes',
            result_delay_type='high',
            result_status='delivered',
        ),
        ParametrizeData(
            order_status='delivering',
            cargo_status='delivery_arrived',
            promised_delivery_ts='2020-03-13T07:35:00+00:00',
            user_phone_number='+79139999999',
            courier_phone_number='+79138888888',
            result_eta_est='10:35',
            result_delay='no',
            result_status='arrived_to_customer',
        ),
        ParametrizeData(
            order_status='delivering',
            cargo_status='performer_found',
            promised_delivery_ts='2020-03-13T07:35:00+00:00',
            result_eta_est='10:35',
            result_delay='no',
            result_status='ready_for_delivery',
        ),
        ParametrizeData(
            order_status='reserved',
            promised_delivery_ts='2020-03-13T07:05:00+00:00',
            result_eta_est='10:05',
            result_delay='yes',
            result_delay_type='small',
            result_status='place_confirmed',
        ),
        ParametrizeData(
            order_status='canceled',
            promised_delivery_ts='2020-03-13T07:05:00+00:00',
            finished_at='2020-03-13T07:55:00+00:00',
            cancel_reason='failure',
            result_eta_est='10:05',
            result_eta_fact='10:55',
            result_delay='yes',
            result_delay_type='high',
            result_status='rejected',
            result_cancel_type='tech_issue_rest',
        ),
    ],
)
async def test_support_data_basic(
        taxi_grocery_eats_gateway, mockserver, data, testpoint,
):
    @mockserver.json_handler(
        '/grocery-orders/internal/v1/get-eats-support-meta-info',
    )
    def _mock_tips(request):
        json_body = {
            'order_id': data.order_id,
            'order_status': data.order_status,
            'promised_delivery_ts': data.promised_delivery_ts,
            'depot_id': data.depot_id,
        }
        if data.finished_at:
            json_body['finished_at'] = data.finished_at
        if data.user_phone_number:
            json_body['user_phone_number'] = data.user_phone_number
        if data.courier_phone_number:
            json_body['courier_phone_number'] = data.courier_phone_number
        if data.cancel_reason:
            json_body['cancel_reason'] = data.cancel_reason
        if data.cargo_status:
            json_body['cargo_status'] = data.cargo_status

        return mockserver.make_response(status=200, json=json_body)

    @testpoint('fix-log-no-phone')
    def testpoint_logs(log_data):
        if data.user_phone_number:
            assert data.user_phone_number not in log_data['log']
        if data.courier_phone_number:
            assert data.courier_phone_number not in log_data['log']

    response = await taxi_grocery_eats_gateway.get(
        '/internal/grocery-eats-gateway/v1/support-data?order_id={}'.format(
            data.order_id,
        ),
        headers=headers.DEFAULT_HEADERS,
    )

    assert response.status == 200
    assert response.json()['order_is_active'] == (data.finished_at is None)

    awaited_chat_meta = {
        'order_id': data.order_id,
        'user_phone': data.user_phone_number if data.user_phone_number else '',
        'order_type': 'lavka',
        'order_delivery_type': 'our_delivery',
    }
    assert response.json()['chat_meta'] == awaited_chat_meta

    awaited_doc_center_params = {
        'order_delivery_type': 'our_delivery',
        'delivery_type': 'lavka',
        'is_courier_hard_of_hearing': False,
        'order_type': 'lavka',
        'cancel_payment': 'unknown',
        'delay': data.result_delay,
        'status': data.result_status,
        'eta_est': data.result_eta_est,
    }
    if data.result_eta_fact:
        awaited_doc_center_params['eta_fact'] = data.result_eta_fact
    if data.result_delay_type:
        awaited_doc_center_params['delay_type'] = data.result_delay_type
    if data.result_cancel_type:
        awaited_doc_center_params['cancel_type'] = data.result_cancel_type

    assert response.json()['doc_center']['params'] == awaited_doc_center_params

    awaited_doc_center_templates = {
        'wait': {
            'type': 'button-link',
            'label': 'Буду ждать',
            'href': TRACKING_LINK.format(data.order_id),
        },
        'cancel': {
            'type': 'button-link',
            'label': 'Отменить заказ',
            'href': TRACKING_LINK.format(data.order_id),
        },
        'chat': {
            'type': 'button-navigation',
            'label': 'Написать в поддержку',
            'href': 'chat',
        },
        'rate_document': {
            'type': 'document-rate-metrika',
            'target': {'like': 'macros_liked', 'dislike': 'macros_disliked'},
        },
    }

    if data.courier_phone_number:
        awaited_doc_center_templates['courier'] = {
            'type': 'button-link',
            'label': 'Позвонить курьеру',
            'href': 'tel:{}'.format(data.courier_phone_number),
        }

    assert (
        response.json()['doc_center']['templates']
        == awaited_doc_center_templates
    )

    assert testpoint_logs.times_called == 1


async def test_support_data_404_response(
        taxi_grocery_eats_gateway, mockserver,
):
    @mockserver.json_handler(
        '/grocery-orders/internal/v1/get-eats-support-meta-info',
    )
    def _mock_tips(request):
        return mockserver.make_response(status=404)

    response = await taxi_grocery_eats_gateway.get(
        '/internal/grocery-eats-gateway/v1/support-data?order_id={}'.format(
            ORDER_ID,
        ),
        headers=headers.DEFAULT_HEADERS,
    )

    assert response.status == 404
