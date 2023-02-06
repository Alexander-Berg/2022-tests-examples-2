# pylint: disable=redefined-outer-name
import pytest

from ml_cron.generated.short_life_pins_partitioning import run_cron


def check_if_table_exists(pgsql, table_name):
    cursor = pgsql['ml_pin_stats'].cursor()
    cursor.execute(
        f"""
        SELECT EXISTS (SELECT 1
        FROM information_schema.tables
        WHERE table_schema = 'pins'
        AND table_name = '{table_name}');""",
    )
    result = list(row[0] for row in cursor)
    return result == [True]


@pytest.mark.pgsql('ml_pin_stats', files=['renew_pins_schema.sql'])
@pytest.mark.now('2019-08-27T10:00:00')
async def test_no_partitions(pgsql):
    await run_cron.main(
        ['ml_cron.crontasks.short_life_pins_partitioning', '-t', '0'],
    )

    assert check_if_table_exists(pgsql, 'short_life_pins')
    assert check_if_table_exists(pgsql, 'short_life_pins_1566900000')
    assert check_if_table_exists(pgsql, 'short_life_pins_1566898200')
    assert check_if_table_exists(pgsql, 'short_life_pins_lag')


@pytest.mark.pgsql(
    'ml_pin_stats',
    files=[
        'renew_pins_schema.sql',
        'create_partition_1566900000.sql',
        'create_partition_1566898200.sql',
    ],
)
@pytest.mark.now('2019-08-27T10:00:00')
async def test_already_created(pgsql):
    await run_cron.main(
        ['ml_cron.crontasks.short_life_pins_partitioning', '-t', '0'],
    )

    assert check_if_table_exists(pgsql, 'short_life_pins')
    assert check_if_table_exists(pgsql, 'short_life_pins_1566900000')
    assert check_if_table_exists(pgsql, 'short_life_pins_1566898200')
    assert check_if_table_exists(pgsql, 'short_life_pins_lag')


@pytest.mark.pgsql(
    'ml_pin_stats',
    files=['renew_pins_schema.sql', 'create_partition_1566898200.sql'],
)
@pytest.mark.now('2019-08-27T10:00:00')
async def test_one_already_created(pgsql):
    await run_cron.main(
        ['ml_cron.crontasks.short_life_pins_partitioning', '-t', '0'],
    )

    assert check_if_table_exists(pgsql, 'short_life_pins')
    assert check_if_table_exists(pgsql, 'short_life_pins_1566900000')
    assert check_if_table_exists(pgsql, 'short_life_pins_1566898200')
    assert check_if_table_exists(pgsql, 'short_life_pins_lag')


@pytest.mark.pgsql('ml_pin_stats')
@pytest.mark.pgsql(
    'ml_pin_stats',
    files=[
        'renew_pins_schema.sql',
        'create_partition_1566898200.sql',
        'create_partition_1566894600.sql',
    ],
)
@pytest.mark.now('2019-08-27T10:30:00')
async def test_one_expired(pgsql):
    await run_cron.main(
        ['ml_cron.crontasks.short_life_pins_partitioning', '-t', '0'],
    )

    assert check_if_table_exists(pgsql, 'short_life_pins')
    assert check_if_table_exists(pgsql, 'short_life_pins_1566900000')
    assert check_if_table_exists(pgsql, 'short_life_pins_lag')
    assert not check_if_table_exists(pgsql, 'short_life_pins_1566898200')
