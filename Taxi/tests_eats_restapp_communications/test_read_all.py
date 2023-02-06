# flake8: noqa

# Feel free to provide your custom implementation to override generated tests.

import datetime
import pytest
import json
import base64

# pylint: disable=import-error,wildcard-import
from eats_restapp_communications_plugins.generated_tests import *


TIMESTAMP_NOW = '2021-01-10T12:12:00+00:00'


def make_feed_data(has_more, service_name, feed_timestamps, important_feeds):
    data = {
        'polling_delay': 300,
        'etag': 'etag1',
        'has_more': has_more,
        'feed': [],
    }
    for feed_id, timestamp in feed_timestamps.items():
        created = timestamp.astimezone().strftime('%Y-%m-%dT%H:%M:%S.%f%z')
        data['feed'].append(
            {
                'feed_id': feed_id,
                'created': created,
                'service': service_name,
                'request_id': 'request_id',
                'last_status': {'status': 'published', 'created': created},
                'payload': {
                    'preview': {'title': 'Заголовок'},
                    'info': {'important': feed_id in important_feeds},
                },
            },
        )
    return data


@pytest.mark.now(TIMESTAMP_NOW)
@pytest.mark.pgsql(
    'eats_restapp_communications', files=('read_all_compound.sql',),
)
async def test_read_all_simple(
        taxi_eats_restapp_communications, mockserver, mock_authorizer_allowed,
):
    service = 'survey'
    service_prefix = 'eats-restaurants-'
    feed_id = '4ec6a5d00d634f8c9d5605b0fdc2c576'
    partner_id = 1
    place_id = 43

    @mockserver.json_handler('/feeds/v1/fetch')
    def fetch_feeds(request):
        service_name = service_prefix + service
        assert request.json['service'] == service_name
        assert set(request.json['channels']) == set(
            (
                f'restaurant:{place_id}',
                f'partner_id:{partner_id}',
                'all',
                'brand:kfc',
                'city:adler',
            ),
        )
        assert request.json['earlier_than'] == TIMESTAMP_NOW
        return mockserver.make_response(
            status=200,
            json=make_feed_data(
                False,
                service_name,
                {feed_id: datetime.datetime(2021, 1, 10, 12, 1, 1)},
                (),
            ),
        )

    @mockserver.json_handler('/feeds/v1/log_status')
    def log_status(request):
        assert request.json['service'] == service_prefix + service
        assert request.json['channel'] == f'partner_id:{partner_id}'
        assert request.json['status'] == 'read'
        assert 'feed_ids' in request.json and request.json['feed_ids'] == [
            feed_id,
        ]
        return mockserver.make_response(
            status=200, json={'statuses': {feed_id: 200}},
        )

    response = await taxi_eats_restapp_communications.post(
        '/4.0/restapp-front/communications/v1/read-all',
        headers={'X-YaEda-PartnerId': str(partner_id)},
        params={'place_id': place_id},
        json={'service': service},
    )

    assert response.status_code == 200
    assert fetch_feeds.times_called == log_status.times_called == 1


@pytest.mark.now(TIMESTAMP_NOW)
@pytest.mark.pgsql(
    'eats_restapp_communications', files=('read_all_compound.sql',),
)
async def test_read_all_compound(
        taxi_eats_restapp_communications, mockserver, mock_authorizer_allowed,
):
    service = 'survey'
    service_name = 'eats-restaurants-' + service
    important_feeds = set(('1', '3', '12'))
    partner_id = 1
    place_id = 43

    now = datetime.datetime.fromisoformat(TIMESTAMP_NOW)
    fetch_batches = [
        (
            True,
            service_name,
            {str(i): now - datetime.timedelta(hours=i) for i in range(5)},
            important_feeds,
        ),
        (
            True,
            service_name,
            {str(i): now - datetime.timedelta(hours=i) for i in range(5, 10)},
            important_feeds,
        ),
        (
            False,
            service_name,
            {str(i): now - datetime.timedelta(hours=i) for i in range(10, 15)},
            important_feeds,
        ),
    ]
    earlier_than = [
        now,
        now - datetime.timedelta(hours=4),
        now - datetime.timedelta(hours=9),
    ]
    count = 0

    @mockserver.json_handler('/feeds/v1/fetch')
    def fetch_feeds(request):
        nonlocal count
        count += 1
        assert (
            request.json['earlier_than'] == earlier_than[count - 1].isoformat()
        )
        return mockserver.make_response(
            status=200, json=make_feed_data(*fetch_batches[count - 1]),
        )

    @mockserver.json_handler('/feeds/v1/log_status')
    def log_status(request):
        assert (
            set(request.json['feed_ids'])
            == set(str(i) for i in range(15)) - important_feeds
        )
        return mockserver.make_response(
            status=200,
            json={
                'statuses': {
                    feed_id: 200 for feed_id in request.json['feed_ids']
                },
            },
        )

    response = await taxi_eats_restapp_communications.post(
        '/4.0/restapp-front/communications/v1/read-all',
        headers={'X-YaEda-PartnerId': str(partner_id)},
        params={'place_id': place_id},
        json={'service': service},
    )

    assert response.status_code == 200
    assert fetch_feeds.times_called == len(fetch_batches)
    assert log_status.times_called == 1


async def test_read_all_failed_fetch(
        taxi_eats_restapp_communications, mockserver, mock_authorizer_allowed,
):
    service = 'survey'
    partner_id = 1
    place_id = 43

    @mockserver.json_handler('/feeds/v1/fetch')
    def fetch_feeds(request):
        return mockserver.make_response(status=404)

    @mockserver.json_handler('/feeds/v1/log_status')
    def log_status(request):
        pass

    response = await taxi_eats_restapp_communications.post(
        '/4.0/restapp-front/communications/v1/read-all',
        headers={'X-YaEda-PartnerId': str(partner_id)},
        params={'place_id': place_id},
        json={'service': service},
    )

    assert response.status_code == 400
    assert fetch_feeds.times_called == 1
    assert log_status.times_called == 0


async def test_read_all_failed_log_status(
        taxi_eats_restapp_communications, mockserver, mock_authorizer_allowed,
):
    service = 'survey'
    service_name = 'eats-restaurants-' + service
    feed_id = '4ec6a5d00d634f8c9d5605b0fdc2c576'
    partner_id = 1
    place_id = 43

    @mockserver.json_handler('/feeds/v1/fetch')
    def fetch_feeds(request):
        return mockserver.make_response(
            status=200,
            json=make_feed_data(
                False,
                service_name,
                {feed_id: datetime.datetime(2021, 1, 10, 12, 1, 1)},
                (),
            ),
        )

    @mockserver.json_handler('/feeds/v1/log_status')
    def log_status(request):
        return mockserver.make_response(
            status=404, json={'code': '404', 'message': 'Not Found'},
        )

    response = await taxi_eats_restapp_communications.post(
        '/4.0/restapp-front/communications/v1/read-all',
        headers={'X-YaEda-PartnerId': str(partner_id)},
        params={'place_id': place_id},
        json={'service': service},
    )

    assert response.status_code == 400
    assert fetch_feeds.times_called == log_status.times_called == 1
