import pytest


@pytest.mark.pgsql(
    'taxi_db_postgres_atlas_backend', files=['pg_hierarchy.sql'],
)
@pytest.mark.parametrize(
    'key,value',
    [
        pytest.param('city', 'Москва'),
        pytest.param(
            'geonodes', [{'name': 'br_moscow', 'type': 'agglomeration'}],
        ),
    ],
)
async def test_get_events(web_app_client, atlas_blackbox_mock, key, value):
    response = await web_app_client.post(
        '/api/events',
        json={
            'date_from': 1593180000,
            'date_to': 1593181000,
            key: value,
            'type': 'regular',
        },
    )
    assert response.status == 200
    events = await response.json()
    assert len(events) == 1
    assert events[0] == {
        '_id': '5f082c92d4ccf927ec94f68b',
        'created_utc': 1593180600,
        'global': False,
        'user_alias': 'test_user',
        'title': 'Очень важное событие',
        'description': 'secret description',
        'color': '#faaa14',
        'city': 'Москва',
        'is_interval': False,
        'type': 'regular',
        'start_ts': 1593180600,
        'end_ts': 1593180600,
    }


@pytest.mark.pgsql(
    'taxi_db_postgres_atlas_backend', files=['pg_hierarchy.sql'],
)
@pytest.mark.parametrize(
    'key,value',
    [
        pytest.param('city', ['Москва', 'Казань']),
        pytest.param(
            'geonodes',
            [
                {'name': 'br_moscow', 'type': 'agglomeration'},
                {'name': 'br_kazan', 'type': 'agglomeration'},
            ],
        ),
    ],
)
async def test_get_multiple_cities_events(
        web_app_client, atlas_blackbox_mock, key, value,
):
    response = await web_app_client.post(
        '/api/events',
        json={
            'date_from': 1593180000,
            'date_to': 1593181000,
            key: value,
            'type': 'regular',
        },
    )
    assert response.status == 200
    events = await response.json()
    assert len(events) == 2


@pytest.mark.pgsql(
    'taxi_db_postgres_atlas_backend', files=['pg_hierarchy.sql'],
)
@pytest.mark.parametrize(
    'key,value',
    [
        pytest.param('city', 'Казань'),
        pytest.param(
            'geonodes', [{'name': 'br_kazan', 'type': 'agglomeration'}],
        ),
    ],
)
async def test_get_global_events(
        web_app_client, atlas_blackbox_mock, key, value,
):
    response = await web_app_client.post(
        '/api/events',
        json={
            'date_from': 1593604800,
            'date_to': 1593604800,
            key: value,
            'type': 'regular',
        },
    )
    assert response.status == 200
    events = await response.json()
    assert len(events) == 1
    assert events[0]['city'] == 'Владивосток'


@pytest.mark.pgsql(
    'taxi_db_postgres_atlas_backend', files=['pg_hierarchy.sql'],
)
@pytest.mark.parametrize(
    'key,value',
    [
        pytest.param('city', 'Москва'),
        pytest.param(
            'geonodes', [{'name': 'br_moscow', 'type': 'agglomeration'}],
        ),
    ],
)
async def test_get_anomaly_events(
        web_app_client, atlas_blackbox_mock, key, value,
):
    response = await web_app_client.post(
        '/api/events',
        json={
            'date_from': 1593180000,
            'date_to': 1593190000,
            key: value,
            'type': 'anomaly',
        },
    )
    assert response.status == 200
    events = await response.json()
    assert len(events) == 2
    assert events[0] == {
        '_id': '5e00b661954de74d8a6af7c7',
        'created_utc': 1593173520,
        'global': True,
        'user_alias': 'some-user',
        'title': 'anomaly 5e00b661954de74d8a6af7c7',
        'description': '\nLosses: -38 orders\nAnomaly source: all\nAnomaly severity level: minor',  # noqa: disable=e501
        'color': '#f5222d',
        'city': 'Москва',
        'type': 'anomaly',
        'is_interval': True,
        'start_ts': 1593181520,
        'end_ts': 1593186537,
    }


async def test_bad_get_events(web_app_client, atlas_blackbox_mock):
    response = await web_app_client.post(
        '/api/events',
        json={
            'date_from': 1593180000,
            'date_to': 1593181000,
            'type': 'regular',
        },
    )
    assert response.status == 400


async def test_create_event(web_app_client, db, atlas_blackbox_mock):
    count_before = await db.atlas_events.find().count()
    data = {
        'created_utc': 1593173520,
        'global': False,
        'user_alias': 'some-user',
        'title': 'New event',
        'description': '---',
        'city': 'Владивосток',
    }
    response = await web_app_client.post('/api/events/create', json=data)
    assert response.status == 200
    inserted_id = (await response.json())['_id']

    count_after = await db.atlas_events.find().count()
    assert count_after == count_before + 1

    inserted_response = await web_app_client.post(
        '/api/events',
        json={
            'date_from': 1593173520,
            'date_to': 1593173520,
            'city': 'Владивосток',
        },
    )
    inserted_doc = [
        doc
        for doc in await inserted_response.json()
        if doc['_id'] == inserted_id
    ][0]
    assert set(data.items()).issubset(inserted_doc.items())
    assert inserted_doc['start_ts'] == inserted_doc['end_ts']
    assert inserted_doc['created_utc'] == inserted_doc['start_ts']


async def test_update_event(web_app_client, db, atlas_blackbox_mock):
    existed_event_response = await web_app_client.post(
        '/api/events',
        json={
            'date_from': 1593604800,
            'date_to': 1593604800,
            'city': 'Владивосток',
            'type': 'regular',
        },
    )
    assert existed_event_response.status == 200
    update = (await existed_event_response.json())[0]
    update['user_alias'] = 'another_test_user'
    update['description'] = 'Changed description'

    await web_app_client.post(
        'api/events/update',
        json={
            key: update[key]
            for key in [
                '_id',
                'city',
                'created_utc',
                'global',
                'user_alias',
                'title',
                'description',
                'is_interval',
                'start_ts',
                'end_ts',
            ]
        },
    )

    updated_event_response = await web_app_client.post(
        '/api/events',
        json={
            'date_from': 1593604800,
            'date_to': 1593604800,
            'city': 'Владивосток',
            'type': 'regular',
        },
    )
    updated_event = (await updated_event_response.json())[0]
    assert updated_event == update


async def test_delete_event(web_app_client, atlas_blackbox_mock):
    event_list_response_before = await web_app_client.post(
        '/api/events',
        json={
            'date_from': 1593604800,
            'date_to': 1593604800,
            'city': 'Владивосток',
            'type': 'regular',
        },
    )
    assert event_list_response_before.status == 200
    event_list_before = await event_list_response_before.json()
    assert event_list_before  # not empty

    deleted_response = await web_app_client.post(
        '/api/events/remove', json={'_id': event_list_before[-1]['_id']},
    )
    assert deleted_response.status == 200

    event_list_response_after = await web_app_client.post(
        '/api/events',
        json={
            'date_from': 1593604800,
            'date_to': 1593604800,
            'city': 'Владивосток',
            'type': 'regular',
        },
    )
    assert event_list_response_after.status == 200
    event_list_after = await event_list_response_after.json()

    assert len(event_list_after) == len(event_list_before) - 1
