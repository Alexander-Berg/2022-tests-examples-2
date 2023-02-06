import tests_client_events.pull_helpers as helpers


SERVICE = 'yandex.pro'


def _make_channel(dbid, uuid):
    return 'contractor:' + dbid + '_' + uuid


async def _do_pull_request(taxi_client_events, dbid, uuid, body):
    return await taxi_client_events.post(
        'pro/v1/pull',
        headers={
            'X-YaTaxi-Park-Id': dbid,
            'X-YaTaxi-Driver-Profile-Id': uuid,
            'X-Request-Application-Version': '9.40',
            'X-Request-Version-Type': '',  # '' for taximeter
            'X-Request-Platform': 'android',
        },
        json=body,
    )


def _check_polling_header(header):
    parts = header.split(', ')
    parts.sort()
    assert parts == [
        'background=1200s',
        'full=600s',
        'idle=1800s',
        'powersaving=1200s',
    ]


async def test_sample(taxi_client_events, push_events):
    dbid = 'park000'
    uuid = 'profile000'

    await push_events(
        [
            {
                'service': SERVICE,
                'channel': _make_channel(dbid, uuid),
                'event': 'event_1',
                'event_id': 'event_id',
                'payload': {'some': 'data'},
            },
        ],
    )

    pull_request_body = {'events': []}

    response = await _do_pull_request(
        taxi_client_events, dbid, uuid, pull_request_body,
    )
    assert response.status_code == 200
    _check_polling_header(response.headers['X-Polling-Power-Policy'])

    assert helpers.prepare_response(response.json()) == {
        'events': {
            'updated': [
                {
                    'event': 'event_1',
                    'event_id': 'event_id',
                    'payload': {'some': 'data'},
                },
            ],
            'expired': [],
        },
    }


async def test_expired(taxi_client_events, push_events):
    dbid = 'park000'
    uuid = 'profile000'

    await push_events(
        [
            {
                'service': SERVICE,
                'channel': _make_channel(dbid, uuid),
                'event': 'event_1',
            },
        ],
    )

    pull_request_body = {
        'events': [
            {'event': 'event_2', 'version': '0.0'},
            {'event': 'event_3', 'event_id': 'event_id', 'version': '0.0'},
        ],
    }

    response = await _do_pull_request(
        taxi_client_events, dbid, uuid, pull_request_body,
    )
    assert response.status_code == 200
    _check_polling_header(response.headers['X-Polling-Power-Policy'])

    assert helpers.prepare_response(response.json()) == {
        'events': {
            'updated': [{'event': 'event_1'}],
            'expired': [
                {'event': 'event_2'},
                {'event': 'event_3', 'event_id': 'event_id'},
            ],
        },
    }


async def test_updated(taxi_client_events, push_events):
    dbid = 'park000'
    uuid = 'profile000'
    channel = _make_channel(dbid, uuid)

    await push_events(
        [
            {'service': SERVICE, 'channel': channel, 'event': 'event_1'},
            {'service': SERVICE, 'channel': channel, 'event': 'event_2'},
            {
                'service': SERVICE,
                'channel': channel,
                'event': 'event_2',
                'event_id': 'event_id',
            },
        ],
    )

    pull_request_body = {
        'events': [
            {'event': 'event_1', 'version': '0.0'},
            {'event': 'event_2', 'version': '9.0'},
            {'event': 'event_2', 'event_id': 'event_id', 'version': '0.0'},
        ],
    }

    response = await _do_pull_request(
        taxi_client_events, dbid, uuid, pull_request_body,
    )
    assert response.status_code == 200
    _check_polling_header(response.headers['X-Polling-Power-Policy'])

    assert helpers.prepare_response(response.json()) == {
        'events': {
            'updated': [
                {'event': 'event_1'},
                {'event': 'event_2', 'event_id': 'event_id'},
            ],
            'expired': [],
        },
    }


async def test_no_version(taxi_client_events, push_events):
    dbid = 'park000'
    uuid = 'profile000'

    await push_events(
        [
            {
                'service': SERVICE,
                'channel': _make_channel(dbid, uuid),
                'event': 'event_1',
            },
        ],
    )

    pull_request_body = {
        'events': [{'event': 'event_1'}, {'event': 'event_2'}],
    }

    response = await _do_pull_request(
        taxi_client_events, dbid, uuid, pull_request_body,
    )
    assert response.status_code == 200
    _check_polling_header(response.headers['X-Polling-Power-Policy'])

    assert helpers.prepare_response(response.json()) == {
        'events': {'updated': [], 'expired': []},
    }
