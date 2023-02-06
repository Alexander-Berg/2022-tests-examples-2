import json

import pytest

from feeds_admin.services import fleet_fullscreens
from test_feeds_admin import common


@pytest.mark.now('2020-06-23T05:10:25+0300')
async def test_lifecycle(web_app_client, load):
    author = 'adomogashev'
    service = 'fleet-fullscreens'

    # Create
    create_request = json.loads(load('create_request.json'))
    create_run_history = json.loads(load('create_run_history.json'))
    create_response = await web_app_client.post(
        '/v1/fleet-fullscreens/create',
        json=create_request,
        headers={'X-Yandex-Login': author},
    )
    assert create_response.status == 200
    feed_id = (await create_response.json())['id']

    get_params = {'id': feed_id, 'service': service}

    # Get
    get_response = await web_app_client.get(
        '/v1/fleet-fullscreens/get', params=get_params,
    )
    content = await get_response.json()
    assert content.pop('id') == feed_id
    assert content.pop('author') == author
    assert content.pop('status') == 'publishing'
    assert content.pop('created') == content.pop('updated')
    assert content.pop('run_history') == create_run_history
    assert create_request == content

    # Update
    update_request = json.loads(load('update_request.json'))
    update_run_history = json.loads(load('update_run_history.json'))

    update_request.update({'id': feed_id})
    update_response = await web_app_client.post(
        '/v1/fleet-fullscreens/update', json=update_request,
    )
    assert update_response.status == 200

    get_response = await web_app_client.get(
        '/v1/fleet-fullscreens/get', params=get_params,
    )
    content = await get_response.json()
    assert content.pop('author') == author
    assert content.pop('status') == 'publishing'
    assert content.pop('run_history') == update_run_history
    assert content.pop('created')
    assert content.pop('updated')
    assert update_request == content


async def test_channels_generator(web_app_client):
    feed = common.create_fake_feed(
        'fleet-fullscreens', payload={'options': {'state': 'production'}},
    )
    recipients_group = common.create_fake_recipients_group(
        group_settings={
            'includes_pages': ['main', 'news'],
            'excludes_pages': ['about'],
            'positions': ['director'],
        },
    )

    gen = fleet_fullscreens.ChannelsGenerator(feed, recipients_group)
    gen.append_test(
        fleet_fullscreens.RecipientType.PARK, ['test_dbid1', 'test_dbid2'],
    )
    gen.append_prod(fleet_fullscreens.RecipientType.PARK, ['dbid1', 'dbid2'])
    gen.append_prod(
        fleet_fullscreens.RecipientType.CITY, ['Moscow', 'Novosibirsk'],
    )
    gen.append_prod(fleet_fullscreens.RecipientType.COUNTRY, ['Russia'])

    assert set(gen.included_channels) == {
        'park:dbid1;page:main;position:director',
        'park:dbid1;page:news;position:director',
        'park:dbid2;page:main;position:director',
        'park:dbid2;page:news;position:director',
        'park:test_dbid1;page:main;position:director',
        'park:test_dbid1;page:news;position:director',
        'park:test_dbid2;page:main;position:director',
        'park:test_dbid2;page:news;position:director',
        'country:Russia;page:main;position:director',
        'country:Russia;page:news;position:director',
        'city:Moscow;page:main;position:director',
        'city:Moscow;page:news;position:director',
        'city:Novosibirsk;page:main;position:director',
        'city:Novosibirsk;page:news;position:director',
        'service;park:dbid2;position:director',
        'service;park:test_dbid1;position:director',
        'service;city:Moscow;position:director',
        'service;city:Novosibirsk;position:director',
        'service;country:Russia;position:director',
        'service;park:test_dbid2;position:director',
        'service;park:dbid1;position:director',
    }
