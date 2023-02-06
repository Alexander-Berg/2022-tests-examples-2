# pylint: disable=dangerous-default-value
import datetime

from aiohttp import web
import pytest

from testsuite.utils import matching


def _format_datetime(value: datetime.datetime) -> str:
    return value.strftime('%Y-%m-%dT%H:%M:%S%z')


def _parse_datetime(value: str) -> datetime.datetime:
    return datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%S%z')


@pytest.fixture(name='get_default_payload')
def _get_default_payload(load_json):
    def wrapper(service):
        kind = service[len('cargo-corp-') :]
        return load_json(f'payload_{kind}.json')

    return wrapper


@pytest.fixture(name='create_feed')
def _create_feed(web_app_client):
    async def wrapper(
            service, payload, settings=None, name='Name', author=YA_LOGIN,
    ):
        response = await web_app_client.post(
            '/v1/cargo-corp/create',
            headers={'X-Yandex-Login': author},
            json={
                'service': service,
                'name': name,
                'payload': payload,
                'settings': settings or SETTINGS,
            },
        )
        assert response.status == 200
        feed_id = (await response.json())['id']
        return feed_id

    return wrapper


@pytest.fixture(name='create_feed_by_service')
def _create_feed_by_service(create_feed, get_default_payload):
    async def wrapper(service, settings=None):
        return await create_feed(
            service, get_default_payload(service), settings,
        )

    return wrapper


@pytest.fixture(name='create_feed_by_payload')
def _create_feed_by_payload(create_feed):
    async def wrapper(payload, settings=None):
        return await create_feed(payload['kind'], payload, settings)

    return wrapper


@pytest.fixture(name='get_feed')
def _get_feed(web_app_client):
    async def wrapper(feed_id, service, expected_status=200):
        response = await web_app_client.get(
            '/v1/cargo-corp/get', params={'service': service, 'id': feed_id},
        )
        assert response.status == expected_status
        return await response.json()

    return wrapper


@pytest.fixture(name='start_feed')
def _start_feed(web_app_client):
    async def wrapper(
            feed_id,
            service,
            name='Name (after start)',
            recipients=RECIPIENTS[0],
            schedule=SCHEDULE,
            settings=SETTINGS,
    ):
        response = await web_app_client.post(
            '/v1/cargo-corp/start',
            json={
                'id': feed_id,
                'service': service,
                'name': name,
                'settings': settings,
                'recipients': recipients,
                'schedule': schedule,
            },
        )
        assert response.status == 200

    return wrapper


@pytest.fixture(name='set_feed_params')
def _set_feed_params(pgsql):
    def wrapper(feed_id, status=None, created_ts=None, updated_ts=None):
        changes = []
        if status is not None:
            changes.append(f'status = \'{status}\'')
        if created_ts is not None:
            changes.append(f'created = \'{created_ts}\'')
        if updated_ts is not None:
            changes.append(f'updated = \'{updated_ts}\'')
        assert changes
        sql_query = (
            """
            UPDATE feeds_admin.feeds
            SET
                {0}
            WHERE
                feed_uuid = \'{1}\'
            ;
        """.format(
                ','.join(changes), feed_id,
            )
        )

        cursor = pgsql['feeds_admin'].conn.cursor()
        cursor.execute(sql_query)
        cursor.close()

    return wrapper


