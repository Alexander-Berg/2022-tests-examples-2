# flake8: noqa
# pylint: disable=import-error,wildcard-import
from market_content_storage_mappings_plugins.generated_tests import *

from datetime import datetime, timedelta, timezone
from google.protobuf.timestamp_pb2 import Timestamp
from market.idx.datacamp.proto.api.DatacampMessage_pb2 import DatacampMessage
from market.idx.datacamp.proto.offer.DataCampOffer_pb2 import (
    ReadinessForPublicationStatus,
)
from market.idx.datacamp.proto.offer.OfferMeta_pb2 import MarketColor
from market.pylibrary.proto_utils import message_from_data

import base64
import json
import pytest
import psycopg2

OFFER_YABS_ID_1 = 1
OFFER_YABS_ID_2 = 2
OFFER_YABS_ID_3 = 3
OFFER_YABS_ID_4 = 4
OFFER_YABS_ID_5 = 5
OFFER_YABS_ID_6 = 6


def make_offer_with_defaults(offer):
    defaultOffer = {
        'business_id': 1,
        'shop_id': 2,
        'warehouse_id': 3,
        'feed_id': 4,
        'model_id': 42,
        'market_sku_id': 24,
        'ts': getMidday(),
        'ready_for_publication': ReadinessForPublicationStatus.READY,
        'ready_for_publication_ts': getMidday() - timedelta(weeks=1),
        'disabled': False,
        'disabled_ts': getMidday() - timedelta(weeks=3),
        'approved': False,
    }
    offerId = {
        # offer_yabs_id is mandatory
        'offer_id': 'offer' + str(offer['offer_yabs_id']),
    }

    result = {**defaultOffer, **offerId, **offer}
    result['ware_md5'] = str(result['warehouse_id'])
    return result


def getMidday():
    result = datetime.now()
    result = result.replace(
        hour=12, minute=0, second=0, microsecond=0, tzinfo=timezone.utc,
    )
    return result


def convertTimestamp(dt):
    ts = Timestamp()
    ts.FromDatetime(dt)
    return ts


def make_offer(offer):
    offer = make_offer_with_defaults(offer)
    business_id = offer['business_id']
    offer_yabs_id = offer['offer_yabs_id']
    shop_id = offer['shop_id']
    warehouse_id = offer['warehouse_id']
    offer_id = offer['offer_id']

    # if warehouse_id is None, we create a pure service offer (should be filtered out)
    warehouse = (
        {
            'warehouse_id': warehouse_id,
            'extra': {'ware_md5': str(warehouse_id)},
        }
        if warehouse_id is not None
        else {}
    )

    force_send = offer.get('force_send')
    binding_key = 'approved' if offer['approved'] else 'uc_mapping'

    return {
        'basic': {
            'identifiers': {
                'business_id': business_id,
                'offer_id': offer_id,
                'extra': {'offer_yabs_id': offer_yabs_id},
            },
            'content': {
                'binding': {
                    binding_key: {
                        'market_model_id': offer['model_id'],
                        'market_sku_id': offer['market_sku_id'],
                        'meta': {
                            'timestamp': convertTimestamp(
                                offer['ts'],
                            ).ToJsonString(),
                        },
                    },
                },
            },
            'status': {},
            'meta': (
                {
                    'content_storage_mappings_force_send': {
                        'ts': convertTimestamp(force_send).ToJsonString(),
                    },
                }
                if force_send
                else {}
            ),
        },
        'service': {
            shop_id: {
                'identifiers': {
                    **{
                        'business_id': business_id,
                        'shop_id': shop_id,
                        'feed_id': offer['feed_id'],
                        'offer_id': offer_id,
                    },
                    **warehouse,
                },
                'status': {
                    'disabled': [
                        {
                            'flag': offer['disabled'],
                            'meta': {
                                'timestamp': convertTimestamp(
                                    offer['disabled_ts'],
                                ).ToJsonString(),
                            },
                        },
                    ],
                    'ready_for_publication': {
                        'value': offer['ready_for_publication'],
                        'meta': {
                            'timestamp': convertTimestamp(
                                offer['ready_for_publication_ts'],
                            ).ToJsonString(),
                        },
                    },
                },
            },
        },
    }


