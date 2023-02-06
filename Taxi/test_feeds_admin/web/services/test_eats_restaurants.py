import json

from aiohttp import web
import pytest

from feeds_admin import models
from feeds_admin.services import eats_restaurants
from test_feeds_admin import common
from test_feeds_admin import const


NOTIFICATION = 'eats-restaurants-notification'
NEWS = 'eats-restaurants-news'
SURVEY = 'eats-restaurants-survey'

ALL = {'recipient_type': 'all'}
RESTAURANTS = {
    'recipient_type': 'restaurant',
    'recipients_ids': ['1', '2', '3'],
}
PARTNERS = {'recipient_type': 'partner_id', 'recipients_ids': ['1', '2', '3']}
BRAND = {'recipient_type': 'brand', 'recipients_ids': ['100']}
CITY = {'recipient_type': 'city', 'recipients_ids': ['moscow']}
YQL = {'yql_link': 'just_link'}


@pytest.mark.parametrize(
    'service,payload_file,recipients',
    [
        (NEWS, 'news_tutorial_payload.json', ALL),
        (NEWS, 'news_tutorial_payload.json', RESTAURANTS),
        (NEWS, 'news_tutorial_payload.json', PARTNERS),
        (NEWS, 'news_tutorial_payload.json', BRAND),
        (NEWS, 'news_article_payload.json', CITY),
        (NEWS, 'news_service_payload.json', YQL),
        (NOTIFICATION, 'notification_payload.json', ALL),
        (SURVEY, 'survey_payload.json', ALL),
    ],
)
async def test_lifecycle(
        web_app_client, patch, load, service, payload_file, recipients,
):
    payload = json.loads(load(payload_file))
    schedule = {
        'recurrence': 'once',
        'first_publish_at': '3000-01-01T00:00:00+0300',
        'ttl_seconds': 5 * 24 * 3600,
    }
    # Create
    response = await web_app_client.post(
        '/v1/eats-restaurants/create',
        headers={'X-Yandex-Login': 'v-belikov'},
        json={
            'service': service,
            'name': 'RestApp',
            'payload': payload,
            'recipients': recipients,
            'schedule': schedule,
        },
    )
    assert response.status == 200
    feed_id = (await response.json())['id']

    # Get
    response = await web_app_client.get(
        '/v1/eats-restaurants/get', params={'service': service, 'id': feed_id},
    )
    assert response.status == 200
    body = await response.json()
    body.pop('created')
    body.pop('updated')
    assert body == {
        'id': feed_id,
        'service': service,
        'name': 'RestApp',
        'status': 'created',
        'payload': payload,
        'author': 'v-belikov',
        'schedule': schedule,
        'recipients': recipients,
        'ticket': '',
    }

    # Update
    response = await web_app_client.post(
        '/v1/eats-restaurants/update',
        json={
            'id': feed_id,
            'service': service,
            'name': 'Changed name',
            'payload': payload,
            'recipients': recipients,
            'schedule': schedule,
        },
    )
    assert response.status == 200

    response = await web_app_client.get(
        '/v1/eats-restaurants/get', params={'service': service, 'id': feed_id},
    )
    assert response.status == 200
    body = await response.json()
    body.pop('created')
    body.pop('updated')
    assert body == {
        'id': feed_id,
        'service': service,
        'name': 'Changed name',
        'status': 'created',
        'payload': payload,
        'author': 'v-belikov',
        'schedule': schedule,
        'recipients': recipients,
        'ticket': '',
    }


@pytest.mark.pgsql('feeds_admin', files=['feeds_admin_purge.sql'])
@pytest.mark.config(TVM_RULES=[{'dst': 'feeds', 'src': 'feeds-admin'}])
async def test_purge(web_app_client, mock_feeds):
    params = {'id': const.UUID_1, 'service': NEWS}
    calls = []

    @mock_feeds('/v1/batch/remove_by_request_id')
    async def feeds_remove_by_request_id(request):  # pylint: disable=W0612
        calls.append('called')
        return web.json_response({'statuses': {}})

    response = await web_app_client.post(
        '/v1/eats-restaurants/purge', json=params,
    )
    assert response.status == 200

    updated_feed = await web_app_client.get(
        '/v1/eats-restaurants/get', params=params,
    )
    content = await updated_feed.json()
    assert content['status'] == 'finished'
    assert len(calls) == 1