@pytest.fixture(name='db_for_list')
async def _db_for_list(
        web_app_client,
        create_feed,
        set_feed_params,
        get_default_payload,
        start_feed,
):
    feed_name_to_id = {}
    payload = get_default_payload(CARGO_CORP_SERVICES[0])
    # feed to test order_by
    feed_id = await create_feed(
        CARGO_CORP_SERVICES[0], payload, name=FEED_NAMES[0],
    )
    feed_name_to_id[FEED_NAMES[0]] = feed_id
    set_feed_params(
        feed_id,
        created_ts='2020-01-01T12:00:00+0300',
        updated_ts='2020-01-01T12:00:00+0300',
    )

    # feed to test status
    feed_id = await create_feed(
        CARGO_CORP_SERVICES[0], payload, name=FEED_NAMES[1],
    )
    feed_name_to_id[FEED_NAMES[1]] = feed_id
    response = await web_app_client.post(
        '/v1/cargo-corp/purge',
        json={'id': feed_id, 'service': CARGO_CORP_SERVICES[0]},
    )
    assert response.status == 200

    # feed to test author
    feed_id = await create_feed(
        CARGO_CORP_SERVICES[0], payload, name=FEED_NAMES[2], author=YA_LOGIN_2,
    )
    feed_name_to_id[FEED_NAMES[2]] = feed_id

    # feed to test recurrence type
    feed_id = await create_feed(
        CARGO_CORP_SERVICES[0], payload, name=FEED_NAMES[3],
    )
    feed_name_to_id[FEED_NAMES[3]] = feed_id
    await start_feed(
        feed_id,
        CARGO_CORP_SERVICES[0],
        name=FEED_NAMES[3],
        recipients=RECIPIENTS[4],
    )

    settings = SETTINGS.copy()
    settings.update(about='This is about 2')
    # feed 1 to test about setting
    feed_id = await create_feed(
        CARGO_CORP_SERVICES[0], payload, settings=settings, name=FEED_NAMES[4],
    )
    feed_name_to_id[FEED_NAMES[4]] = feed_id

    payload = get_default_payload(CARGO_CORP_SERVICES[1])
    # feed 2 to test about setting (in another service)
    feed_id = await create_feed(
        CARGO_CORP_SERVICES[1], payload, settings=settings, name=FEED_NAMES[5],
    )
    feed_name_to_id[FEED_NAMES[5]] = feed_id

    payload = get_default_payload(CARGO_CORP_SERVICES[2])
    # feed 1 to test order_by=updated and offset
    feed_id = await create_feed(
        CARGO_CORP_SERVICES[2], payload, name=FEED_NAMES[6],
    )
    feed_name_to_id[FEED_NAMES[6]] = feed_id
    set_feed_params(
        feed_id,
        created_ts='2019-01-01T12:00:00+0300',
        updated_ts='2020-01-01T12:00:00+0300',
    )

    # feed 2 to test order_by=updated and offset
    feed_id = await create_feed(
        CARGO_CORP_SERVICES[2], payload, name=FEED_NAMES[7],
    )
    feed_name_to_id[FEED_NAMES[7]] = feed_id
    set_feed_params(
        feed_id,
        created_ts='2019-01-02T12:00:00+0300',
        updated_ts='2019-01-03T12:00:00+0300',
    )

    return feed_name_to_id


YA_LOGIN = 'dipterix'
YA_LOGIN_2 = 'basilgradov'
DEFAULT_FEED_COUNT_LIMIT = 50
FEED_NAMES = [f'Name_{i}' for i in range(8)]

CARGO_CORP_SERVICES = [
    'cargo-corp-bar',
    'cargo-corp-important',
    'cargo-corp-actual',
    'cargo-corp-news',
]

SETTINGS = {'about': 'About', 'priority': 101, 'meta_tags': []}

RECIPIENTS = [
    {'kind': 'all'},
    {'kind': 'id', 'ids': ['123', '321']},
    {'kind': 'contract', 'contracts': ['card']},
    {'kind': 'experiment', 'experiment': 'exp3'},
    {'kind': 'yql', 'yql_link': 'https://yql.yandex-team.ru/'},
    {'kind': 'backend'},
    {'kind': 'channel', 'channels': ['special']},
    {'kind': 'country', 'countries': ['blr', 'rus']},
    {'kind': 'city', 'cities': ['moscow', 'sochi']},
]

TIMEZONE = datetime.timezone(datetime.timedelta(hours=3))

SCHEDULE = {
    'recurrence': 'schedule',
    'first_publish_at': _format_datetime(
        datetime.datetime.now(tz=TIMEZONE) - datetime.timedelta(days=20),
    ),
    'last_publish_at': _format_datetime(
        datetime.datetime.now(tz=TIMEZONE) + datetime.timedelta(days=20),
    ),
    'week': [
        {'day': 'monday', 'time': '12:00:00'},
        {'day': 'tuesday', 'time': '14:00:00'},
    ],
    'ttl_seconds': 5 * 24 * 3600,
}


