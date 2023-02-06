from taxi_driver_metrics.common.models import DriverInfo
from taxi_driver_metrics.common.utils import tags_manager


TST_TAG = 'special_driver'
TST_TAG_WITHOUT_PREFIX = 'special_driver'
TST_TAGS = ['good_driver', 'lucky']
TST_UDID = '5b05621ee6c22ea2654849c0'


def test_udid_experiments(web_context):
    tags_manager_ = tags_manager.TagsManager(
        web_context.config,
        web_context.tags_client,
        web_context.driver_tags_client,
    )
    local_config = web_context.config
    driver = DriverInfo(TST_UDID)
    setattr(
        local_config,
        'DRIVER_METRICS_TAG_FOR_EXPERIMENT',
        {
            TST_TAG: {
                'salt': '1122334455667788',
                'from': 'wrong_value',
                'to': 100,
            },
        },
    )

    tags = tags_manager_.fetch_experiment_tags(driver.udid)
    assert not tags

    setattr(
        local_config,
        'DRIVER_METRICS_TAG_FOR_EXPERIMENT',
        {TST_TAG: {'from': 0, 'to': 100}},
    )

    tags = tags_manager_.fetch_experiment_tags(driver.udid)

    assert not tags

    setattr(
        local_config,
        'DRIVER_METRICS_TAG_FOR_EXPERIMENT',
        {TST_TAG: {'salt': '1122334455667788', 'from': 0, 'to': 0}},
    )

    tags = tags_manager_.fetch_experiment_tags(driver.udid)

    assert not tags

    setattr(
        local_config,
        'DRIVER_METRICS_TAG_FOR_EXPERIMENT',
        {TST_TAG: {'salt': '1122334455667788', 'from': 0, 'to': 100}},
    )

    tags = tags_manager_.fetch_experiment_tags(driver.udid)

    assert TST_TAG_WITHOUT_PREFIX in tags


async def test_tag_fetcher_service(web_context, tags_service_mock):
    tags_service_mock()
    tags_manager_ = tags_manager.TagsManager(
        web_context.config,
        web_context.tags_client,
        web_context.driver_tags_client,
    )
    local_config = web_context.config
    udid = TST_UDID

    setattr(local_config, 'DRIVER_METRICS_ENABLE_TAG_FETCHER', False)
    tags = await tags_manager_.fetch_service_tags(udid, 'dbid', 'uuid')
    assert not tags

    setattr(local_config, 'DRIVER_METRICS_ENABLE_TAG_FETCHER', True)
    tags = await tags_manager_.fetch_service_tags(udid, 'dbid', 'uuid')
    # tags from tags_service_mock
    assert tags == set(TST_TAGS)