async def send_offers(taxi_market_content_storage_mappings, testpoint, offers):
    message = message_from_data(
        {
            'united_offers': [
                {'offer': [make_offer(offer) for offer in offers]},
            ],
        },
        DatacampMessage(),
    )

    @testpoint('logbroker_commit')
    def commit(cookie):
        assert cookie == 'cookie1'

    response = await taxi_market_content_storage_mappings.post(
        'tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'positions',
                'data_b64': base64.b64encode(
                    message.SerializeToString(),
                ).decode(),
                'topic': (
                    '/market-mbo/testsuite/datacamp/datacamp-fast-mappings'
                ),
                'cookie': 'cookie1',
            },
        ),
    )
    assert response.status_code == 200

    await commit.wait_call()


@pytest.mark.parametrize(
    'offers',
    [
        [
            {'offer_yabs_id': OFFER_YABS_ID_1},
            {'offer_yabs_id': OFFER_YABS_ID_2},
            # special case when there is no mapping (yet?)
            {
                'offer_yabs_id': OFFER_YABS_ID_3,
                'model_id': 0,
                'market_sku_id': -1,
            },
            # regression test: model_id and market_sku_id are 64-bit
            {
                'offer_yabs_id': OFFER_YABS_ID_4,
                'model_id': 100439187587,
                'market_sku_id': 100439187587,
            },
            # check approved mapping offers (also fast cards)
            {'offer_yabs_id': OFFER_YABS_ID_5, 'approved': True},
        ],
    ],
)
async def test_basic_message(
        offers, taxi_market_content_storage_mappings, testpoint, pgsql,
):
    await send_offers(taxi_market_content_storage_mappings, testpoint, offers)

    cursor = pgsql['market_content_storage_mappings'].cursor()

    for offer in offers:
        offer = make_offer_with_defaults(offer)
        query = """SELECT model_id, market_sku_id, ware_md5, feed_id, offer_id
            FROM market_content_storage_mappings.offers
            WHERE business_id = {} AND offer_yabs_id = {} AND shop_id = {} AND warehouse_id = {}"""

        cursor.execute(
            query.format(
                offer['business_id'],
                offer['offer_yabs_id'],
                offer['shop_id'],
                offer['warehouse_id'],
            ),
        )
        result = list(row for row in cursor)

        assert result == [
            (
                offer['model_id'],
                offer['market_sku_id'],
                offer['ware_md5'],
                offer['feed_id'],
                offer['offer_id'],
            ),
        ]


# Tests cases when offers should not be processed by the service
@pytest.mark.parametrize(
    'offers',
    [
        [
            {'offer_yabs_id': OFFER_YABS_ID_1, 'warehouse_id': None},
            {'offer_yabs_id': OFFER_YABS_ID_2, 'warehouse_id': 0},
        ],
    ],
)
async def test_filtering(
        offers, taxi_market_content_storage_mappings, testpoint, pgsql,
):
    await send_offers(taxi_market_content_storage_mappings, testpoint, offers)

    cursor = pgsql['market_content_storage_mappings'].cursor()
    cursor.execute('SELECT * FROM market_content_storage_mappings.offers')
    result = list(row for row in cursor)
    assert result == []


