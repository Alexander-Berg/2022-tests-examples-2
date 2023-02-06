import datetime as dt
from typing import List
from typing import Union

import pytest

from . import constants
from . import models


PERIODIC_NAME = 'run-feeds-generation-periodic'
MOCK_NOW = '2021-02-18T20:00:00+00:00'
EXPIRATION_THRESHOLD_IN_HOURS = 336
BRAND_1_ID = '771'
BRAND_2_ID = '772'
BRAND_3_ID = '773'
BRAND_4_ID = '774'
STQ_DELAY_IN_SECONDS = 300


@pytest.mark.now(MOCK_NOW)
async def test_run_feeds_generation(
        assert_objects_lists,
        generate_feed_s3_path,
        get_brands_google_feeds_from_db,
        get_brands_market_feeds_from_db,
        get_expected_feeds_list,
        mds_s3_storage,
        save_brands_to_db,
        save_brands_feeds_to_db,
        stq,
        taxi_eats_retail_seo,
        testpoint,
        to_utc_datetime,
        update_taxi_config,
):
    @testpoint(PERIODIC_NAME + '-finished')
    def periodic_finished(param):
        pass

    _set_configs(update_taxi_config)

    brands = _generate_brands()
    save_brands_to_db(list(brands.values()))

    now = to_utc_datetime(MOCK_NOW)
    recently_generated_at = now - dt.timedelta(
        hours=EXPIRATION_THRESHOLD_IN_HOURS / 2,
    )
    old_generated_at = now - dt.timedelta(
        hours=EXPIRATION_THRESHOLD_IN_HOURS * 2,
    )

    brand_1 = brands[BRAND_1_ID]
    brand_3 = brands[BRAND_3_ID]
    brand_4_with_old_feed = brands[BRAND_4_ID]

    brand_google_feed_1 = models.BrandGoogleFeed(
        brand=brand_1,
        s3_path=generate_feed_s3_path(
            constants.S3_DIRS[constants.GOOGLE_FEED_TYPE], brand_1,
        ),
        last_generated_at=recently_generated_at,
    )
    brand_google_feed_2 = models.BrandGoogleFeed(
        brand=brand_3,
        s3_path=generate_feed_s3_path(
            constants.S3_DIRS[constants.GOOGLE_FEED_TYPE], brand_3,
        ),
        last_generated_at=recently_generated_at,
    )
    brand_google_feed_3_old = models.BrandGoogleFeed(
        brand=brand_4_with_old_feed,
        s3_path=generate_feed_s3_path(
            constants.S3_DIRS[constants.GOOGLE_FEED_TYPE],
            brand_4_with_old_feed,
        ),
        last_generated_at=old_generated_at,
    )
    save_brands_feeds_to_db(
        [brand_google_feed_1, brand_google_feed_2, brand_google_feed_3_old],
    )

    brand_market_feed_1 = models.BrandMarketFeed(
        brand=brand_1,
        s3_path=generate_feed_s3_path(
            constants.S3_DIRS[constants.MARKET_FEED_TYPE], brand_1,
        ),
        last_generated_at=recently_generated_at,
    )
    brand_market_feed_2 = models.BrandMarketFeed(
        brand=brand_3,
        s3_path=generate_feed_s3_path(
            constants.S3_DIRS[constants.MARKET_FEED_TYPE], brand_3,
        ),
        last_generated_at=recently_generated_at,
    )
    brand_market_feed_3_old = models.BrandMarketFeed(
        brand=brand_4_with_old_feed,
        s3_path=generate_feed_s3_path(
            constants.S3_DIRS[constants.MARKET_FEED_TYPE],
            brand_4_with_old_feed,
        ),
        last_generated_at=old_generated_at,
    )
    save_brands_feeds_to_db(
        [brand_market_feed_1, brand_market_feed_2, brand_market_feed_3_old],
    )

    await taxi_eats_retail_seo.run_distlock_task(PERIODIC_NAME)

    expected_called_brands = [brand_1, brand_3]

    feed_types = [constants.GOOGLE_FEED_TYPE, constants.MARKET_FEED_TYPE]
    for feed_type in feed_types:
        if feed_type == constants.GOOGLE_FEED_TYPE:
            not_expired_brands_feeds = [
                brand_google_feed_1,
                brand_google_feed_2,
            ]
        else:
            not_expired_brands_feeds = [
                brand_market_feed_1,
                brand_market_feed_2,
            ]

        stq_queue_name = constants.STQ_QUEUES[feed_type]
        times_called = stq[stq_queue_name].times_called
        assert times_called == len(expected_called_brands)
        called_brands = set()
        for _ in range(times_called):
            task_info = stq[stq_queue_name].next_call()
            called_brands.add(task_info['kwargs']['brand_id'])
        assert (
            set(brand.brand_id for brand in expected_called_brands)
            == called_brands
        )

        s3_dir = constants.S3_DIRS[feed_type]
        result_feeds_list = mds_s3_storage.storage[
            f'{s3_dir}/feeds_list.txt'
        ].data.decode('utf-8')
        assert result_feeds_list == get_expected_feeds_list(
            s3_dir, not_expired_brands_feeds,
        )

        if feed_type == constants.MARKET_FEED_TYPE:
            assert_objects_lists(
                get_brands_market_feeds_from_db(), not_expired_brands_feeds,
            )
        else:
            assert_objects_lists(
                get_brands_google_feeds_from_db(), not_expired_brands_feeds,
            )

    assert periodic_finished.times_called == 1


