import json

import pytest


@pytest.fixture(name='mock_xiva')
def _mock_xiva(mockserver):
    @mockserver.json_handler('/xiva/v2/send')
    def _send(request):
        return mockserver.make_response(
            'OK', 200, headers={'TransitID': 'bulk'},
        )

    @mockserver.json_handler('/xiva/v2/batch_send')
    def _batch_send(request):
        response = {
            'results': [
                {'code': 200, 'body': 'OK'},
                {'code': 200, 'body': {'text': 'OK'}},
            ],
        }
        return mockserver.make_response(
            json.dumps(response), 200, headers={'TransitID': 'bulk'},
        )


@pytest.fixture(name='mock_user_api')
def _mock_user_api(mockserver):
    @mockserver.json_handler('/user-api/users/get')
    def _users_get(request):
        responses = {
            'user_1': json.dumps(
                {
                    'id': 'user_1',
                    'gcm_token': '1',
                    'application': 'android',
                    'application_version': '4.0.0',
                },
            ),
            'user_2': json.dumps(
                {
                    'id': 'user_2',
                    'application': 'iphone',
                    'application_version': '4.0.0',
                },
            ),
            'user_3': json.dumps(
                {
                    'id': 'user_3',
                    'application': 'iphone',
                    'application_version': '4.0.0',
                },
            ),
        }
        return mockserver.make_response(responses[request.json['id']], 200)


async def _acknowledge(taxi_ucommunications, db, user_id):
    n_acks = db.user_notification_ack_queue.count()
    assert n_acks > 0

    n_user_acks = db.user_notification_ack_queue.count({'user_id': user_id})
    assert n_user_acks == 1

    ack = db.user_notification_ack_queue.find_one({'user_id': user_id})
    assert ack is not None
    assert ack['bulk_id']

    if user_id == 'user_1':
        assert ack['application'] == 'android'
    elif user_id == 'user_2':
        assert ack['application'] == 'iphone'
    elif user_id == 'user_3':
        assert ack['application'] == 'iphone'

    response = await taxi_ucommunications.post(
        'user/notification/acknowledge',
        json={'id': user_id, 'push_id': ack['bulk_id']},
    )
    assert response.status_code == 200
    assert response.json() == {}

    assert db.user_notification_ack_queue.count() == n_acks - 1
    assert (
        db.user_notification_ack_queue.count({'user_id': user_id})
        == n_user_acks - 1
    )


@pytest.mark.config(
    COMMUNICATIONS_USER_NOTIFICATION_ACK_ENABLED=True,
    COMMUNICATIONS_USER_NOTIFICATION_AUTODETECT_XIVA_SERVICE=True,
)
async def test_single_ack(
        taxi_ucommunications, testpoint, mongodb, mock_xiva, mock_user_api,
):
    @testpoint('write-ack-queue-finish')
    def write_ack_queue_finish(data):
        pass

    mongodb.user_notification_ack_queue.remove()
    assert mongodb.user_notification_ack_queue.count() == 0

    response = await taxi_ucommunications.post(
        'user/notification/push',
        json={'user': 'user_1', 'data': {}, 'intent': 'test'},
    )
    assert response.status_code == 200
    await write_ack_queue_finish.wait_call()

    response = await taxi_ucommunications.post(
        'user/notification/push',
        json={'user': 'user_2', 'data': {}, 'intent': 'test'},
    )
    assert response.status_code == 200
    await write_ack_queue_finish.wait_call()

    assert mongodb.user_notification_ack_queue.count() == 2

    await _acknowledge(taxi_ucommunications, mongodb, 'user_1')
    await _acknowledge(taxi_ucommunications, mongodb, 'user_2')


