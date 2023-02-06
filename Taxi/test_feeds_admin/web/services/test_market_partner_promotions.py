import copy
import json

from aiohttp import web
import pytest

from feeds_admin import models
from feeds_admin.services import market_partner_promotions
from test_feeds_admin import common

PromoType = market_partner_promotions.PromoType


SCHEDULE = {
    'schedule_type': 'interval',
    'start_at': '2019-08-26T00:00:00+0300',
    'finish_at': '2050-08-30T00:00:00+0300',
}

RECIPIENTS_PARTNERS = {
    'recipient_type': 'partner_id',
    'partners': ['1', '2', '3', '4'],
}
RECIPIENTS_ALL = {'recipient_type': 'all'}


@pytest.mark.parametrize(
    'promo_type',
    [
        PromoType.BUSINESS_OPPORTUNITIES,
        PromoType.ADS,
        PromoType.OPERATING_ALERT,
    ],
)
@pytest.mark.config(
    FEEDS_ADMIN_SERVICES={
        '__default__': {'max_channels_for_immediate_publish': 3},
    },
    ADMIN_MARKET_PARTNER_PROMOTIONS={
        'dropdowns': {
            'page_ids': [
                {
                    'label': 'Сводка маркетплейса',
                    'value': 'market-partner:html:marketplace-summary:get',
                    'page_type': 'summary',
                },
                {
                    'label': 'Сводка магазина',
                    'value': 'market-partner:html:fulfillment-summary:get',
                    'page_type': 'internal',
                },
            ],
        },
    },
)
async def test_lifecycle(web_app_client, mock_feeds, patch, load, promo_type):
    service = promo_type.value
    payload = json.loads(load(service + '_payload.json'))
    settings = json.loads(load(service + '_settings.json'))

    @mock_feeds('/v1/batch/remove')
    async def handler(request):  # pylint: disable=W0612
        return web.json_response({'statuses': {}})

    # Create
    response = await web_app_client.post(
        '/v1/market-partner-promotions/create',
        headers={'X-Yandex-Login': 'v-belikov'},
        json={
            'service': service,
            'name': 'Promo',
            'payload': payload,
            'settings': settings,
            'schedule': SCHEDULE,
            'recipients': RECIPIENTS_PARTNERS,
            'ticket': 'TAXIINFRA-1',
        },
    )
    assert response.status == 200
    feed_id = (await response.json())['id']

    # List
    response = await web_app_client.post(
        '/v1/market-partner-promotions/list', json={'service': service},
    )
    assert response.status == 200
    body = await response.json()
    assert len(body['items']) == 1
    assert body['items'][0].pop('created') is not None
    assert body['items'][0].pop('severity', None) in (1, None)
    assert body == {
        'service': service,
        'offset': 0,
        'limit': 50,
        'total': 1,
        'items': [
            {
                'service': service,
                'id': feed_id,
                'name': 'Promo',
                'status': 'created',
                'author': 'v-belikov',
                'ticket': 'TAXIINFRA-1',
                'next_start_at': '2019-08-26T00:00:00+0300',
                'media_id': '9a5c250ea7534ce4b657e021c31e2a09',
            },
        ],
    }

    # Publish
    response = await web_app_client.post(
        '/v1/market-partner-promotions/publish',
        json={'id': feed_id, 'service': service},
    )
    assert response.status == 200

    # Unpublish
    response = await web_app_client.post(
        '/v1/market-partner-promotions/unpublish',
        json={'service': service, 'id': feed_id},
    )
    assert response.status == 200

    # Archive
    response = await web_app_client.post(
        '/v1/market-partner-promotions/archive',
        json={'service': service, 'id': feed_id},
    )
    assert response.status == 200

    # Get
    response = await web_app_client.post(
        '/v1/market-partner-promotions/get',
        json={'service': service, 'id': feed_id},
    )
    assert response.status == 200
    body = await response.json()
    assert body.pop('created') is not None
    assert body.pop('updated') is not None

    run_history = body.pop('run_history')
    assert len(run_history) == 1
    assert run_history[0]['status'] == 'cancelled'

    assert body == {
        'id': feed_id,
        'service': service,
        'name': 'Promo',
        'status': 'deleted',
        'payload': payload,
        'settings': settings,
        'schedule': SCHEDULE,
        'recipients': RECIPIENTS_PARTNERS,
        'author': 'v-belikov',
        'ticket': 'TAXIINFRA-1',
    }


@pytest.mark.parametrize(
    'promo_type,raw_recipients',
    [
        (PromoType.BUSINESS_OPPORTUNITIES, RECIPIENTS_PARTNERS),
        (PromoType.BUSINESS_OPPORTUNITIES, RECIPIENTS_ALL),
        (PromoType.ADS, RECIPIENTS_PARTNERS),
        (PromoType.ADS, RECIPIENTS_ALL),
        (PromoType.OPERATING_ALERT, RECIPIENTS_PARTNERS),
        (PromoType.OPERATING_ALERT, RECIPIENTS_ALL),
    ],
)
@pytest.mark.config(
    FEEDS_ADMIN_SERVICES={
        '__default__': {'max_channels_for_immediate_publish': 3},
    },
)
async def test_service(
        web_app_client, mock_feeds, patch, load, promo_type, raw_recipients,
):
    target_service = promo_type.value
    recipient_type = raw_recipients['recipient_type']
    partner_ids = raw_recipients.get('partners', [])

    publication = common.create_fake_publication(target_service)
    publication.feed.payload = json.loads(
        load(target_service + '_payload.json'),
    )
    publication.feed.settings = json.loads(
        load(target_service + '_settings.json'),
    )

    recipients_group = publication.recipients_groups[0]
    recipients_group.group_settings['recipient_type'] = recipient_type

    recipients = [
        models.recipients.Recipient(recipient_id=partner_id)
        for partner_id in partner_ids
    ]

    service = market_partner_promotions.MarketPartnerPromotionsService(
        target_service,
    )

    # Test channels
    channels = await service.make_channels(
        publication, recipients_group, recipients,
    )
    if recipient_type == 'all':
        assert channels == ['all']
    else:
        assert channels == [f'partner_id:{pid}' for pid in partner_ids]

    # Test payload
    payload = await service.make_payload(publication)
    expected_payload = copy.deepcopy(publication.feed.payload)
    expected_payload['display_conditions'] = publication.feed.settings[
        'display_conditions'
    ]
    assert payload == expected_payload