@pytest.mark.now(MOCK_NOW)
@pytest.mark.parametrize('stq_delay_in_seconds', [300, 600])
@pytest.mark.parametrize(
    'should_add_stq_delay_after_previous_queue', [True, False],
)
async def test_stq_delay(
        save_brands_to_db,
        stq,
        taxi_eats_retail_seo,
        testpoint,
        to_utc_datetime,
        update_taxi_config,
        # parametrize params
        stq_delay_in_seconds,
        should_add_stq_delay_after_previous_queue,
):
    @testpoint(PERIODIC_NAME + '-finished')
    def periodic_finished(param):
        pass

    _set_configs(
        update_taxi_config,
        stq_delay_in_seconds,
        should_add_stq_delay_after_previous_queue,
    )

    brands = _generate_brands()
    save_brands_to_db(list(brands.values()))

    brand_1 = brands[BRAND_1_ID]
    brand_3 = brands[BRAND_3_ID]

    await taxi_eats_retail_seo.run_distlock_task(PERIODIC_NAME)

    expected_called_brands = [brand_1, brand_3]

    now = to_utc_datetime(MOCK_NOW).replace(tzinfo=None)
    current_stq_delay = 0
    feed_types = [constants.MARKET_FEED_TYPE, constants.GOOGLE_FEED_TYPE]
    for feed_type in feed_types:
        if not should_add_stq_delay_after_previous_queue:
            current_stq_delay = 0
        stq_queue_name = constants.STQ_QUEUES[feed_type]
        times_called = stq[stq_queue_name].times_called
        assert times_called == len(expected_called_brands)
        for _ in range(times_called):
            task_info = stq[stq_queue_name].next_call()
            assert (
                task_info['eta'] - now
            ).total_seconds() == current_stq_delay
            current_stq_delay += stq_delay_in_seconds

    assert periodic_finished.times_called == 1


async def test_periodic_metrics(
        save_brands_to_db, update_taxi_config, verify_periodic_metrics,
):
    _set_configs(update_taxi_config)

    brands = _generate_brands()
    save_brands_to_db(list(brands.values()))

    await verify_periodic_metrics(PERIODIC_NAME, is_distlock=True)


def _set_configs(
        update_taxi_config,
        stq_delay_in_seconds=STQ_DELAY_IN_SECONDS,
        should_add_stq_delay_after_previous_queue=True,
):
    update_taxi_config(
        'EATS_RETAIL_SEO_PERIODICS',
        {PERIODIC_NAME: {'is_enabled': True, 'period_in_sec': 86400}},
    )
    update_taxi_config(
        'EATS_NOMENCLATURE_MASTER_TREE',
        {
            'master_tree_settings': {
                BRAND_1_ID: {'assortment_name': 'default_assortment'},
                BRAND_3_ID: {'assortment_name': 'master_tree'},
            },
        },
    )
    update_taxi_config(
        'EATS_RETAIL_SEO_FEEDS_SETTINGS',
        {
            '__default__': {
                'allowed_countries': [],
                'feed_expiration_threshold_in_hours': (
                    EXPIRATION_THRESHOLD_IN_HOURS
                ),
                'stq_delay_in_seconds': stq_delay_in_seconds,
                'should_add_stq_delay_after_previous_queue': (
                    should_add_stq_delay_after_previous_queue
                ),
            },
        },
    )


def _generate_brands():
    brand_1 = models.Brand(brand_id=BRAND_1_ID, slug='magnit', name='Магнит')
    brand_2 = models.Brand(
        brand_id=BRAND_2_ID, slug='ashan_gipermarket', name='Ашан Гипермаркет',
    )
    brand_3 = models.Brand(
        brand_id=BRAND_3_ID, slug='vkusvill', name='ВкусВилл',
    )
    brand_4 = models.Brand(
        brand_id=BRAND_4_ID, slug='azbuka_vkusa', name='Азбука Вкуса',
    )
    return {
        brand.brand_id: brand for brand in [brand_1, brand_2, brand_3, brand_4]
    }


@pytest.fixture(name='get_expected_feeds_list')
def _get_expected_feeds_list(generate_feed_s3_path):
    def do_get(
            s3_dir: str,
            brands_feeds: Union[
                List[models.BrandMarketFeed], List[models.BrandGoogleFeed],
            ],
    ):
        return '\n'.join(
            [
                generate_feed_s3_path(s3_dir, brand_feed.brand)
                for brand_feed in brands_feeds
            ],
        )

    return do_get