@pytest.mark.config(
    COMMUNICATIONS_USER_NOTIFICATION_ACK_ENABLED=True,
    COMMUNICATIONS_USER_NOTIFICATION_AUTODETECT_XIVA_SERVICE=True,
)
async def test_bulk_ack(
        taxi_ucommunications, testpoint, mongodb, mock_xiva, mock_user_api,
):
    @testpoint('write-ack-queue-finish')
    def write_ack_queue_finish(data):
        pass

    mongodb.user_notification_ack_queue.remove()
    assert mongodb.user_notification_ack_queue.count() == 0

    response = await taxi_ucommunications.post(
        'user/notification/bulk-push',
        json={
            'intent': 'test',
            'data': {'payload': {'msg': 'Message', 'title': 'Title'}},
            'recipients': [
                {
                    'user_id': 'user_1',
                    'data': {'payload': {'msg': 'Personal'}},
                },
                {'user_id': 'user_2'},
                {'user_id': 'user_3'},
            ],
        },
    )
    assert response.status_code == 200

    # wait PutAsync() write 2 bulks in db
    for _ in range(2):
        await write_ack_queue_finish.wait_call()
    assert mongodb.user_notification_ack_queue.count() == 3
    ack1 = mongodb.user_notification_ack_queue.find_one({'user_id': 'user_1'})
    ack2 = mongodb.user_notification_ack_queue.find_one({'user_id': 'user_2'})
    ack3 = mongodb.user_notification_ack_queue.find_one({'user_id': 'user_3'})
    assert ack1 is not None and ack2 is not None and ack3 is not None
    assert ack2['bulk_id'] != ack1['bulk_id']
    assert ack2['bulk_id'] == ack3['bulk_id']

    await _acknowledge(taxi_ucommunications, mongodb, 'user_1')
    await _acknowledge(taxi_ucommunications, mongodb, 'user_2')
    await _acknowledge(taxi_ucommunications, mongodb, 'user_3')


@pytest.mark.config(
    COMMUNICATIONS_USER_NOTIFICATION_ACK_ENABLED=True,
    COMMUNICATIONS_USER_NOTIFICATION_AUTODETECT_XIVA_SERVICE=True,
    COMMUNICATIONS_USER_NOTIFICATION_INTENTS={
        'prefix_enabled': {'bulk_id_prefix_enabled': True},
        'prefix_disabled': {'bulk_id_prefix_enabled': False},
        'prefix_not_specified': {},
    },
)
@pytest.mark.parametrize(
    'intent,bulk_id,expected_prefix',
    [
        ['prefix_enabled', None, 'ga:'],
        ['prefix_disabled', None, None],
        ['prefix_not_specified', None, 'ga:'],
        ['prefix_not_specified', 'bulk_id', None],
    ],
    ids=['has_prefix_forced', 'no_prefix_forced', 'has_prefix', 'no_prefix'],
)
async def test_bulk_id_prefix(
        taxi_ucommunications,
        testpoint,
        mongodb,
        mock_xiva,
        mock_user_api,
        intent,
        bulk_id,
        expected_prefix,
):
    @testpoint('write-ack-queue-finish')
    def write_ack_queue_finish(data):
        pass

    mongodb.user_notification_ack_queue.remove()

    response = await taxi_ucommunications.post(
        'user/notification/push',
        json={
            'user': 'user_1',
            'data': {'payload': {'id': bulk_id}},
            'intent': intent,
        },
    )
    assert response.status_code == 200
    await write_ack_queue_finish.wait_call()

    ack = mongodb.user_notification_ack_queue.find_one({'user_id': 'user_1'})
    assert ack is not None
    if expected_prefix:
        assert ack['bulk_id'].startswith(expected_prefix)
    else:
        assert ':' not in ack['bulk_id']