@pytest.mark.parametrize('service', CARGO_CORP_SERVICES)
@pytest.mark.parametrize('recipients', RECIPIENTS)
async def test_lifecycle(
        web_app_client,
        get_default_payload,
        create_feed_by_payload,
        get_feed,
        start_feed,
        service,
        recipients,
):
    payload = get_default_payload(service)

    # Create
    feed_id = await create_feed_by_payload(payload)
    expected_feed = {
        'id': feed_id,
        'service': service,
        'status': 'created',
        'name': 'Name',
        'settings': SETTINGS,
        'payload': payload,
        'author': YA_LOGIN,
        'created_ts': matching.datetime_string,
        'updated_ts': matching.datetime_string,
    }
    assert await get_feed(feed_id, service) == expected_feed

    # Update
    response = await web_app_client.post(
        '/v1/cargo-corp/update',
        json={
            'id': feed_id,
            'service': service,
            'name': 'Name (after update)',
            'payload': payload,
            'settings': SETTINGS,
        },
    )
    assert response.status == 200
    expected_feed.update(name='Name (after update)')
    assert await get_feed(feed_id, service) == expected_feed

    # Start
    await start_feed(feed_id, service, recipients=recipients)
    expected_feed.update(
        name='Name (after start)', recipients=recipients, schedule=SCHEDULE,
    )
    assert await get_feed(feed_id, service) == expected_feed

    # Archive
    response = await web_app_client.post(
        '/v1/cargo-corp/archive', json={'id': feed_id, 'service': service},
    )
    assert response.status == 200
    expected_feed.update(status='deleted')
    assert await get_feed(feed_id, service) == expected_feed


@pytest.mark.parametrize(
    'is_feed_started',
    (pytest.param(False, id='ok'), pytest.param(True, id='ok after start')),
)
async def test_copy(
        web_app_client,
        get_default_payload,
        create_feed_by_payload,
        get_feed,
        start_feed,
        is_feed_started,
):
    service = CARGO_CORP_SERVICES[0]
    payload = get_default_payload(service)

    # Create
    feed_id = await create_feed_by_payload(payload)
    expected_feed = {
        'id': feed_id,
        'service': service,
        'status': 'created',
        'name': 'Name',
        'settings': SETTINGS,
        'payload': payload,
        'author': YA_LOGIN,
        'created_ts': matching.datetime_string,
        'updated_ts': matching.datetime_string,
    }
    assert await get_feed(feed_id, service) == expected_feed

    if is_feed_started:
        await start_feed(feed_id, service)
        expected_feed.update(
            name='Name (after start)', recipients=RECIPIENTS[0],
        )

    # Copy
    response = await web_app_client.post(
        '/v1/cargo-corp/copy',
        json={'id': feed_id, 'service': service},
        headers={'X-Yandex-Login': YA_LOGIN_2},
    )
    assert response.status == 200
    copy_feed_id = (await response.json())['id']
    expected_feed.update(id=copy_feed_id, author=YA_LOGIN_2)
    assert await get_feed(copy_feed_id, service) == expected_feed


@pytest.mark.parametrize(
    'is_correct_feed_id, expected_code',
    [
        pytest.param(True, 200, id='ok'),
        pytest.param(False, 404, id='invalid feed_id'),
    ],
)
async def test_purge(
        web_app_client,
        get_default_payload,
        create_feed_by_payload,
        get_feed,
        start_feed,
        is_correct_feed_id,
        expected_code,
):
    service = CARGO_CORP_SERVICES[0]
    recipients = RECIPIENTS[0]
    payload = get_default_payload(service)

    # Create
    feed_id = await create_feed_by_payload(payload)
    expected_feed = {
        'id': feed_id,
        'service': service,
        'status': 'created',
        'name': 'Name',
        'settings': SETTINGS,
        'payload': payload,
        'author': YA_LOGIN,
        'created_ts': matching.datetime_string,
        'updated_ts': matching.datetime_string,
    }
    assert await get_feed(feed_id, service) == expected_feed

    # Start
    await start_feed(feed_id, service)
    expected_feed.update(
        name='Name (after start)', recipients=recipients, schedule=SCHEDULE,
    )
    assert await get_feed(feed_id, service) == expected_feed

    # Purge
    feed_to_purge = feed_id if is_correct_feed_id else feed_id[::-1]
    response = await web_app_client.post(
        '/v1/cargo-corp/purge', json={'id': feed_to_purge, 'service': service},
    )
    assert response.status == expected_code
    expected_feed.update(status='finished')
    if expected_code == 200:
        assert await get_feed(feed_id, service) == expected_feed


