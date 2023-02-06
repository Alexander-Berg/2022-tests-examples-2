# flake8: noqa
# pylint: disable=import-error,wildcard-import
from market_fast_mappings_reader_plugins.generated_tests import *

from tests_market_fast_mappings_reader.utils import *
from google.protobuf.json_format import MessageToDict

import asyncio
import grpc
import pytest

from fast_mappings.v1 import fast_mappings_pb2_grpc
from fast_mappings.v1 import fast_mappings_pb2


@pytest.mark.pgsql('market_content_storage_mappings', files=['test_data.sql'])
async def test_all_fields(grpc_mappings_channel, testpoint, pgsql):
    stub = fast_mappings_pb2_grpc.MappingsServiceStub(grpc_mappings_channel)
    request = fast_mappings_pb2.MappingsRequest(
        ModelIds=[10], OfferFields=fast_mappings_pb2.All,
    )
    response = MessageToDict(await stub.GetMappings(request))
    offers = {
        10: {
            'Offers': [
                {
                    'BusinessId': '3',
                    'OfferYabsId': '30',
                    'ShopId': '300',
                    'WarehouseId': '3000',
                    'ModelId': '10',
                    'MskuId': '20',
                    'WareMd5': 'waremd5.5',
                    'FeedId': 333,
                    'OfferId': 'shop.3,offer.3',
                },
            ],
        },
    }
    assert response['ModelOffers'] == offers


#  checks report format
@pytest.mark.pgsql('market_content_storage_mappings', files=['test_data.sql'])
async def test_report(grpc_mappings_channel, testpoint, pgsql):
    stub = fast_mappings_pb2_grpc.MappingsServiceStub(grpc_mappings_channel)
    offerFields = fast_mappings_pb2.FeedId | fast_mappings_pb2.OfferId
    request = fast_mappings_pb2.MappingsRequest(
        ModelIds=[42], MskuIds=[24], OfferFields=offerFields,
    )
    response = MessageToDict(await stub.GetMappings(request))
    mskuOffers = {
        24: {
            'Offers': [
                {'FeedId': 111, 'OfferId': 'shop.1,offer.1'},
                {'FeedId': 222, 'OfferId': 'shop.2,offer.1'},
            ],
        },
    }
    assert response['MskuOffers'] == mskuOffers
    assert 'ModelOffers' not in response


#  checks that models are filtered based on mskus
@pytest.mark.pgsql('market_content_storage_mappings', files=['test_data.sql'])
async def test_model_filtering(grpc_mappings_channel, testpoint, pgsql):
    stub = fast_mappings_pb2_grpc.MappingsServiceStub(grpc_mappings_channel)
    offerFields = fast_mappings_pb2.WareMd5
    request = fast_mappings_pb2.MappingsRequest(
        ModelIds=[42, 100], MskuIds=[500], OfferFields=offerFields,
    )
    response = MessageToDict(await stub.GetMappings(request))
    mskuOffers = {500: {'Offers': [{'WareMd5': 'waremd5.2'}]}}
    modelOffers = {
        42: {'Offers': [{'WareMd5': 'waremd5.1'}, {'WareMd5': 'waremd5.3'}]},
    }
    assert response['MskuOffers'] == mskuOffers
    assert response['ModelOffers'] == modelOffers


#  checks huge model_id
@pytest.mark.pgsql('market_content_storage_mappings', files=['test_data.sql'])
async def test_huge_model_id(grpc_mappings_channel, testpoint, pgsql):
    stub = fast_mappings_pb2_grpc.MappingsServiceStub(grpc_mappings_channel)
    offerFields = (
        fast_mappings_pb2.FeedId
        | fast_mappings_pb2.OfferId
        | fast_mappings_pb2.ModelId
    )
    request = fast_mappings_pb2.MappingsRequest(
        ModelIds=[100439187587], OfferFields=offerFields,
    )
    response = MessageToDict(await stub.GetMappings(request))
    modelOffers = {
        100439187587: {
            'Offers': [
                {
                    'FeedId': 444,
                    'OfferId': 'shop.4,offer.1',
                    'ModelId': '100439187587',
                },
            ],
        },
    }
    assert response['ModelOffers'] == modelOffers
    assert 'MskuOffers' not in response


@pytest.mark.pgsql('market_content_storage_mappings', files=['test_data.sql'])
async def test_waremd5(grpc_mappings_channel, testpoint, pgsql):
    stub = fast_mappings_pb2_grpc.MappingsServiceStub(grpc_mappings_channel)
    offerFields = fast_mappings_pb2.FeedId | fast_mappings_pb2.OfferId
    request = fast_mappings_pb2.OffersRequest(
        WareMd5s=['waremd5.2', 'waremd5.5'], OfferFields=offerFields,
    )
    response = MessageToDict(await stub.GetOffers(request))
    offers = [
        {'FeedId': 111, 'OfferId': 'shop.1,offer.2'},
        {'FeedId': 333, 'OfferId': 'shop.3,offer.3'},
    ]
    assert response['WareMd5Offers'] == offers


@pytest.mark.pgsql('market_content_storage_mappings', files=['test_data.sql'])
async def test_all_fields_http(taxi_market_fast_mappings_reader, pgsql):
    offer1 = [
        {
            'business_id': 3,
            'offer_yabs_id': 30,
            'shop_id': 300,
            'warehouse_id': 3000,
            'model_id': 10,
            'market_sku_id': 20,
            'ware_md5': 'waremd5.5',
            'feed_id': 333,
            'offer_id': 'shop.3,offer.3',
        },
    ]
    offer2 = [
        {
            'business_id': 4,
            'offer_yabs_id': 40,
            'shop_id': 400,
            'warehouse_id': 4000,
            'model_id': 100439187587,
            'market_sku_id': 100439187587,
            'ware_md5': 'waremd5.6',
            'feed_id': 444,
            'offer_id': 'shop.4,offer.1',
        },
    ]
    response = await taxi_market_fast_mappings_reader.get(
        '/fast_mappings/v1/mappings?model_ids=10,100439187587',
    )

    assert response.status_code == 200
    assert response.json()['model_offers'] == {
        '10': offer1,
        '100439187587': offer2,
    }
    assert response.json()['market_sku_offers'] == {}

    response = await taxi_market_fast_mappings_reader.get(
        '/fast_mappings/v1/mappings?market_sku_ids=20,100439187587',
    )
    assert response.status_code == 200
    assert response.json()['model_offers'] == {}
    assert response.json()['market_sku_offers'] == {
        '20': offer1,
        '100439187587': offer2,
    }
