import pytest


HEADERS = {'X-Idempotency-Token': 'token'}

QUERY = {
    'consumer': 'quality-control-cpp',
    'consumer_provider': 'contractor-quality-control',
}

PUSH = {'intent': 'MessageNew', 'code': 100}

PAYLOAD = {
    'text': 'Текст',
    'title': 'Заголовок',
    'link': 'Ссылка',
    'sound': 'Звук',
    'new_field': 'Примеры payload см в taxi_feeds api',
    'extra': {'new_field': 'Перекладываем как есть'},
}


@pytest.fixture
def feeds(mockserver, contractors, expire, filtered):
    @mockserver.json_handler('/feeds/v1/create')
    def _create(request):
        channels = request.json['channels']
        service = request.json['service']
        if 'expire' in request.json:
            req_expire = request.json['expire']
            assert req_expire == expire
        expected_channels = []
        for contractor in contractors:
            expected_contractor = {
                'channel': make_channel_from_contractor(contractor),
            }
            if 'payload_overrides' in contractor:
                expected_contractor['payload_overrides'] = contractor[
                    'payload_overrides'
                ]
            expected_channels.append(expected_contractor)
        assert channels == expected_channels
        assert request.json['ignore_filters']
        return mockserver.make_response(
            json={'service': service, 'filtered': filtered, 'feed_ids': {}},
            status=200,
        )


@pytest.fixture
def client_notify(mockserver, contractors, push, expire, payload):
    @mockserver.json_handler('/client-notify/v2/bulk-push')
    def _push(request):
        # required params
        assert 'intent' in request.json
        assert 'service' in request.json
        assert 'recipients' in request.json

        assert request.json['intent'] == push['intent']
        assert request.json['service'] == 'taximeter'
        assert request.json['recipients'] == make_drivers_from_contractors(
            contractors,
        )

        # additional params
        if expire is not None:
            assert request.json['ttl'] == 180

        if 'text' in payload:
            assert (
                request.json['notification']['text'] == f'"{payload["text"]}"'
            )
        if 'title' in payload:
            assert (
                request.json['notification']['title']
                == f'"{payload["title"]}"'
            )
        if 'sound' in payload:
            assert (
                request.json['notification']['sound']
                == f'"{payload["sound"]}"'
            )
        if 'link' in payload:
            assert (
                request.json['notification']['link'] == f'"{payload["link"]}"'
            )

        # why so: see client_notify.cpp
        assert request.json['data'] == PAYLOAD

        notification_ids = [
            {'notification_id': f'id{i}'} for i in range(len(contractors))
        ]
        return mockserver.make_response(
            status=200, json={'notifications': notification_ids},
        )


def make_channel_from_contractor(contractor):
    return (
        'contractor:'
        + contractor['park_id']
        + ':'
        + contractor['contractor_profile_id']
    )


def make_drivers_from_contractors(contractors):
    recipients = []
    for contractor in contractors:
        recipient = {
            'client_id': (
                f'{contractor["park_id"]}-'
                f'{contractor["contractor_profile_id"]}'
            ),
        }
        if 'payload_overrides' in contractor:
            for key, value in contractor['payload_overrides'].items():
                if key in ['text', 'title', 'sound', 'link']:
                    if 'notification' not in recipient:
                        recipient['notification'] = {}
                    recipient['notification'][key] = f'"{value}"'
                if 'data' not in recipient:
                    recipient['data'] = {}
                recipient['data'][key] = value
        recipients.append(recipient)
    return recipients


def make_failed_post(filtered, contractors):
    result = []
    for contractor in contractors:
        channel = {'channel': make_channel_from_contractor(contractor)}
        if channel in filtered:
            result.append(contractor)
    return result


