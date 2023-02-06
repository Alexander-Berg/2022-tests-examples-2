# flake8: noqa

# Feel free to provide your custom implementation to override generated tests.

import datetime
import pytest
import json
import base64

# pylint: disable=import-error,wildcard-import
from eats_restapp_communications_plugins.generated_tests import *


async def request_proxy_notifications(
        taxi_eats_restapp_communications,
        data,
        patner_id,
        place_id,
        limit=10,
        cursor='',
):
    url = (
        '/4.0/restapp-front/communications/v1/list?place_id={}&limit={}'.format(
            place_id, limit,
        )
    )
    if cursor != '':
        url += '&cursor={}'.format(cursor)

    headers = {
        'X-YaEda-PartnerId': str(patner_id),
        'Content-type': 'application/json',
    }
    extra = {'headers': headers}

    return await taxi_eats_restapp_communications.post(
        url, data=json.dumps(data), **extra,
    )


async def test_notification_priority(
        taxi_eats_restapp_communications,
        mock_eats_feeds_200_priority,
        mock_authorizer_allowed,
        pgsql,
):
    place_id = 43
    partner_id = 1
    data = {'etags': {}, 'services': ['news']}
    response = await request_proxy_notifications(
        taxi_eats_restapp_communications, data, partner_id, place_id,
    )
    assert response.status_code == 200
    assert len(response.json()['feed']['news']) == 5
    assert response.json()['feed']['news'][0]['id'] == '3'  # important: True
    assert (
        response.json()['feed']['news'][1]['id'] == '5'
    )  # priority:5 and newer than id=2
    assert response.json()['feed']['news'][2]['id'] == '2'
    assert response.json()['feed']['news'][3]['id'] == '4'  # priority:2
    assert response.json()['feed']['news'][4]['id'] == '1'  # no priority info


@pytest.mark.pgsql(
    'eats_restapp_communications', files=('test_get_notification.sql',),
)
async def test_get_notification(
        taxi_eats_restapp_communications,
        mock_eats_feeds_200,
        mock_authorizer_allowed,
        pgsql,
):
    place_id = 43
    partner_id = 1
    data = {
        'etags': {'news': 'etag-advice', 'survey': 'a4f920ec5d'},
        'services': ['news', 'notification', 'survey'],
    }
    response = await request_proxy_notifications(
        taxi_eats_restapp_communications, data, partner_id, place_id,
    )
    assert response.status_code == 200
    assert len(response.json()['feed']['survey']) == 1
    assert (
        response.json()['feed']['survey'][0]['id']
        == '4ec6a5d00d634f8c9d5605b0fdc2c576'
    )
    cursor = response.json()['cursor']
    parsed_cursor = json.loads(str(base64.b64decode(cursor), 'ascii'))
    assert parsed_cursor['survey'] == '4ec6a5d00d634f8c9d5605b0fdc2c576'


async def test_notification_cursor(
        taxi_eats_restapp_communications,
        mock_eats_feeds_200_priority,
        mock_authorizer_allowed,
        pgsql,
):
    place_id = 43
    partner_id = 1
    limit = 2
    data = {'etags': {}, 'services': ['news']}

    response = await request_proxy_notifications(
        taxi_eats_restapp_communications, data, partner_id, place_id, limit,
    )
    assert response.status_code == 200
    assert len(response.json()['feed']['news']) == 2
    assert response.json()['feed']['news'][0]['id'] == '3'  # important: True
    assert (
        response.json()['feed']['news'][1]['id'] == '5'
    )  # priority:5 and newer than id=2
    cursor = response.json()['cursor']

    response = await request_proxy_notifications(
        taxi_eats_restapp_communications,
        data,
        partner_id,
        place_id,
        limit,
        cursor,
    )
    assert response.status_code == 200
    assert len(response.json()['feed']['news']) == 2
    assert response.json()['feed']['news'][0]['id'] == '2'
    assert response.json()['feed']['news'][1]['id'] == '4'  # priority:2
    cursor = response.json()['cursor']

    response = await request_proxy_notifications(
        taxi_eats_restapp_communications,
        data,
        partner_id,
        place_id,
        limit,
        cursor,
    )
    assert response.status_code == 200
    assert len(response.json()['feed']['news']) == 1
    assert response.json()['feed']['news'][0]['id'] == '1'