async def test_stop(
        web_app_client,
        set_feed_params,
        get_default_payload,
        create_feed_by_payload,
        get_feed,
        start_feed,
):
    service = CARGO_CORP_SERVICES[0]
    payload = get_default_payload(service)

    # Create
    feed_id = await create_feed_by_payload(payload)
    # Start
    await start_feed(feed_id, service)
    # change status to allow stop
    set_feed_params(feed_id, status='publishing')

    # Stop
    response = await web_app_client.post(
        '/v1/cargo-corp/stop', json={'id': feed_id, 'service': service},
    )
    assert response.status == 200
    feed = await get_feed(feed_id, service)
    expected_feed = {
        'id': feed_id,
        'service': service,
        'status': 'published',
        'name': 'Name (after start)',
        'settings': SETTINGS,
        'payload': payload,
        'author': YA_LOGIN,
        'recipients': RECIPIENTS[0],
        'schedule': SCHEDULE,
        'created_ts': matching.datetime_string,
        'updated_ts': matching.datetime_string,
    }
    assert feed == expected_feed


@pytest.mark.parametrize(
    ('services', 'body_params', 'filters', 'expected_feed_names'),
    (
        pytest.param(
            [CARGO_CORP_SERVICES[0]],
            {},
            None,
            FEED_NAMES[0:5],
            id='ok one service',
        ),
        pytest.param(
            [CARGO_CORP_SERVICES[0]],
            {},
            {'name': FEED_NAMES[0]},
            [FEED_NAMES[0]],
            id='ok name filter',
        ),
        pytest.param(
            [CARGO_CORP_SERVICES[0]],
            {},
            {'about': 'about 2'},
            [FEED_NAMES[4]],
            id='ok "about" setting filter',
        ),
        pytest.param(
            [CARGO_CORP_SERVICES[0]],
            {},
            {'statuses': ['finished']},
            [FEED_NAMES[1]],
            id='ok status filter',
        ),
        pytest.param(
            [CARGO_CORP_SERVICES[0]],
            {},
            {'recurrence_type': 'schedule'},
            [FEED_NAMES[3]],
            id='ok recurrence_type filter',
        ),
        pytest.param(
            [CARGO_CORP_SERVICES[0]],
            {},
            {'authors': [YA_LOGIN_2]},
            [FEED_NAMES[2]],
            id='ok author filter',
        ),
        pytest.param(
            [CARGO_CORP_SERVICES[2]],
            {'order_by': 'updated'},
            None,
            [FEED_NAMES[6], FEED_NAMES[7]],
            id='ok order_by=updated',
        ),
        pytest.param(
            [CARGO_CORP_SERVICES[2]],
            {'limit': 1, 'order_by': 'updated'},
            None,
            [FEED_NAMES[6]],
            id='ok limit',
        ),
        pytest.param(
            [CARGO_CORP_SERVICES[2]],
            {'limit': 1, 'order_by': 'updated', 'offset': 1},
            None,
            [FEED_NAMES[7]],
            id='ok offset',
        ),
        pytest.param(
            [CARGO_CORP_SERVICES[0], CARGO_CORP_SERVICES[1]],
            {},
            {'authors': [YA_LOGIN], 'statuses': ['created', 'finished']},
            FEED_NAMES[:2] + FEED_NAMES[3:6],
            id='ok combined filters',
        ),
    ),
)
async def test_list_filters(
        web_app_client,
        db_for_list,
        services,
        body_params,
        filters,
        expected_feed_names,
):
    # create request
    request_json = {'services': services, **body_params}
    if filters is not None:
        request_json['filters'] = filters

    # List
    response = await web_app_client.post(
        '/v1/cargo-corp/list', json=request_json,
    )
    response_json = await response.json()
    assert response.status == 200
    assert len(response_json['items']) <= body_params.get(
        'limit', DEFAULT_FEED_COUNT_LIMIT,
    )

    response_feed_names = []
    order_field = f'{body_params.get("order_by", "created")}_ts'
    if response_json['items']:
        previous_order_value = _parse_datetime(
            response_json['items'][0][order_field],
        )

    for feed in response_json['items']:
        response_feed_names.append(feed['name'])

        current_order_value = _parse_datetime(feed[order_field])
        assert previous_order_value >= current_order_value
        previous_order_value = current_order_value
    assert sorted(expected_feed_names) == sorted(response_feed_names)