@pytest.mark.config(
    COMMUNICATIONS_USER_NOTIFICATION_ACK_ENABLED=True,
    COMMUNICATIONS_USER_NOTIFICATION_ACK_LOOKUP_ENABLED=False,
    COMMUNICATIONS_USER_NOTIFICATION_AUTODETECT_XIVA_SERVICE=True,
    COMMUNICATIONS_USER_NOTIFICATION_INTENTS={
        'prefix_enabled': {'bulk_id_prefix_enabled': True},
        'prefix_disabled': {'bulk_id_prefix_enabled': False},
        'prefix_not_specified': {},
    },
)
@pytest.mark.parametrize(
    'intent,ack_lookup_enabled',
    [
        ['prefix_enabled', True],
        ['prefix_disabled', False],
        ['prefix_not_specified', True],
    ],
    ids=['has_prefix', 'no_prefix', 'notset_prefix'],
)
async def test_ack_lookup(
        taxi_ucommunications,
        testpoint,
        mongodb,
        mock_xiva,
        mock_user_api,
        intent,
        ack_lookup_enabled,
):
    @testpoint('write-ack-queue-finish')
    def write_ack_queue_finish(data):
        pass

    mongodb.user_notification_ack_queue.remove()

    response = await taxi_ucommunications.post(
        'user/notification/push',
        json={'user': 'user_1', 'data': {}, 'intent': intent},
    )
    assert response.status_code == 200
    await write_ack_queue_finish.wait_call()

    ack = mongodb.user_notification_ack_queue.find_one({'user_id': 'user_1'})
    assert ack is not None

    response = await taxi_ucommunications.post(
        'user/notification/acknowledge',
        json={'id': 'user_1', 'push_id': ack['bulk_id']},
    )
    assert response.status_code == 200
    assert response.json() == {}

    n_acks = mongodb.user_notification_ack_queue.count({'user_id': 'user_1'})
    if ack_lookup_enabled:
        assert n_acks == 0
    else:
        assert n_acks == 1


@pytest.mark.config(
    COMMUNICATIONS_USER_NOTIFICATION_ACK_SHORT_CIRCUIT_ENABLED=True,
    COMMUNICATIONS_USER_NOTIFICATION_ACK_ENABLED=True,
    COMMUNICATIONS_USER_NOTIFICATION_AUTODETECT_XIVA_SERVICE=True,
)
async def test_ack_short_circuit(
        taxi_ucommunications, testpoint, mongodb, mock_xiva, mock_user_api,
):
    @testpoint('write-ack-queue-finish')
    def write_ack_queue_finish(data):
        pass

    mongodb.user_notification_ack_queue.remove()

    response = await taxi_ucommunications.post(
        'user/notification/push',
        json={'user': 'user_1', 'data': {}, 'intent': 'test'},
    )
    assert response.status_code == 200
    await write_ack_queue_finish.wait_call()

    ack = mongodb.user_notification_ack_queue.find_one({'user_id': 'user_1'})
    assert ack is not None

    response = await taxi_ucommunications.post(
        'user/notification/acknowledge',
        json={'id': 'user_1', 'push_id': ack['bulk_id']},
    )
    assert response.status_code == 200
    assert response.json() == {}

    assert (
        mongodb.user_notification_ack_queue.count({'user_id': 'user_1'}) == 1
    )


@pytest.mark.config(
    COMMUNICATIONS_USER_NOTIFICATION_ACK_ENABLED=True,
    COMMUNICATIONS_USER_NOTIFICATION_AUTODETECT_XIVA_SERVICE=True,
)
async def test_callback(
        taxi_ucommunications,
        testpoint,
        mongodb,
        mock_xiva,
        mock_user_api,
        mockserver,
):
    @testpoint('write-ack-queue-finish')
    def write_ack_queue_finish(data):
        pass

    @mockserver.json_handler('/communication-scenario/v1/report-event')
    def _mock_callback_service(request):
        assert request.url == url
        return {}

    mongodb.user_notification_ack_queue.remove()

    url = mockserver.url(
        '/communication-scenario/v1/report-event?'
        'event_name=delivered&event_id=bulk_1',
    )
    response = await taxi_ucommunications.post(
        'user/notification/push',
        json={
            'user': 'user_1',
            'data': {},
            'intent': 'test',
            'callback': {
                'url': url,
                'tvm_name': 'communication-scenario',
                'timeout_ms': 500,
                'attemts': 2,
            },
        },
    )

    assert response.status_code == 200
    await write_ack_queue_finish.wait_call()

    ack = mongodb.user_notification_ack_queue.find_one({'user_id': 'user_1'})
    response = await taxi_ucommunications.post(
        'user/notification/acknowledge',
        json={'id': 'user_1', 'push_id': ack['bulk_id']},
    )
    await _mock_callback_service.wait_call()
