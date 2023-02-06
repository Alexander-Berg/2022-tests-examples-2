import decimal

import pytest

# pylint: disable=invalid-name
pytestmark = [pytest.mark.config(PASSENGER_PROFILE_RATINGS_SYNC_ENABLED=True)]


@pytest.mark.parametrize(
    'config_override',
    [
        pytest.param(
            {'PASSENGER_PROFILE_RATINGS_SYNC_ENABLED': False},
            id='disabled-by-config',
        ),
        pytest.param(
            {},
            marks=pytest.mark.pgsql(
                'passenger_profile',
                files=['pg_passenger_profile_last_sync_finished.sql'],
            ),
            id='last-sync-finished',
        ),
        pytest.param(
            {},
            marks=pytest.mark.pgsql(
                'passenger_profile',
                files=['pg_passenger_profile_no_syncs.sql'],
            ),
            id='no-syncs',
        ),
    ],
)
async def test_sync_worker_nothing_to_do(
        cron_runner, taxi_config, config_override, run_sql,
):
    if config_override:
        taxi_config.set_values(config_override)

    await cron_runner.ratings_sync_worker()

    profiles = run_sql('select * from passenger_profile.profile')
    assert not profiles


@pytest.mark.config(
    PASSENGER_PROFILE_RATINGS_READ_BATCH_SIZE=40,
    PASSENGER_PROFILE_WRITE_BATCH_SIZE=10,
    PASSENGER_PROFILE_WRITE_DELAY=0,
)
@pytest.mark.parametrize(
    [],
    [
        pytest.param(
            marks=pytest.mark.pgsql(
                'passenger_profile',
                files=['pg_passenger_profile_first_sync.sql'],
            ),
            id='first-sync',
        ),
        pytest.param(
            marks=pytest.mark.pgsql(
                'passenger_profile',
                files=['pg_passenger_profile_second_sync.sql'],
            ),
            id='filter-by-updated',
        ),
        pytest.param(
            marks=pytest.mark.pgsql(
                'passenger_profile',
                files=['pg_passenger_profile_restarted_sync.sql'],
            ),
            id='continue-sync',
        ),
    ],
)
@pytest.mark.yt(
    schemas=['yt_ratings_schema.yaml'], static_table_data=['yt_ratings.yaml'],
)
async def test_ratings_sync_worker(
        cron_runner, run_sql, yt_apply_force, load_json,
):

    await cron_runner.ratings_sync_worker()

    actual_profiles = run_sql(
        'select yandex_uid, brand, rating, first_name '
        'from passenger_profile.profile',
    )
    expected_profiles = load_json('expected_profiles.json')
    expected_profiles = [
        {**profile, 'rating': decimal.Decimal(str(profile['rating']))}
        for profile in expected_profiles
    ]

    assert actual_profiles == expected_profiles
