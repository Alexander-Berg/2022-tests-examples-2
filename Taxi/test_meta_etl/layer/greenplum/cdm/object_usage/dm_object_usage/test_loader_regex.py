import re
import pytest



@pytest.fixture(scope='module', autouse=True)
def import_implementation(unit_test_settings):
    # The imports are performed inside a fixture, because the settings are disabled
    # during test collection, and the loader module requires the settings during its importing.
    global REGEX_YT_PART_REPLACE_CPL

    with unit_test_settings():
        from meta_etl.layer.greenplum.cdm.object_usage.dm_object_usage.loader import (
            REGEX_YT_PART_REPLACE
        )

    REGEX_YT_PART_REPLACE_CPL = re.compile(REGEX_YT_PART_REPLACE)


@pytest.mark.parametrize(
    "table,table_dmp", [
        ('//home/taxi/production/tracks/raw_entries/2019-11-24', '//home/taxi/production/tracks/raw_entries'),
        ('//home/taxi/production/tracks/raw_entries', '//home/taxi/production/tracks/raw_entries'),
        ('//home/taxi/production/tracks/raw_entries/3019', '//home/taxi/production/tracks/raw_entries'),
        ('//home/taxi-analytics/overdraft/test2/aggregation', '//home/taxi-analytics/overdraft/test2/aggregation'),
        ('//home/taxi/production/tracks/raw_entries/2019', '//home/taxi/production/tracks/raw_entries'),
        ('//home/taxi/production/tracks/raw_entries/2019-01', '//home/taxi/production/tracks/raw_entries'),
        ('//home/taxi-backup/hahn/2019-11-22/order_proc', '//home/taxi-backup/hahn/2019-11-22/order_proc'),
        ('//home/taxi/metrics/eta/hourly/2019-11-28T13:00:00', '//home/taxi/metrics/eta/hourly'),
        ('//home/taxi-analytics/2019-03-25_test_tag_upgrade', '//home/taxi-analytics'),
        ('//home/taxi-analytics/2019-03-25_test/node', '//home/taxi-analytics/2019-03-25_test/node'),
    ]
)
def test_regex_yt_part_replace(table, table_dmp):
    result = REGEX_YT_PART_REPLACE_CPL.sub('', table)
    assert table_dmp == result
