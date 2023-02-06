import pytest

from testsuite.utils import matching

DELIVERY_DESCRIPTION = {
    'comment': 'some_comment',
    'payment_info': {'id': 'card-123', 'type': 'card'},
    'route_points': [
        {
            'type': 'source',
            'uri': 'some uri',
            'coordinates': [55, 55],
            'full_text': 'some full_text',
            'short_text': 'some short_text',
            'area_description': 'some area_description',
            'contact': {'name': 'some_name', 'phone': '+79999999999'},
            'comment': 'comment',
        },
        {
            'type': 'destination',
            'uri': 'some uri',
            'coordinates': [56, 56],
            'full_text': 'some full_text',
            'short_text': 'some short_text',
            'area_description': 'some area_description',
            'contact': {'name': 'some_name', 'phone': '+79999999999'},
        },
    ],
    'postcard': {
        'user_message': 'hi, buddy!',
        'path': 'some-postcard-path',
        'download_url': 'some-postcard-url',
    },
}


@pytest.fixture(name='mock_c2c_save', autouse=True)
def _mock_c2c(mockserver):
    @mockserver.json_handler('/cargo-c2c/v1/clients-orders')
    def _get_orders(request):
        order_id = request.json['order_id']

        return mockserver.make_response(
            json={
                'orders': [
                    {
                        'id': {
                            'order_id': order_id,
                            'order_provider_id': 'cargo-c2c',
                            'phone_pd_id': 'phone_pd_id_3',
                        },
                        'roles': ['initiator'],
                        'sharing_key': 'sharing_key_3',
                        'sharing_url': 'http://host/sharing_key_3',
                        'additional_delivery_description': (
                            DELIVERY_DESCRIPTION
                        ),
                    },
                ],
            },
        )

    class Context:
        def __init__(self):
            self.empty_orders_on_first_call = False

    context = Context()
    return context


def build_notify_stq_kwards(
        phone_pd_id,
        order_id,
        role,
        status,
        push_type,
        notification_id,
        key_title,
        key_body,
):
    return {
        'id': {
            'phone_pd_id': phone_pd_id,
            'order_id': order_id,
            'order_provider_id': 'cargo-c2c',
        },
        'notification_id': notification_id,
        'push_payload': {
            'logistics': {
                'type': push_type,
                'delivery_id': f'cargo-c2c/{order_id}',
                'notification_group': f'cargo-c2c/{order_id}',
                'meta': {
                    'tariff_class': 'courier',
                    'order_provider_id': 'cargo-c2c',
                    'roles': [role],
                    'order_status': status,
                },
            },
        },
        'push_content': {
            'title': {
                'keyset': 'cargo',
                'key': f'{key_title}.title',
                'locale': 'ru',
            },
            'body': {
                'keyset': 'cargo',
                'key': f'{key_body}.body',
                'locale': 'ru',
            },
        },
        'sender': 'go',
        'log_extra': {'_link': matching.AnyString()},
        'role': role,
        'initiator_phone_pd_id': 'phone_pd_id_3',
    }


async def test_generate_upload_link(taxi_cargo_c2c, default_pa_headers, pgsql):
    headers = default_pa_headers('phone_pd_id_1').copy()
    headers['X-Idempotency-Token'] = '123'

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/postcard/generate-upload-link',
        json={'content_type': 'image/jpeg'},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()['path'] == matching.AnyString()
    assert response.json()['upload_url'] == matching.AnyString()
    assert response.json()['download_url'] == matching.AnyString()

    cursor = pgsql['cargo_c2c'].cursor()
    query = 'SELECT * FROM cargo_c2c.postcards'
    cursor.execute(query)
    rows = list(cursor)
    assert len(rows) == 1
    assert rows[0][0] == response.json()['path']
    assert not rows[0][1]