# Tests case when older offer arrives after the new one
@pytest.mark.parametrize(
    'offers',
    [
        [
            # this offer is OK
            {
                'offer_yabs_id': OFFER_YABS_ID_1,
                'model_id': 42,
                'ts': getMidday() - timedelta(hours=2),
            },
            # this offer should overwrite the previous one since TS is newer
            {
                'offer_yabs_id': OFFER_YABS_ID_1,
                'model_id': 24,
                'ts': getMidday(),
            },
            # this offer should NOT overwrite the previous one since TS is older
            {
                'offer_yabs_id': OFFER_YABS_ID_1,
                'model_id': 42,
                'ts': getMidday() - timedelta(hours=1),
            },
            # this offer is too old to get into DB
            {
                'offer_yabs_id': OFFER_YABS_ID_2,
                'model_id': 24,
                'ts': getMidday() - timedelta(weeks=3),
                'ready_for_publication_ts': getMidday() - timedelta(weeks=3),
            },
            # this offer is almost too old but OK
            {
                'offer_yabs_id': OFFER_YABS_ID_3,
                'model_id': 42,
                'ts': getMidday() - timedelta(weeks=1, days=6),
                'ready_for_publication_ts': getMidday() - timedelta(weeks=3),
            },
            # ready_for_publication is newer than ts, so offer should not be removed
            {
                'offer_yabs_id': OFFER_YABS_ID_4,
                'model_id': 4242,
                'ts': getMidday() - timedelta(weeks=3),
                'ready_for_publication_ts': getMidday() - timedelta(hours=2),
            },
            # offer is not disabled and disabled_ts is newer than others
            {
                'offer_yabs_id': OFFER_YABS_ID_5,
                'model_id': 42,
                'ts': getMidday() - timedelta(weeks=3),
                'ready_for_publication_ts': getMidday() - timedelta(weeks=3),
                'disabled_ts': getMidday(),
            },
            # offer is disabled and it's TS should be ignored
            {
                'offer_yabs_id': OFFER_YABS_ID_5,
                'model_id': 42,
                'ts': getMidday() - timedelta(weeks=3),
                'ready_for_publication_ts': getMidday() - timedelta(weeks=3),
                'disabled': True,
                'disabled_ts': getMidday(),
            },
        ],
    ],
)
async def test_timestamp(
        offers, taxi_market_content_storage_mappings, testpoint, pgsql,
):
    # we need to process offers one by one here since bulk insert cannot have
    # duplicate keys
    for offer in offers:
        await send_offers(
            taxi_market_content_storage_mappings, testpoint, [offer],
        )

    cursor = pgsql['market_content_storage_mappings'].cursor()
    cursor.execute(
        'SELECT offer_yabs_id, model_id FROM market_content_storage_mappings.offers',
    )
    result = list(row for row in cursor)
    assert result == [
        (OFFER_YABS_ID_1, 24),
        (OFFER_YABS_ID_3, 42),
        (OFFER_YABS_ID_4, 4242),
        (OFFER_YABS_ID_5, 42),
    ]


# TODO: add more cases (e.g. removed flag and MARKET_IDX flag)
@pytest.mark.parametrize(
    'offers',
    [
        [
            # the offer is removed as removal timestamp is newer than update timestamp
            {'offer_yabs_id': OFFER_YABS_ID_1},
            {
                'offer_yabs_id': OFFER_YABS_ID_1,
                'ready_for_publication': (
                    ReadinessForPublicationStatus.NOT_READY
                ),
                'ts': getMidday(),
                'ready_for_publication_ts': getMidday() + timedelta(hours=1),
            },
            # this offer is not removed as removal timestamp is older than update timestamp
            {'offer_yabs_id': OFFER_YABS_ID_2, 'ts': getMidday()},
            {
                'offer_yabs_id': OFFER_YABS_ID_2,
                'ready_for_publication': (
                    ReadinessForPublicationStatus.NOT_READY
                ),
                'ts': getMidday(),
                'ready_for_publication_ts': (getMidday() - timedelta(hours=1)),
            },
        ],
    ],
)
async def test_removal(
        offers, taxi_market_content_storage_mappings, testpoint, pgsql,
):

    await send_offers(taxi_market_content_storage_mappings, testpoint, offers)
    cursor = pgsql['market_content_storage_mappings'].cursor()
    cursor.execute(
        'SELECT offer_yabs_id FROM market_content_storage_mappings.offers',
    )
    result = list(row for row in cursor)
    assert result == [(OFFER_YABS_ID_2,)]


@pytest.mark.parametrize(
    'offers',
    [
        [
            # the offer is removed as removal timestamp is newer than update timestamp (see default values)
            {'offer_yabs_id': OFFER_YABS_ID_1, 'ts': getMidday()},
            {
                'offer_yabs_id': OFFER_YABS_ID_1,
                'ts': getMidday(),
                'force_send': (getMidday() + timedelta(hours=1)),
            },
        ],
    ],
)
async def test_force_send(
        offers, taxi_market_content_storage_mappings, testpoint, pgsql,
):
    # need to send offer one by one to emulate different batches
    for offer in offers:
        await send_offers(
            taxi_market_content_storage_mappings, testpoint, [offer],
        )
    cursor = pgsql['market_content_storage_mappings'].cursor()
    cursor.execute(
        'SELECT offer_yabs_id, ts FROM market_content_storage_mappings.offers',
    )
    result = list(row for row in cursor)
    assert result == [(OFFER_YABS_ID_1, (getMidday() + timedelta(hours=1)))]
