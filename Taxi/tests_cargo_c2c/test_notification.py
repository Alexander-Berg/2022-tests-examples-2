import pytest


PUSH_PAYLOAD = {'logistics': {'type': 'some_type'}}

PUSH_CONTENT = {
    'title': {
        'key': 'b2c.push.recipient.new_order.title',
        'keyset': 'cargo',
        'locale': 'ru',
    },
    'body': {
        'key': 'b2c.push.recipient.new_order.body',
        'keyset': 'cargo',
        'locale': 'ru',
        'args': {
            'corp_client_name': 'Рога и копыта',
            'corp_client_name_ru_genitive': 'Рогов и Копыт',
        },
    },
}

SMS_CONTENT = {
    'text': {
        'key': 'b2c.push.recipient.new_order.title',
        'keyset': 'cargo',
        'locale': 'ru',
    },
}


@pytest.fixture(name='mock_ucommunications_push')
def _mock_ucommunications_push(
        mockserver, build_ucommunications_body, get_default_order_id,
):
    @mockserver.json_handler('/ucommunications/user/notification/push')
    def _push(request):
        if context.expected_request:
            assert request.json == context.expected_request
        return {}

    class Context:
        def __init__(self):
            self.expected_request = None
            self.handler = _push

    context = Context()
    return context


@pytest.fixture(name='mock_ucommunications_sms')
def _mock_ucommunications_sms(mockserver):
    @mockserver.json_handler('/ucommunications/user/sms/send')
    def _sms(request):
        if context.expected_request:
            assert request.json == context.expected_request
        return {'code': '200', 'message': '200'}

    class Context:
        def __init__(self):
            self.expected_request = None
            self.handler = _sms

    context = Context()
    return context


