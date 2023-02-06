import json

from feeds_admin.services import taxi_summary_promo
from test_feeds_admin import common


async def test_service(web_app_client, patch, load):
    publication = common.create_fake_publication('taxi-summary-promo')
    publication.feed.payload = json.loads(load('discount_promo_payload.json'))
    publication.feed.settings = json.loads(
        load('discount_promo_settings.json'),
    )

    recipients_group = publication.recipients_groups[0]
    recipients = []

    service = taxi_summary_promo.TaxiSummaryPromoService('taxi-summary-promo')

    # Test channels
    channels = await service.make_channels(
        publication, recipients_group, recipients,
    )
    assert channels == ['discount:promo_mastercard']

    # Test payload
    payload = await service.make_payload(publication)
    expected_payload = json.loads(load('expected_discount_promo_payload.json'))
    assert payload == expected_payload