@pytest.mark.parametrize(
    'expire, contractors, filtered',
    [
        (
            None,
            [{'park_id': 'park_id1', 'contractor_profile_id': 'profile_id1'}],
            [],
        ),
        (
            None,
            [
                {
                    'park_id': 'park_id1',
                    'contractor_profile_id': 'profile_id1',
                    'payload_overrides': {'kek': 'kek'},
                },
            ],
            [],
        ),
        (
            '2020-06-01T06:35:00+00:00',
            [{'park_id': 'park_id1', 'contractor_profile_id': 'profile_id1'}],
            [{'channel': 'contractor:park_id1:profile_id1'}],
        ),
        (
            '2020-06-01T06:35:00+00:00',
            [
                {
                    'park_id': 'park_id1',
                    'contractor_profile_id': 'profile_id1',
                },
                {
                    'park_id': 'park_id2',
                    'contractor_profile_id': 'profile_id2',
                },
            ],
            [{'channel': 'contractor:park_id1:profile_id1'}],
        ),
        (
            '2020-06-01T06:35:00+00:00',
            [
                {
                    'park_id': 'park_id1',
                    'contractor_profile_id': 'profile_id1',
                },
                {
                    'park_id': 'park_id2',
                    'contractor_profile_id': 'profile_id2',
                },
                {
                    'park_id': 'park_id3',
                    'contractor_profile_id': 'profile_id3',
                },
            ],
            [{'channel': 'contractor:park_id2:profile_id2'}],
        ),
    ],
)
@pytest.mark.config(
    DRIVER_COMMUNICATIONS_CONSUMERS={
        'quality-control-cpp': {
            '__default__': {'service': 'kek', 'limit': 1000},
            'contractor-quality-control': {
                'is_urgent': True,
                'limit': 1000,
                'service': 'feeds',
                'provider': 'contractor-quality-control',
            },
        },
    },
)
@pytest.mark.now('2020-06-01T06:35:00+0000')
async def test_internal_create_post(
        mockserver,
        feeds,  # pylint: disable=W0621
        taxi_driver_communications,
        expire,
        contractors,
        filtered,
):
    body = {
        'options': ['post'],
        'payload': PAYLOAD,
        'contractors': contractors,
    }
    if expire is not None:
        body['expire'] = expire

    response = await taxi_driver_communications.post(
        '/internal/driver-communications/v1/create',
        headers=HEADERS,
        params=QUERY,
        json=body,
    )

    failed_post = make_failed_post(filtered, contractors)
    expected_response = {
        'service': 'feeds',
        'provider': 'contractor-quality-control',
    }
    if failed_post:
        expected_response['failed_post'] = failed_post
    assert response.status_code == 200
    assert response.json() == expected_response


@pytest.mark.parametrize(
    'push, payload, expire, contractors',
    [
        (
            PUSH,
            PAYLOAD,
            None,
            [{'park_id': 'park_id1', 'contractor_profile_id': 'profile_id1'}],
        ),
        (
            PUSH,
            PAYLOAD,
            '2020-06-01T06:38:00+00:00',
            [
                {
                    'park_id': 'park_id1',
                    'contractor_profile_id': 'profile_id1',
                    'payload_overrides': {
                        'text': 'Свой payload',
                        'title': 'Новый заголовок',
                        'link': 'Новая ссылка',
                        'sound': 'Новый звук',
                    },
                },
                {
                    'park_id': 'park_id2',
                    'contractor_profile_id': 'profile_id2',
                    'payload': {  # this driver will have payload from PAYLOAD
                        'text': 'Этот payload будет проигнорирован',
                        'title': 'Чтобы водитель имел этот payload',
                        'link': 'Нужно только...',
                        'sound': 'Заменить payload --> payload_overrides',
                    },
                },
            ],
        ),
        (
            PUSH,
            PAYLOAD,
            None,
            [
                {
                    'park_id': 'park_id1',
                    'contractor_profile_id': 'profile_id1',
                },
                {
                    'park_id': 'park_id2',
                    'contractor_profile_id': 'profile_id2',
                    'payload_overrides': {
                        'text': 'Свой payload',
                        'title': 'Новый заголовок',
                    },
                },
            ],
        ),
        (
            PUSH,
            PAYLOAD,
            None,
            [
                {
                    'park_id': 'park_id1',
                    'contractor_profile_id': 'profile_id1',
                    'payload_overrides': {
                        'text': 'Свой payload для первого водителя',
                        'some_field': 'Свое поле для первого водителя',
                    },
                },
                {
                    'park_id': 'park_id2',
                    'contractor_profile_id': 'profile_id2',
                    'payload_overrides': {
                        'text': 'Свой payload для второго водителя',
                        'extra': {
                            'new_field': 'Свое extra для второго водителя',
                        },
                    },
                },
            ],
        ),
    ],
)
@pytest.mark.config(
    DRIVER_COMMUNICATIONS_CONSUMERS={
        'quality-control-cpp': {
            '__default__': {'service': 'kek', 'limit': 1000},
            'contractor-quality-control': {
                'is_urgent': True,
                'limit': 1000,
                'service': 'feeds',
                'provider': 'contractor-quality-control',
            },
        },
    },
)
@pytest.mark.now('2020-06-01T06:35:00+0000')
async def test_internal_create_push(
        mockserver,
        client_notify,  # pylint: disable=W0621
        taxi_driver_communications,
        push,
        payload,
        contractors,
        expire,
):
    body = {
        'options': ['push'],
        'push': push,
        'payload': payload,
        'contractors': contractors,
    }
    if expire is not None:
        body['expire'] = expire

    response = await taxi_driver_communications.post(
        '/internal/driver-communications/v1/create',
        headers=HEADERS,
        params=QUERY,
        json=body,
    )

    assert response.status_code == 200
    assert response.json() == {
        'service': 'feeds',
        'provider': 'contractor-quality-control',
    }