@pytest.fixture(autouse=True)
def _mock_user_api(mockserver):
    @mockserver.json_handler('/user-api/v3/userinfo')
    def _user_info(request):
        return {
            'id': request.json['id'],
            'token_only': True,
            'authorized': True,
            'application': 'iphone',
            'application_version': '4.90.0',
        }


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_c2c_push_control',
    consumers=['cargo-c2c/push_control'],
    clauses=[],
    default_value={
        'enabled': True,
        'ttl_seconds': 30,
        'notification_type': 'push',
    },
    is_config=True,
)
@pytest.mark.config(
    ORDER_ROUTE_SHARING_SUPPORTED_CORPS={
        '5e36732e2bc54e088b1466e08e31c486': {
            'en': 'R&G',
            'ru': 'Рога и копыта',
            'ru_genitive': 'Рогов и Копытов',
        },
    },
)
async def test_send_push(
        taxi_cargo_c2c,
        stq_runner,
        mockserver,
        create_cargo_claims_orders,
        get_default_order_id,
        mock_ucommunications_push,
        mock_ucommunications_sms,
        taxi_cargo_c2c_monitor,
):
    title = 'Сегодня вам приедет доставка'
    body = 'Отслеживайте статус заказа из Рогов и Копыт'
    mock_ucommunications_push.expected_request = {
        'user': 'user_id_1_2',
        'ttl': 30,
        'intent': 'some_push',
        'data': {
            'payload': PUSH_PAYLOAD,
            'repack': {
                'apns': {
                    'aps': {
                        'alert': {'body': body, 'title': title},
                        'content-available': 1,
                        'thread-id': f'cargo-claims/{get_default_order_id()}',
                    },
                },
                'gcm': {'notification': {'title': title, 'body': body}},
                'hms': {'notification': {'title': title, 'body': body}},
            },
        },
        'meta': {
            'order_id': get_default_order_id(),
            'order_provider_id': 'cargo-claims',
            'phone_pd_id': 'phone_pd_id_1',
            'type': 'cargo-c2c',
        },
    }

    await stq_runner.cargo_c2c_send_notification.call(
        task_id='1',
        args=[
            {
                'phone_pd_id': 'phone_pd_id_1',
                'order_id': get_default_order_id(),
                'order_provider_id': 'cargo-claims',
            },
            'some_push',
            None,
            None,
            PUSH_PAYLOAD,
            PUSH_CONTENT,
            None,
        ],
    )

    assert mock_ucommunications_push.handler.times_called == 1
    assert mock_ucommunications_sms.handler.times_called == 0

    stats = await taxi_cargo_c2c_monitor.get_metric('pushes-or-sms-sent')
    assert stats['push'] == {'some_push': 1}


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_c2c_push_control',
    consumers=['cargo-c2c/push_control'],
    clauses=[],
    default_value={
        'enabled': True,
        'ttl_seconds': 30,
        'notification_type': 'sms',
    },
    is_config=True,
)
async def test_send_sms(
        taxi_cargo_c2c,
        stq_runner,
        mockserver,
        create_cargo_claims_orders,
        get_default_order_id,
        mock_ucommunications_push,
        mock_ucommunications_sms,
        taxi_cargo_c2c_monitor,
):
    mock_ucommunications_sms.expected_request = {
        'intent': 'some_sms',
        'phone_id': 'phone_pd_id_1',
        'text': 'Сегодня вам приедет доставка',
        'meta': {
            'order_id': get_default_order_id(),
            'order_provider_id': 'cargo-claims',
            'phone_pd_id': 'phone_pd_id_1',
            'type': 'cargo-c2c',
        },
    }

    await stq_runner.cargo_c2c_send_notification.call(
        task_id='1',
        args=[
            {
                'phone_pd_id': 'phone_pd_id_1',
                'order_id': get_default_order_id(),
                'order_provider_id': 'cargo-claims',
            },
            'some_sms',
            None,
            None,
            None,
            None,
            SMS_CONTENT,
        ],
    )

    assert mock_ucommunications_push.handler.times_called == 0
    assert mock_ucommunications_sms.handler.times_called == 1

    stats = await taxi_cargo_c2c_monitor.get_metric('pushes-or-sms-sent')
    assert stats['sms'] == {'some_sms': 1}


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_c2c_push_control',
    consumers=['cargo-c2c/push_control'],
    clauses=[],
    default_value={
        'enabled': True,
        'ttl_seconds': 30,
        'notification_type': 'push_instead_of_sms',
    },
    is_config=True,
)
async def test_send_push_or_sms(
        taxi_cargo_c2c,
        stq_runner,
        mockserver,
        create_cargo_claims_orders,
        get_default_order_id,
        mock_ucommunications_push,
        mock_ucommunications_sms,
        taxi_cargo_c2c_monitor,
):
    mock_ucommunications_sms.expected_request = {
        'intent': 'some_push',
        'user_id': 'user_id_1_2',
        'text': 'Сегодня вам приедет доставка',
        'notification': {
            'text': 'Отслеживайте статус заказа из Рогов и Копыт',
            'title': 'Сегодня вам приедет доставка',
        },
        'meta': {
            'order_id': get_default_order_id(),
            'order_provider_id': 'cargo-claims',
            'phone_pd_id': 'phone_pd_id_1',
            'type': 'cargo-c2c',
        },
    }

    await stq_runner.cargo_c2c_send_notification.call(
        task_id='1',
        args=[
            {
                'phone_pd_id': 'phone_pd_id_1',
                'order_id': get_default_order_id(),
                'order_provider_id': 'cargo-claims',
            },
            'some_push',
            None,
            None,
            PUSH_PAYLOAD,
            PUSH_CONTENT,
            SMS_CONTENT,
        ],
    )

    assert mock_ucommunications_push.handler.times_called == 0
    assert mock_ucommunications_sms.handler.times_called == 1

    stats = await taxi_cargo_c2c_monitor.get_metric('pushes-or-sms-sent')
    assert stats['push-or-sms'] == {'some_push': 1}


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_c2c_push_control',
    consumers=['cargo-c2c/push_control'],
    clauses=[
        {
            'title': '1',
            'predicate': {
                'init': {
                    'predicates': [
                        {
                            'init': {
                                'arg_name': 'application',
                                'arg_type': 'string',
                                'value': 'iphone',
                            },
                            'type': 'eq',
                        },
                        {
                            'init': {
                                'arg_name': 'application_version',
                                'arg_type': 'string',
                                'value': '2',
                            },
                            'type': 'gt',
                        },
                    ],
                },
                'type': 'all_of',
            },
            'value': {
                'enabled': True,
                'ttl_seconds': 30,
                'notification_type': 'push',
            },
        },
    ],
    default_value={'enabled': False},
    is_config=True,
)
async def test_experiment(
        taxi_cargo_c2c,
        stq_runner,
        mockserver,
        create_cargo_claims_orders,
        get_default_order_id,
        mock_ucommunications_push,
        mock_ucommunications_sms,
):
    await stq_runner.cargo_c2c_send_notification.call(
        task_id='1',
        args=[
            {
                'phone_pd_id': 'phone_pd_id_1',
                'order_id': get_default_order_id(),
                'order_provider_id': 'cargo-claims',
            },
            'some_push',
            None,
            None,
            PUSH_PAYLOAD,
            PUSH_CONTENT,
            SMS_CONTENT,
        ],
    )

    assert mock_ucommunications_push.handler.times_called == 0
    assert mock_ucommunications_sms.handler.times_called == 0


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_c2c_push_control',
    consumers=['cargo-c2c/push_control'],
    clauses=[],
    default_value={
        'enabled': True,
        'ttl_seconds': 30,
        'notification_type': 'sms',
    },
    is_config=True,
)
@pytest.mark.config(CARGO_C2C_PUSH_CONTROL={'exec_max_tries': 3})
async def test_retries(
        taxi_cargo_c2c,
        stq_runner,
        mockserver,
        get_default_order_id,
        create_cargo_claims_orders,
):
    @mockserver.json_handler('/ucommunications/user/sms/send')
    def _sms(request):
        return mockserver.make_response(
            json={'code': '500', 'message': '500'}, status=500,
        )

    await stq_runner.cargo_c2c_send_notification.call(
        task_id='1',
        args=[
            {
                'phone_pd_id': 'phone_pd_id_1',
                'order_id': get_default_order_id(),
                'order_provider_id': 'cargo-claims',
            },
            'some_push',
            None,
            None,
            PUSH_PAYLOAD,
            PUSH_CONTENT,
            SMS_CONTENT,
        ],
        expect_fail=True,
        exec_tries=0,
    )

    await stq_runner.cargo_c2c_send_notification.call(
        task_id='1',
        args=[
            {
                'phone_pd_id': 'phone_pd_id_1',
                'order_id': get_default_order_id(),
                'order_provider_id': 'cargo-claims',
            },
            'some_push',
            None,
            None,
            PUSH_PAYLOAD,
            PUSH_CONTENT,
            SMS_CONTENT,
        ],
        expect_fail=False,
        exec_tries=4,
    )


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_c2c_push_control',
    consumers=['cargo-c2c/push_control'],
    clauses=[],
    default_value={
        'enabled': True,
        'ttl_seconds': 30,
        'notification_type': 'push',
    },
    is_config=True,
)
async def test_send_silent_push(
        taxi_cargo_c2c,
        stq_runner,
        create_cargo_claims_orders,
        get_default_order_id,
        mockserver,
        mock_ucommunications_push,
        mock_ucommunications_sms,
):
    silent_push_payload = {
        'payload': {
            'logistics': {'type': 'journal-updated', 'silent_push': True},
        },
    }
    mock_ucommunications_push.expected_request = {
        'user': 'user_id_1_2',
        'data': {
            'payload': silent_push_payload,
            'repack': {
                'apns': {'aps': {'content-available': 1}},
                'gcm': {},
                'hms': {},
            },
        },
        'intent': 'some_push',
        'ttl': 30,
        'meta': {
            'order_id': get_default_order_id(),
            'order_provider_id': 'cargo-claims',
            'phone_pd_id': 'phone_pd_id_1',
            'type': 'cargo-c2c',
        },
    }

    await stq_runner.cargo_c2c_send_notification.call(
        task_id='1',
        args=[
            {
                'phone_pd_id': 'phone_pd_id_1',
                'order_id': get_default_order_id(),
                'order_provider_id': 'cargo-claims',
            },
            'some_push',
            None,
            None,
            silent_push_payload,
            None,
            None,
        ],
    )

    assert mock_ucommunications_push.handler.times_called == 1
    assert mock_ucommunications_sms.handler.times_called == 0


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_c2c_push_control',
    consumers=['cargo-c2c/push_control'],
    clauses=[],
    default_value={
        'enabled': True,
        'ttl_seconds': 30,
        'notification_type': 'push_and_sms',
    },
    is_config=True,
)
async def test_send_push_and_sms(
        taxi_cargo_c2c,
        stq_runner,
        mockserver,
        create_cargo_claims_orders,
        get_default_order_id,
        mock_ucommunications_push,
        mock_ucommunications_sms,
        taxi_cargo_c2c_monitor,
):
    mock_ucommunications_sms.expected_request = {
        'intent': 'some_push_and_sms',
        'phone_id': 'phone_pd_id_1',
        'text': 'Сегодня вам приедет доставка',
        'meta': {
            'order_id': get_default_order_id(),
            'order_provider_id': 'cargo-claims',
            'phone_pd_id': 'phone_pd_id_1',
            'type': 'cargo-c2c',
        },
    }

    title = 'Сегодня вам приедет доставка'
    body = 'Отслеживайте статус заказа из Рогов и Копыт'
    mock_ucommunications_push.expected_request = {
        'user': 'user_id_1_2',
        'ttl': 30,
        'intent': 'some_push_and_sms',
        'data': {
            'payload': PUSH_PAYLOAD,
            'repack': {
                'apns': {
                    'aps': {
                        'alert': {'body': body, 'title': title},
                        'content-available': 1,
                        'thread-id': f'cargo-claims/{get_default_order_id()}',
                    },
                },
                'gcm': {'notification': {'title': title, 'body': body}},
                'hms': {'notification': {'title': title, 'body': body}},
            },
        },
        'meta': {
            'order_id': get_default_order_id(),
            'order_provider_id': 'cargo-claims',
            'phone_pd_id': 'phone_pd_id_1',
            'type': 'cargo-c2c',
        },
    }

    await stq_runner.cargo_c2c_send_notification.call(
        task_id='1',
        args=[
            {
                'phone_pd_id': 'phone_pd_id_1',
                'order_id': get_default_order_id(),
                'order_provider_id': 'cargo-claims',
            },
            'some_push_and_sms',
            None,
            None,
            PUSH_PAYLOAD,
            PUSH_CONTENT,
            SMS_CONTENT,
        ],
    )

    assert mock_ucommunications_push.handler.times_called == 1
    assert mock_ucommunications_sms.handler.times_called == 1

    stats = await taxi_cargo_c2c_monitor.get_metric('pushes-or-sms-sent')
    assert stats['push-and-sms'] == {'some_push_and_sms': 1}
