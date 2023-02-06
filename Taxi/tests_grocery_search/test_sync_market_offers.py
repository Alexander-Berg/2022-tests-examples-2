# pylint: disable=import-error

import base64
import datetime

from arc_market.idx.datacamp.proto.api import ExportMessage_pb2
from arc_market.idx.datacamp.proto.external import Offer_pb2
from arc_market.idx.datacamp.proto.offer import OfferMeta_pb2
from google.protobuf import timestamp_pb2
import pytest


NEW_EVENT_TIME = '2021-08-09T12:10:10+00:00'
PRODUCT_ID = 'product-1'
DEPOT_ID = 'depot-1'
AVAILABLE = False
FULL_PRICE = 10
MBI_BY_LOCALE = {
    'ru': {
        'service_id': 'lavka:ru',
        'eats_and_lavka_id': DEPOT_ID,
        'market_feed_id': 1,
        'partner_id': 2,
        'business_id': 3,
    },
    'en': {
        'service_id': 'lavka:en',
        'eats_and_lavka_id': DEPOT_ID,
        'market_feed_id': 10,
        'partner_id': 20,
        'business_id': 30,
    },
}


def _convert_datetime_iso_format_to_timestamp(datetime_in_iso_format):
    raw_time = datetime.datetime.fromisoformat(datetime_in_iso_format).replace(
        tzinfo=datetime.timezone.utc,
    )
    time = raw_time.timestamp()
    seconds = int(time)
    nanos = int((time - seconds) * 10 ** 9)
    return timestamp_pb2.Timestamp(seconds=seconds, nanos=nanos)


def _create_expected_offer(locale='ru'):
    expected = Offer_pb2.Offer()
    expected.business_id = MBI_BY_LOCALE[locale]['business_id']
    expected.offer_id = PRODUCT_ID
    expected.shop_prices.append(
        Offer_pb2.IdentifiedPrice(
            meta=OfferMeta_pb2.UpdateMeta(
                timestamp=_convert_datetime_iso_format_to_timestamp(
                    NEW_EVENT_TIME,
                ),
            ),
            shop_id=MBI_BY_LOCALE[locale]['partner_id'],
            price=Offer_pb2.OfferPrice(
                currency=Offer_pb2.OfferPrice.Currency.RUR,
                price=int(FULL_PRICE * 1e7),
            ),
        ),
    )

    disable_status = {}
    disable_status[OfferMeta_pb2.DataSource.PUSH_PARTNER_API] = (
        OfferMeta_pb2.Flag(
            meta=OfferMeta_pb2.UpdateMeta(
                timestamp=_convert_datetime_iso_format_to_timestamp(
                    NEW_EVENT_TIME,
                ),
            ),
            flag=not AVAILABLE,
        )
    )
    expected.shop_statuses.append(
        Offer_pb2.IdentifiedStatus(
            disable_status=disable_status,
            shop_id=MBI_BY_LOCALE[locale]['partner_id'],
        ),
    )
    return expected


# Проверяет, что market-offers-sync-component отсылает в LogBroker события,
# принятые из ручки overlord-catalog/pull-event-queue.
@pytest.mark.suspend_periodic_tasks('market-offers-sync-component')
@pytest.mark.config(GROCERY_OVERLORD_CACHES_MBI_SUPPORTED_LOCALES=['ru', 'en'])
async def test_sync_market_offers(
        taxi_grocery_search,
        overlord_catalog,
        grocery_depots,
        mbi_api,
        testpoint,
):
    @testpoint('publish')
    def _publish(data):
        _publish.calls += 1

        expected = _create_expected_offer(
            'ru' if _publish.calls == 1 else 'en',
        )
        published = ExportMessage_pb2.ExportMessage.FromString(
            base64.b64decode(data),
        ).offer
        assert expected == published

    _publish.calls = 0

    grocery_depots.add_depot(depot_test_id=1, legacy_depot_id='depot-1')
    overlord_catalog.set_products_events(
        {
            'availability_changed': [
                {
                    'event': 'availability_changed',
                    'product_id': PRODUCT_ID,
                    'availabilities_per_depots': [
                        {
                            'available': AVAILABLE,
                            'available_updated': NEW_EVENT_TIME,
                            'depot_id': 'wms-depot-1',
                            'external_depot_id': DEPOT_ID,
                        },
                    ],
                },
            ],
            'full_price_changed': [
                {
                    'event': 'full_price_changed',
                    'product_id': PRODUCT_ID,
                    'full_prices_per_depots': [
                        {
                            'depot_id': 'wms-depot-1',
                            'external_depot_id': DEPOT_ID,
                            'full_price': str(FULL_PRICE),
                            'full_price_updated': NEW_EVENT_TIME,
                        },
                    ],
                },
            ],
        },
    )

    mbi_api.add_depot(**MBI_BY_LOCALE['ru'])
    mbi_api.add_depot(**MBI_BY_LOCALE['en'])

    await taxi_grocery_search.invalidate_caches()
    await taxi_grocery_search.run_periodic_task('market-offers-sync-component')

    # Дожидаемся полной обработки сообщения в сервисе, т.е.
    # дожидаемся вызова testpoint
    await _publish.wait_call()