@pytest.mark.parametrize(
    'expire, push, payload, contractors, filtered',
    [
        (
            '2020-06-01T06:38:00+00:00',
            PUSH,
            PAYLOAD,
            [
                {
                    'park_id': 'park_id1',
                    'contractor_profile_id': 'profile_id1',
                },
                {
                    'park_id': 'park_id2',
                    'contractor_profile_id': 'profile_id2',
                },
            ],
            [{'channel': 'contractor:park_id1:profile_id1'}],
        ),
        (
            '2020-06-01T06:38:00+00:00',
            PUSH,
            PAYLOAD,
            [
                {
                    'park_id': 'park_id1',
                    'contractor_profile_id': 'profile_id1',
                },
                {
                    'park_id': 'park_id2',
                    'contractor_profile_id': 'profile_id2',
                },
            ],
            [],
        ),
    ],
)
@pytest.mark.config(
    DRIVER_COMMUNICATIONS_CONSUMERS={
        'quality-control-cpp': {
            '__default__': {'service': 'kek', 'limit': 1000},
            'contractor-quality-control': {
                'is_urgent': True,
                'limit': 1000,
                'service': 'feeds',
                'provider': 'contractor-quality-control',
            },
        },
    },
)
@pytest.mark.now('2020-06-01T06:35:00+0000')
async def test_internal_create_post_and_push(
        mockserver,
        feeds,  # pylint: disable=W0621
        client_notify,  # pylint: disable=W0621
        taxi_driver_communications,
        expire,
        push,
        payload,
        contractors,
        filtered,
):
    body = {
        'options': ['post', 'push'],
        'push': push,
        'payload': payload,
        'contractors': contractors,
    }
    if expire is not None:
        body['expire'] = expire

    response = await taxi_driver_communications.post(
        '/internal/driver-communications/v1/create',
        headers=HEADERS,
        params=QUERY,
        json=body,
    )

    failed_post = make_failed_post(filtered, contractors)
    expected_response = {
        'service': 'feeds',
        'provider': 'contractor-quality-control',
    }
    if failed_post:
        expected_response['failed_post'] = failed_post
    assert response.status_code == 200
    assert response.json() == expected_response


