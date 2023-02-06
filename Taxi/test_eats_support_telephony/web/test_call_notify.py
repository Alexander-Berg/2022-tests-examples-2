import http

import pytest


EXP3_FLOWS_CONSUMER = 'eats-support-telephony/flows'
EXP3_FLOWS_NAME = 'eats_support_telephony_flows'

HEADERS = {'X-Idempotency-Token': 'idempotency-token'}


EATS_SUPPORT_TELEPHONY_FLOW = {
    'first_action': {
        'type': 'first_action',
        'next_action_options': {
            'good': 'courier_hello_action',
            'blacklist': 'hangup',
        },
    },
    'courier_hello_action': {
        'type': 'playback',
        'speak_text': 'Добрый вечер, я Бон Флетчер',
        'next_action': 'check_courier_disaster',
    },
    'check_courier_disaster': {
        'type': 'condition_action',
        'next_action_options': {
            'true': 'play_courier_disaster',
            'false': 'play_courier_csat',
        },
        'conditions': [
            {'option': 'true', 'condition': {'courier_disasters': True}},
            {'option': 'false', 'condition': {}},
        ],
    },
    'play_courier_disaster': {
        'type': 'playback',
        'speak_text': 'Клятый дизастер',
        'next_action': 'play_courier_csat',
    },
    'play_courier_csat': {
        'type': 'playback',
        'speak_text': 'Оставьте пожалуйста ксат',
        'next_action': 'choose_courier_queue',
    },
    'choose_courier_queue': {
        'type': 'choose_queue',
        'queue': 'first_queue',
        'send_to_dispatcher': True,
    },
    'hangup': {'type': 'hangup', 'send_to_dispatcher': True},
}


@pytest.mark.config(EATS_SUPPORT_TELEPHONY_FLOW={})
async def test_bad_request(taxi_eats_support_telephony_web):
    body = {
        'call_external_id': 'random_external_id',
        'ivr_flow_id': 'eats_support_flow',
        'call_guid': 'random_call_guid',
        'service_number': '8800',
        'abonent_number': '+74951234567',
        'direction': 'incoming',
        'actions': [],
        'last_action': -1,
    }
    response = await taxi_eats_support_telephony_web.post(
        '/v1/ivr-framework/call-notify', json=body,
    )
    assert response.status == http.HTTPStatus.BAD_REQUEST


@pytest.mark.client_experiments3(
    consumer=EXP3_FLOWS_CONSUMER,
    config_name=EXP3_FLOWS_NAME,
    args=[
        {
            'name': 'ivr_flow_id',
            'type': 'string',
            'value': 'eats_support_flow',
        },
    ],
    value=EATS_SUPPORT_TELEPHONY_FLOW,
)
@pytest.mark.config(
    EATS_SUPPORT_TELEPHONY_QUEUE_PHONES={'first_queue': '9900'},
    EATS_SUPPORT_TELEPHONY_BLACK_LIST=[],
    EATS_SUPPORT_TELEPHONY_FLOW_DISASTERS={},
)
async def test_linear_steps(
        taxi_eats_support_telephony_web, mock_personal, mock_eats_support_misc,
):
    @mock_personal('/v1/phones/find')
    def _mock_phones_store(request):
        return {'value': request.json['value'], 'id': '1234567890'}

    @mock_eats_support_misc('/v1/phone-info')
    def _mock_phone_info(request):
        return {
            'client_id': '177044934',
            'active_order': {
                'order_id': 'random-order',
                'order_city': 'City',
                'delivery_type': 'marketplace',
                'client_id': 'random_client',
                'partner_id': 'random_partner_id',
                'partner_name': 'РесторанРесторан',
                'brand_id': 'random_brand_id',
                'business_type': 'restaurant',
                'caller_role': 'client',
                'order_status': 'call_center_confirmed',
                'client_application': 'eats',
                'partner_personal_phone_id': (
                    'random_partner_personal_phone_id'
                ),
            },
            'has_more_than_one_active_order': False,
        }

    body = {
        'call_external_id': 'random_external_id',
        'ivr_flow_id': 'eats_support_flow',
        'call_guid': 'random_call_guid',
        'service_number': '8800',
        'abonent_number': '+71234567890',
        'direction': 'incoming',
        'actions': [],
        'last_action': -1,
    }

    response = await taxi_eats_support_telephony_web.post(
        '/v1/ivr-framework/call-notify', headers=HEADERS, json=body,
    )
    assert response.status == http.HTTPStatus.OK

    response_data = await response.json()
    assert response_data