@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.parametrize(
    'role, has_postcard, client_phone_pd_id, auto_open_postcard, '
    'delivery_status, expected_summary, expected_postcard_title',
    [
        (
            'sender',
            False,
            'phone_pd_id_1',
            False,
            'accepted',
            'Скоро будет',
            'С посланием получателю',
        ),
        (
            'recipient',
            True,
            'phone_pd_id_2',
            True,
            'performer_found',
            'Уже в пути',
            'Вам открытка',
        ),
        (
            'initiator',
            True,
            'phone_pd_id_3',
            False,
            'delivered_finish',
            'Доставлено',
            'С посланием получателю',
        ),
    ],
)
async def test_postcard_in_delivery_state(
        taxi_cargo_c2c,
        create_cargo_c2c_orders,
        default_pa_headers,
        mock_claims_full,
        mock_waybill_info,
        role,
        has_postcard,
        client_phone_pd_id,
        auto_open_postcard,
        delivery_status,
        expected_summary,
        mockserver,
        load_json,
        expected_postcard_title,
):
    @mockserver.json_handler('/cargo-claims/v2/claims/full')
    def _claims_full(request):
        resp = load_json('claim_full_response.json')
        resp['status'] = delivery_status
        return mockserver.make_response(json=resp)

    order_id = await create_cargo_c2c_orders(add_postcard=True)
    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={'delivery_id': 'cargo-c2c/' + order_id},
        headers=default_pa_headers(client_phone_pd_id),
    )
    assert response.status_code == 200
    resp = response.json()
    resp.pop('etag')

    assert resp['state']['meta']['roles'] == [role]
    assert ('postcard' in resp['state'].keys()) == has_postcard

    if has_postcard:
        assert (
            resp['state']['postcard']['cell_title'] == expected_postcard_title
        )
        assert resp['state']['postcard']['content']['type'] == 'bitmap'
        assert 'url' in resp['state']['postcard']['content'].keys()

        assert (
            resp['state']['postcard']['summary_postcard'] == expected_summary
        )
        assert resp['state']['postcard']['user_message'] == 'hi, buddy!'

        response = await taxi_cargo_c2c.post(
            '/4.0/cargo-c2c/v1/deliveries',
            json={
                'deliveries': [
                    {
                        'delivery_id': 'cargo-c2c/' + order_id,
                        'etag': 'some_etag',
                    },
                ],
            },
            headers=default_pa_headers(client_phone_pd_id),
        )
        assert response.status_code == 200
        assert (
            response.json()['deliveries'][0]['state']['context'][
                'auto_open_postcard'
            ]
            == auto_open_postcard
        )


@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.parametrize(
    'claim_status',
    [
        'cancelled',
        'cancelled_with_payment',
        'cancelled_with_items_on_hands',
        'cancelled_by_taxi',
        'failed',
        'performer_not_found',
        'returning',
    ],
)
async def test_postcard_delivery_failed(
        taxi_cargo_c2c,
        create_cargo_c2c_orders,
        default_pa_headers,
        mock_claims_full,
        mock_waybill_info,
        mockserver,
        load_json,
        claim_status,
):
    @mockserver.json_handler('/cargo-claims/v2/claims/full')
    def _claims_full(request):
        resp = load_json('claim_full_response.json')
        resp['status'] = claim_status
        return mockserver.make_response(json=resp)

    order_id = await create_cargo_c2c_orders(add_postcard=True)
    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={'delivery_id': 'cargo-c2c/' + order_id},
        headers=default_pa_headers('phone_pd_id_2'),
    )
    assert response.status_code == 200
    assert (
        response.json()['state']['postcard']['summary_postcard'] == 'Отменено'
    )


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_c2c_deliveries_handler_control',
    consumers=['cargo-c2c/deliveries'],
    clauses=[],
    default_value={'enabled': True},
    is_config=True,
)
async def test_postcard_in_delivery_state_no_exp(
        taxi_cargo_c2c,
        create_cargo_c2c_orders,
        default_pa_headers,
        mock_claims_full,
        mock_waybill_info,
        mockserver,
        load_json,
):
    @mockserver.json_handler('/cargo-claims/v2/claims/full')
    def _claims_full(request):
        resp = load_json('claim_full_response.json')
        resp['status'] = 'performer_found'
        return mockserver.make_response(json=resp)

    order_id = await create_cargo_c2c_orders(add_postcard=True)
    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/delivery/state',
        json={'delivery_id': 'cargo-c2c/' + order_id},
        headers=default_pa_headers('phone_pd_id_3'),
    )
    assert response.status_code == 200
    resp = response.json()
    assert 'postcard' not in resp['state'].keys()

    response = await taxi_cargo_c2c.post(
        '/4.0/cargo-c2c/v1/deliveries',
        json={
            'deliveries': [
                {'delivery_id': 'cargo-c2c/' + order_id, 'etag': 'some_etag'},
            ],
        },
        headers=default_pa_headers('phone_pd_id_3'),
    )
    assert response.status_code == 200
    assert not response.json()['deliveries'][0]['state']['context'][
        'auto_open_postcard'
    ]


