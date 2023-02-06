import json
import logging
import os.path
from typing import Any
from typing import Dict
from typing import List

import pytest
from yt import yson

from generated.clients import (
    pricing_data_preparer as pricing_data_preparer_client,
)
from generated.clients import superapp_misc as superapp_misc_client
from generated.clients import taxi_tariffs_py3 as taxi_tariffs_py3_client
from generated.models import (
    pricing_data_preparer as pricing_data_preparer_models,
)
from generated.models import superapp_misc as superapp_misc_models

from driver_event_detector.generated.cron import run_cron
from driver_event_detector.models.offers import models


def _get_offer_prices_config() -> Dict[str, Any]:
    import test_driver_event_detector
    absolute_file_path = os.path.join(
        os.path.dirname(test_driver_event_detector.__file__),
        'cron',
        'static',
        'test_predict_offer_prices',
        'offer_prices_config.json',
    )
    with open(absolute_file_path) as json_file:
        return json.load(json_file)


@pytest.mark.now('2022-06-01 20:05:00')
@pytest.mark.config(
    DRIVER_EVENT_DETECTOR_PROXY_CONF={
        'current_prices_proxy': 'prices',
        'proxy_url_mapping': {'prices': 'socks5h://proxy-sample.icu:2924'},
    },
    DRIVER_EVENT_DETECTOR_OFFER_PRICES_CONFIGS=_get_offer_prices_config(),
)
async def test_predict_offer_prices(
        cron_context,
        patch,
        caplog,
        open_file,
        response_mock,
        get_stats_by_list_label_values,
):
    cron_context.secdist['settings_override']['prices'] = {
        'login': 'proxy',
        'password': 'some_password',
    }
    cron_context.secdist['settings_override'][
        'competitor_tokens_secret_key'
    ] = 'f4YqkYquf4oTL3rNQRTe5WkMFEivLGTDCuvF7Ux_NLM='

    @patch(
        'driver_event_detector.models.offers.competitors.tokens.storage.'
        'PostgresTokenStorage.fetch_tokens',
    )
    # pylint: disable=W0612
    async def fetch_tokens(*args, **kwargs) -> List[str]:
        return [
            'gAAAAABiLMIY98biTrTRatzxIIPnQbTWFe6GxeV9OIWkHgV_OOu_'
            'tBqJzkgyxm4em1vpNArYjA5fgci9xhd1DAje4RsAuGn7LwNHwEubY'
            'cupn6Xg5-GoW7cPe0nRJxHehYufcRtigikY',
            'gAAAAABiLMI6ocuVV68mrS3V1FqlTVa7_8eW2Ex0jiaiQBmU4Jlf'
            'n8dZiNl6cTvHHKduZw0Q3eA4Tp0WWDMykp1LLroXNBs65fd_exhbJ'
            '3YMdDNhLAacVPLcnohDuWGoDkh0If9e0PyX',
        ]

    @patch(
        'driver_event_detector.models.offers.config.OfferPickerConfig.'
        'get_latest_config',
    )
    # pylint: disable=W0612
    async def get_latest_config(*args, **kwargs) -> Dict[str, Any]:
        with open_file('yt_config.json') as json_file:
            return json.load(json_file)

    @patch(
        'driver_event_detector.models.offers.config.OfferPickerConfig.'
        'fetch_geo_zones_from_source',
    )
    # pylint: disable=W0612
    async def fetch_geo_zones_from_source(
            *args, **kwargs,
    ) -> List[Dict[str, Any]]:
        with open_file('yt_geo_zones.json') as json_file:
            return json.load(json_file)

    @patch('client_chyt.components.AsyncChytClient.execute')
    # pylint: disable=W0612
    async def execute(*args, **kwargs) -> List[Dict[str, Any]]:
        with open_file('yt_offers.json') as json_file:
            return json.load(json_file)

    @patch('aiohttp.ClientSession.post')
    # pylint: disable=W0612
    async def post(url, **kwargs) -> Dict[str, Any]:
        if 'romashka' in url:
            file_name = 'romashka_response.json'
        else:
            file_name = 'gorky_response.json'

        with open_file(file_name) as json_file:
            return response_mock(json=json.load(json_file))

    @patch(
        'generated.clients.superapp_misc.SuperappMiscClient.'
        'x40_mlutp_v1_nearest_zone_post',
    )
    # pylint: disable=W0612
    async def x40_mlutp_v1_nearest_zone_post(**kwargs):
        return superapp_misc_client.X40MlutpV1NearestZonePost200(
            body=superapp_misc_models.NearestZoneResponse(
                services=[
                    superapp_misc_models.SuccessfulResult(
                        payload=superapp_misc_models.FoundPayload(
                            nearest_zone='chelyabinsk',
                        ),
                        status='found',
                        service='taxi',
                    ),
                ],
            ),
        )

    @patch(
        'generated.clients.taxi_tariffs_py3.TaxiTariffsPy3Client.'
        'get_current_tariff_raw',
    )
    # pylint: disable=W0612
    async def get_current_tariff_raw(**kwargs):
        return taxi_tariffs_py3_client.GetCurrentTariffRaw200(
            body={
                'categories': [
                    {
                        'category_name': 'econom',
                        'category_type': 'application',
                    },
                    {
                        'category_name': 'business',
                        'category_type': 'application',
                    },
                    {'category_name': 'vip', 'category_type': 'application'},
                    {'category_name': 'uberx', 'category_type': 'application'},
                    {
                        'category_name': 'uberselect',
                        'category_type': 'application',
                    },
                    {
                        'category_name': 'uberblack',
                        'category_type': 'application',
                    },
                ],
            },
        )

    @patch(
        'generated.clients.pricing_data_preparer.PricingDataPreparerClient.'
        'v2_prepare_post',
    )
    # pylint: disable=W0612
    async def v2_prepare_post(
            body: pricing_data_preparer_models.PrepareRequest, **kwargs,
    ):
        if 'uberselect' in body.categories:
            file_name = 'ya_uber_response.json'
        else:
            file_name = 'yandex_taxi_response.json'

        with open_file(file_name) as json_file:
            return pricing_data_preparer_client.V2PreparePost200(
                pricing_data_preparer_models.PreparedCategories.deserialize(
                    json.load(json_file),
                ),
            )

    @patch('random.sample')
    # pylint: disable=W0612
    def sample(*args, **kwargs):
        with open_file('yt_offers.json') as json_file:
            raw_offers = json.load(json_file)
            raw_offer = yson.yson_to_json(
                yson.loads(raw_offers[0]['doc'].encode('utf8')),
            )
            return [models.Offer.from_json(raw_offer)]

    caplog.set_level(logging.INFO, logger='taxi.opentracing.reporter')

    await run_cron.main(
        ['driver_event_detector.crontasks.predict_offer_prices', '-t', '0'],
    )

    records = [
        json.loads(x.message)
        for x in caplog.records
        if 'timestamp' in getattr(x, 'message', '{}')
    ]

    assert len(records) == 2
    with open_file('expected_result.json') as expected_result_json_file:
        expected_result = json.load(expected_result_json_file)
        for record in records:
            assert record in expected_result

    stats = get_stats_by_list_label_values(
        cron_context,
        [
            {'sensor': 'offer_picker_config_refresh_time'},
            {'sensor': 'offers_load_time'},
            {'sensor': 'offers_geo_zones_rate'},
            {'sensor': 'raw_offers_loaded'},
            {'sensor': 'offers_to_process'},
            {'sensor': 'interrupted'},
            {'sensor': 'time_elapsed_total'},
            {'sensor': 'yt_rows'},
            {'sensor': 'success_rate_Gorky'},
            {'sensor': 'success_rate_Romashka'},
            {'sensor': 'success_rate_YandexTaxi'},
            {'sensor': 'success_rate_YaUber'},
        ],
    )
    assert len(stats) == 12