@pytest.mark.config(
    DRIVER_COMMUNICATIONS_CONSUMERS={
        'quality-control-cpp': {
            '__default__': {'service': 'kek', 'limit': 1000},
            'contractor-quality-control': {
                'is_urgent': True,
                'limit': 1000,
                'service': 'feeds',
                'provider': 'contractor-quality-control',
            },
        },
    },
)
async def test_internal_create_post_feeds_500(
        mockserver, taxi_driver_communications,
):
    @mockserver.json_handler('/feeds/v1/create')
    def _create(request):
        return mockserver.make_response(status=500)

    body = {
        'options': ['post'],
        'payload': PAYLOAD,
        'contractors': [
            {'park_id': 'park_id1', 'contractor_profile_id': 'profile_id1'},
        ],
    }

    response = await taxi_driver_communications.post(
        '/internal/driver-communications/v1/create',
        headers=HEADERS,
        params=QUERY,
        json=body,
    )

    assert response.status_code == 500


@pytest.mark.config(DRIVER_COMMUNICATIONS_CONSUMERS={})
async def test_internal_create_post_wrong_consumer(taxi_driver_communications):
    body = {
        'options': ['post'],
        'payload': PAYLOAD,
        'contractors': [
            {'park_id': 'park_id1', 'contractor_profile_id': 'profile_id1'},
        ],
    }

    response = await taxi_driver_communications.post(
        '/internal/driver-communications/v1/create',
        headers=HEADERS,
        params=QUERY,
        json=body,
    )

    assert response.status_code == 400


@pytest.mark.config(
    DRIVER_COMMUNICATIONS_CONSUMERS={
        'quality-control-cpp': {
            '__default__': {'service': 'kek', 'limit': 1000},
        },
    },
)
async def test_internal_create_post_no_service(
        mockserver, taxi_driver_communications,
):
    body = {
        'options': ['post'],
        'payload': PAYLOAD,
        'contractors': [
            {'park_id': 'park_id1', 'contractor_profile_id': 'profile_id1'},
        ],
    }

    response = await taxi_driver_communications.post(
        '/internal/driver-communications/v1/create',
        headers=HEADERS,
        params=QUERY,
        json=body,
    )

    assert response.status_code == 500


@pytest.mark.config(
    DRIVER_COMMUNICATIONS_CONSUMERS={
        'quality-control-cpp': {
            '__default__': {'service': 'kek', 'limit': 1000},
            'contractor-quality-control': {
                'is_urgent': True,
                'limit': 0,
                'service': 'feeds',
                'provider': 'contractor-quality-control',
            },
        },
    },
)
async def test_internal_create_post_limit_0(
        mockserver, taxi_driver_communications,
):
    body = {
        'options': ['post'],
        'payload': PAYLOAD,
        'contractors': [
            {'park_id': 'park_id1', 'contractor_profile_id': 'profile_id1'},
        ],
    }

    response = await taxi_driver_communications.post(
        '/internal/driver-communications/v1/create',
        headers=HEADERS,
        params=QUERY,
        json=body,
    )

    assert response.status_code == 400


@pytest.mark.config(
    DRIVER_COMMUNICATIONS_CONSUMERS={
        'quality-control-cpp': {
            '__default__': {'service': 'kek', 'limit': 1000},
            'contractor-quality-control': {
                'is_urgent': True,
                'limit': 2,
                'service': 'feeds',
                'provider': 'contractor-quality-control',
            },
        },
    },
)
async def test_internal_create_push_500(
        mockserver, taxi_driver_communications,
):
    @mockserver.json_handler('/client-notify/v2/bulk-push')
    def _push(request):
        return mockserver.make_response(status=500)

    body = {
        'options': ['push'],
        'payload': PAYLOAD,
        'contractors': [
            {'park_id': 'park_id1', 'contractor_profile_id': 'profile_id1'},
            {
                'park_id': 'park_id2',
                'contractor_profile_id': 'profile_id2',
                'payload_overrides': {'kek': 'kek'},
            },
        ],
    }

    response = await taxi_driver_communications.post(
        '/internal/driver-communications/v1/create',
        headers=HEADERS,
        params=QUERY,
        json=body,
    )

    expected_response = {
        'service': 'feeds',
        'provider': 'contractor-quality-control',
        'failed_push': body['contractors'],
    }

    assert response.status_code == 200
    assert response.json() == expected_response