@pytest.mark.parametrize('add_postcard', [True, False])
async def test_download_url_stq(
        stq_runner,
        stq,
        mock_claims_full,
        mock_waybill_info,
        create_cargo_c2c_orders,
        pgsql,
        add_postcard,
        get_default_draft_request,
):
    order_id = await create_cargo_c2c_orders(add_postcard=add_postcard)

    await stq_runner.cargo_c2c_postcard_download_url.call(
        task_id='1', args=[order_id, 'phone_pd_id_3'],
    )

    cursor = pgsql['cargo_c2c'].cursor()
    query = 'SELECT s3_path, order_id FROM cargo_c2c.postcards'
    cursor.execute(query)
    rows = list(cursor)

    if add_postcard:
        assert rows[0] == (matching.AnyString(), order_id)
    else:
        assert rows == []


@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.parametrize(
    'app_version, notification_id, push_title_key, push_title_body',
    [
        (
            '4.60.0',
            'cargo_c2c_recipient_delivery_with_postcard',
            'c2c.push.recipient.new_order_with_postcard',
            'c2c.push.recipient.new_order_with_postcard',
        ),
        (
            '4.50.0',
            'cargo_c2c_recipient_delivery_with_postcard',
            'c2c.push.recipient.new_order_postcard_old_client',
            'c2c.push.recipient.new_order_postcard_old_client',
        ),
    ],
)
@pytest.mark.config(
    CARGO_SMS_SENDER_BY_COUNTRY={'rus': 'go'},
    CARGO_C2C_SENDER_BY_BRAND={'yataxi': 'go'},
    CARGO_C2C_NEW_DELIVERY_SMS_SETTINGS=[
        {
            'settings': {
                'role': 'recipient',
                'tariff_class': 'courier',
                'door_to_door': True,
            },
            'tanker_key': 'courier.sms.to_reciever',
            'keyset': 'notify',
        },
        {
            'settings': {
                'role': 'sender',
                'tariff_class': 'courier',
                'door_to_door': True,
            },
            'tanker_key': 'courier.sms.to_sender',
            'keyset': 'notify',
        },
    ],
)
async def test_new_order_with_postcard_recipient_push(
        taxi_cargo_c2c,
        create_cargo_c2c_orders,
        default_pa_headers,
        mock_c2c_save,
        stq,
        stq_runner,
        mock_claims_full,
        mock_waybill_info,
        load_json,
        mockserver,
        order_processing_order_create_requested,
        app_version,
        notification_id,
        push_title_key,
        push_title_body,
):
    @mockserver.json_handler('/cargo-claims/v2/claims/full')
    def _mock_trace(request):
        resp = load_json('claim_full_response.json')
        resp['c2c_data']['cargo_c2c_order_id'] = order_id
        return resp

    @mockserver.json_handler('/user-api/v3/userinfo')
    def _user_info_v3(request):
        return {
            'id': request.json['id'],
            'token_only': True,
            'authorized': True,
            'phone': {
                'id': 'q07823gd45378d094837092d80349',
                'personal_id': 'q07823gd45378d094837092d80349',
            },
            'application': 'iphone',
            'application_version': app_version,
        }

    order_id = await create_cargo_c2c_orders(add_postcard=True)

    mock_c2c_save.empty_orders_on_first_call = True

    response = await taxi_cargo_c2c.post(
        '/v1/processing/cargo-c2c/process-event',
        json={
            'claim_id': order_id,
            'status': 'performer_found',
            'current_point_id': 661931,
        },
    )
    assert response.status_code == 200

    expected_notify_kwargs = build_notify_stq_kwards(
        'phone_pd_id_2',
        order_id,
        'recipient',
        'performer_found',
        'delivery-state-changed',
        notification_id,
        push_title_key,
        push_title_body,
    )
    expected_notify_kwargs['sms_content'] = {
        'text': {
            'args': {
                'sharing_url': 'http://host/some_sharing_key',
                'recipient_address': 'Россия, Москва, Садовническая улица 82',
                'recipient_name': 'string',
            },
            'key': 'courier.sms.to_reciever',
            'keyset': 'notify',
            'locale': 'ru',
        },
    }

    stq['cargo_c2c_send_notification'].next_call()
    assert (
        stq['cargo_c2c_send_notification'].next_call()['kwargs']
        == expected_notify_kwargs
    )
    assert order_processing_order_create_requested.next_call() == {
        'arg': {
            'data': {
                'order_id': order_id,
                'order_provider_id': 'cargo-c2c',
                'phone_pd_id': 'phone_pd_id_1',
                'roles': ['sender', 'recipient'],
            },
            'kind': 'order-create-requested',
            'trait': 'is-create',
        },
    }