async def test_list_feed_content(web_app_client, db_for_list):
    feed_id = db_for_list[FEED_NAMES[3]]

    response = await web_app_client.post(
        '/v1/cargo-corp/list',
        json={
            'services': [CARGO_CORP_SERVICES[0]],
            'filters': {'name': FEED_NAMES[3]},
        },
    )
    assert response.status == 200

    feed = (await response.json())['items'][0]
    expected_feed = {
        'id': feed_id,
        'service': CARGO_CORP_SERVICES[0],
        'name': FEED_NAMES[3],
        'settings': SETTINGS,
        'status': 'created',
        'author': YA_LOGIN,
        'schedule': SCHEDULE,
        'recipients_type': 'yql',
        'created_ts': matching.datetime_string,
        'updated_ts': matching.datetime_string,
    }
    assert feed == expected_feed


@pytest.mark.parametrize('service', CARGO_CORP_SERVICES)
async def test_send(
        web_app_client,
        mock_feeds,
        get_default_payload,
        create_feed_by_payload,
        service,
):
    now = datetime.datetime.now(tz=TIMEZONE).replace(microsecond=0)
    expires = now + datetime.timedelta(days=2)
    payload = get_default_payload(service)

    @mock_feeds('/v1/batch/create')
    async def feeds_create(request):  # pylint: disable=W0612
        item = request.json['items'][0]
        assert item['payload'] == payload
        assert _parse_datetime(item['expire']) == expires
        assert item['channels'] == [
            {
                'channel': 'id:1',
                'payload_params': {'name': 'Freddie', 'age': '38'},
            },
            {
                'channel': 'id:2',
                'payload_params': {'name': 'Джонни', 'age': '19'},
            },
        ]
        return web.json_response(
            data={
                'items': [
                    {
                        'service': service,
                        'feed_ids': {service: 'feeds_feed_id'},
                        'filtered': [],
                    },
                ],
            },
        )

    feed_id = await create_feed_by_payload(payload)

    response = await web_app_client.post(
        '/v1/cargo-corp/send',
        headers={'X-Idempotency-Token': 'token'},
        json={
            'id': feed_id,
            'service': service,
            'schedule': {'expires': _format_datetime(expires)},
            'recipients': [
                {
                    'recipient_id': '1',
                    'parameters': {'name': 'Freddie', 'age': '38'},
                },
                {
                    'recipient_id': '2',
                    'parameters': {'name': 'Джонни', 'age': '19'},
                },
            ],
        },
    )
    assert response.status == 200
    assert feeds_create.times_called == 1


async def test_send_request_already_in_progress(
        web_app_client,
        mock_feeds,
        get_default_payload,
        create_feed_by_payload,
):
    @mock_feeds('/v1/batch/create')
    async def feeds_create(request):  # pylint: disable=W0612
        return web.json_response(
            status=409,
            data={'code': '409', 'message': 'request already in progress'},
        )

    service = CARGO_CORP_SERVICES[0]
    expires = datetime.datetime.now() + datetime.timedelta(days=2)
    feed_id = await create_feed_by_payload(get_default_payload(service))

    response = await web_app_client.post(
        '/v1/cargo-corp/send',
        headers={'X-Idempotency-Token': 'token'},
        json={
            'id': feed_id,
            'service': service,
            'schedule': {'expires': _format_datetime(expires)},
            'recipients': [{'recipient_id': '1'}],
        },
    )
    assert response.status == 409
    assert feeds_create.times_called == 1
