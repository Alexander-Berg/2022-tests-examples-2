# flake8: noqa
# pylint: disable=import-error,wildcard-import

import os
import pytest
import shutil
import yatest.common

from market.proto.abo.BlueOfferFilter_pb2 import BlueOfferInfo, BlueOfferFilter
from market.pylibrary.pbufsn_utils import make_pbufsn

ABO_MAGIC = b'BOFR'
DIR = 'uhor'
ABO_FILE = 'abo.pbuf'
MMAP_FILE = 'mmap.mmap'

ID1 = 1
ID2 = 2
ID3 = 3

YABS_ID1 = '1'
YABS_ID2 = '2'
YABS_ID3 = '3'

MOSCOW = 213


REDIS_KEY_1 = bytearray(
    [
        0x7B,
        0x1,  # MSKU
        0x0,
        0x7D,
        0x1,  # FEED-ID
        0x0,
        0x0,
        0x0,
        0x1,  # OFFER-ID
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
    ],
)
REDIS_KEY_2 = bytearray(
    [
        0x7B,
        0x2,  # MSKU
        0x0,
        0x7D,
        0x2,  # FEED-ID
        0x0,
        0x0,
        0x0,
        0x2,  # OFFER-ID
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
    ],
)
REDIS_VALUE_DENIED = bytearray(
    [
        0x03,  # AVAILABLE + DISABLED BIT
        0x01,
        0x01,
        0x01,
        0x01,
        0x01,
        0x01,
        0x01,
        0x01,
        0x01,
        0x01,
        0x01,
        0x01,
        0x01,
        0x01,
        0x01,
    ],
)
REDIS_VALUE_ALLOWED = bytearray(
    [
        0x01,  # AVAILABLE + !DISABLED BIT
        0x01,
        0x01,
        0x01,
        0x01,
        0x01,
        0x01,
        0x01,
        0x01,
        0x01,
        0x01,
        0x01,
        0x01,
        0x01,
        0x01,
        0x01,
    ],
)


class AboRule:
    def __init__(self, id, shop_sku):
        self.id = id
        self.shop_sku = shop_sku


class BusinessOffer:
    def __init__(self, id, yabs_id, features):
        self.category_id = id
        self.business_id = id
        self.model_id = id
        self.msku_id = id
        self.vendor_id = id
        self.yabs_id = yabs_id
        self.features = features


class ServiceOffer:
    def __init__(self, id, features, status):
        self.shop_id = id
        self.warehouse_id = id
        self.feed_id = id
        self.features = features
        self.status = status


class RequestInfo:
    def __init__(self, region, features):
        self.region = region
        self.features = features


class Request:
    def __init__(self, business_offer, service_offers, request_info):
        self.business_offer = business_offer
        self.service_offers = service_offers
        self.request_info = request_info


class Response:
    def __init__(self, business_offer, service_offers):
        self.business_offer = business_offer
        self.service_offers = service_offers


async def prepare_test_api(
        taxi_market_hide_offers_rt, dir, abo_file, mmap_file,
):
    response = await taxi_market_hide_offers_rt.post(
        '/v1/internal/prepare_test_data',
        json={
            'dir': yatest.common.work_path() + '/' + dir,
            'abo_file': abo_file,
            'mmap_file': mmap_file,
        },
    )
    assert response.status_code == 200


async def prepare_abo_data(abo_rules, taxi_market_hide_offers_rt):
    path = yatest.common.work_path() + '/' + DIR
    if not os.path.exists(path):
        os.mkdir(path)

    infos = []
    for abo_rule in abo_rules:
        infos.append(
            BlueOfferInfo(
                MarketSku=abo_rule.id,
                SupplierId=abo_rule.id,
                ShopSku=abo_rule.shop_sku,
                ModelId=abo_rule.id,
            ),
        )

    data = [BlueOfferFilter(Infos=infos)]
    path = yatest.common.work_path() + '/' + DIR + '/' + ABO_FILE
    make_pbufsn(path=path, magic=ABO_MAGIC, proto_iter=data)

    await prepare_test_api(
        taxi_market_hide_offers_rt, DIR, ABO_FILE, MMAP_FILE,
    )


def prepare_request_data(requests):
    # To see full API scheme:
    # https://a.yandex-team.ru/arcadia/taxi/uservices/services/market-hide-offers-rt/docs/yaml/api/api.yaml
    items = []
    for request in requests:
        service_offers = []
        for service_offer in request.service_offers:
            service_offers.append(
                {
                    'id': {
                        'shop_id': service_offer.shop_id,
                        'warehouse_id': service_offer.warehouse_id,
                        'feed_id': service_offer.feed_id,
                        'features': service_offer.features,
                    },
                    'features': service_offer.features,
                },
            )

        items.append(
            {
                'yabs_id': request.business_offer.yabs_id,
                'business_id': request.business_offer.business_id,
                'content': {
                    'category_id': request.business_offer.category_id,
                    'model_id': request.business_offer.model_id,
                    'msku_id': request.business_offer.msku_id,
                    'vendor_id': request.business_offer.vendor_id,
                    'features': request.business_offer.features,
                },
                'service_offers': service_offers,
            },
        )

    request_info = {
        'region': request.request_info.region,
        'features': request.request_info.features,
    }

    return {'items': items, 'request_info': request_info}


def prepare_response_data(responses):
    # To see full API scheme:
    # https://a.yandex-team.ru/arcadia/taxi/uservices/services/market-hide-offers-rt/docs/yaml/api/api.yaml
    items = []
    for response in responses:
        service_offers = []
        for service_offer in response.service_offers:
            service_offers.append(
                {
                    'id': {
                        'features': service_offer.features,
                        'feed_id': service_offer.feed_id,
                        'shop_id': service_offer.shop_id,
                        'warehouse_id': service_offer.warehouse_id,
                    },
                    'status': service_offer.status,
                },
            )

        items.append(
            {
                'business_id': response.business_offer.business_id,
                'service_offers': service_offers,
                'yabs_id': response.business_offer.yabs_id,
            },
        )

    return {'items': items}