@pytest.mark.pgsql('feeds_admin', files=['feeds_admin_stop.sql'])
async def test_stop(web_app_client, mock_feeds):
    params = {'id': const.UUID_1, 'service': 'eats-restaurants-news'}

    response = await web_app_client.post(
        '/v1/eats-restaurants/stop', json=params,
    )
    assert response.status == 200

    updated_feed = await web_app_client.get(
        '/v1/eats-restaurants/get', params=params,
    )
    content = await updated_feed.json()
    assert content['status'] == 'published'


@pytest.mark.pgsql('feeds_admin', files=['feeds_admin_get.sql'])
async def test_list(web_app_client):
    response = await web_app_client.post(
        '/v1/eats-restaurants/list', json={'services': [NEWS, SURVEY]},
    )
    body = await response.json()
    assert body['total'] == 2
    assert body['items']
    result_news = body['items'][0]
    assert result_news == {
        'id': const.UUID_1,
        'service': NEWS,
        'name': 'RestApp',
        'status': 'created',
        'author': 'v-belikov',
        'created': '2019-12-30T00:00:00+0300',
        'first_publish_at': '2020-01-01T00:00:00+0300',
        'media_id': '3f30427b198b4d56be1aecaf73c83597',
        'recipients_type': 'all',
        'recurrence_type': 'once',
    }

    result_survey = body['items'][1]
    assert result_survey == {
        'id': const.UUID_3,
        'service': SURVEY,
        'name': 'RestApp',
        'status': 'created',
        'author': 'v-belikov',
        'created': '2019-12-30T00:00:00+0300',
        'first_publish_at': '2020-01-01T00:00:00+0300',
        'recipients_type': 'city',
        'recurrence_type': 'once',
    }


@pytest.mark.parametrize(
    'feed_id,target_service,payload_file,recipients,raw_channel,channel',
    [
        (const.UUID_1, NEWS, 'news_tutorial_payload.json', ALL, None, 'all'),
        (
            const.UUID_2,
            NOTIFICATION,
            'notification_payload.json',
            BRAND,
            '100',
            'brand:100',
        ),
        (
            const.UUID_3,
            SURVEY,
            'survey_payload.json',
            CITY,
            'moscow',
            'city:moscow',
        ),
    ],
)
async def test_service(
        web_app_client,
        load,
        feed_id,
        target_service,
        payload_file,
        recipients,
        raw_channel,
        channel,
):
    publication = common.create_fake_publication(target_service)

    publication.feed.payload = json.loads(load(payload_file))

    recipient_group = publication.recipients_groups[0]
    recipient_group.group_settings['type'] = 'restaurant'

    recipients = [
        models.recipients.Recipient(recipient_id='dbid_uuid1'),
        models.recipients.Recipient(recipient_id='dbid_uuid2'),
    ]

    service = eats_restaurants.EatsRestaurantsService(target_service)

    channels = await service.make_channels(
        publication, recipient_group, recipients,
    )
    assert channels == ['restaurant:dbid_uuid1', 'restaurant:dbid_uuid2']

    payload = await service.make_payload(publication)
    assert payload == publication.feed.payload

    for yql_field in eats_restaurants.YqlRecipientField:
        query = models.service.YQLQuery(
            yql_link='link',
            column_names=[yql_field.value, 'name'],
            parse_context={},
        )

        service.begin_yql(query, recipient_group)

        recipient = service.parse_yql_row(
            {yql_field.value: '123', 'name': 'Rest #123'},
            query,
            recipient_group,
        )

        assert recipient == models.recipients.Recipient(
            recipient_id='123', payload_params={'name': 'Rest #123'},
        )
        assert (
            recipient_group.group_settings['type']
            == eats_restaurants.YQL_RECIPIENT_FIELD_TO_RECIPIENT_TYPE[
                yql_field
            ].value
        )
