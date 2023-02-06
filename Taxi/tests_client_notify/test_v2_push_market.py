import pytest

X_IDEMPOTENCY_TOKEN = 'token'


@pytest.mark.config(
    CLIENT_NOTIFY_SERVICES={
        'market': {'description': 'Маркет', 'provider': 'market'},
    },
    CLIENT_NOTIFY_INTENTS={
        'market': {'new_order': {'description': 'new order'}},
    },
    CLIENT_NOTIFY_PAYLOAD_REPACK={
        'repack_rules': [
            {
                'enabled': True,
                'conditions': {'services': ['market'], 'intents': []},
                'payload_repack': {
                    'notificationSubtype': 'PUSH_STORE_LAVKA',
                    'data': {
                        'push_template_param_message#xget': (
                            '/root/notification/text'
                        ),
                        'push_template_param_title#xget': (
                            '/root/notification/title'
                        ),
                        'push_data_store_push_deeplink_v1': (
                            'yamarket://my/orders?type=products'
                        ),
                    },
                },
            },
        ],
    },
)
async def test_market(taxi_client_notify, mockserver):
    client_passport_uid = 999

    @mockserver.json_handler('/market-pers-notify/api/event/add')
    def _send(request):
        data = request.json
        assert data == {
            'notificationSubtype': 'PUSH_STORE_LAVKA',
            'uid': int(client_passport_uid),
            'data': {
                'push_template_param_title': 'Title',
                'push_template_param_message': 'Body',
                'push_data_store_push_deeplink_v1': (
                    'yamarket://my/orders?type=products'
                ),
            },
        }

        return mockserver.make_response('{}', 201)

    response = await taxi_client_notify.post(
        'v2/push',
        headers={'X-Idempotency-Token': X_IDEMPOTENCY_TOKEN},
        json={
            'service': 'market',
            'message_id': 'service_message_id',
            'client_id': str(client_passport_uid),
            'intent': 'new_order',
            'notification': {'text': 'Body', 'title': 'Title'},
            'data': {},
        },
    )
    assert response.status_code == 200
