import datetime

import pytest

TOKEN_TABLE_INFO = {
    'row_count': 7,
    'token_prefix': 'tok',
    'now': '2020-12-15T14:50:03+03:00',
    'dead_token_count_by_ttl': {
        datetime.timedelta(hours=1): 3,
        datetime.timedelta(minutes=2): 6,
    },
}

# Currently 'ConfigurablePeriodicTask' class is used instead of 'PeriodicTask'
# because of TAXICOMMON-3353.
# For this class to work properly 'cleanup-period-minutes' must be set to zero
# in all tests
DEFAULT_CONFIG = {
    'EATS_RESTAPP_MARKETING_TOKENS_CLEANUP': {
        'token-ttl-minutes': 60,
        'cleanup-period-minutes': 0,
    },
}


def get_token_rows(pgsql):
    cursor = pgsql['eats_tokens'].cursor()
    cursor.execute('SELECT * FROM eats_tokens.tokens')

    column_names = [it.name for it in cursor.description]
    return [dict(zip(column_names, row)) for row in sorted(cursor)]


def get_uncleaned_token_rows(pgsql):
    token_rows = get_token_rows(pgsql)

    # Ensure table is correct and was not cleaned:
    tokens = [row['token'] for row in token_rows]
    assert (
        len(token_rows) == TOKEN_TABLE_INFO['row_count']
    ), 'Token table has unexpected row count'
    assert '' not in tokens, 'Token table has already been cleaned up'
    assert len(set(tokens)) == len(tokens), 'Token table has repeating tokens'
    token_prefix = TOKEN_TABLE_INFO['token_prefix']
    for token in tokens:
        assert token.startswith(
            token_prefix,
        ), f'Unexpected token name: "{token}"'

    return token_rows


def get_expected_token_rows(mocked_time, pgsql, token_ttl):
    token_rows = get_uncleaned_token_rows(pgsql)
    expected_dead_token_count = TOKEN_TABLE_INFO['dead_token_count_by_ttl'][
        token_ttl
    ]

    # Clean up dead tokens
    now_with_tz = mocked_time.now().replace(tzinfo=datetime.timezone.utc)
    updation_time_threshold = now_with_tz - token_ttl

    dead_token_count = 0
    valid_tokens = []
    for token_row in token_rows:
        if token_row['updated_at'] < updation_time_threshold:
            dead_token_count += 1
        else:
            valid_tokens.append(token_row)
    assert dead_token_count == expected_dead_token_count

    return valid_tokens


@pytest.mark.now(TOKEN_TABLE_INFO['now'])
@pytest.mark.config(**DEFAULT_CONFIG)
@pytest.mark.suspend_periodic_tasks('periodic-tokens-cleanup')
@pytest.mark.pgsql('eats_tokens', files=['insert_tokens.sql'])
async def test_periodic_cleanup(
        taxi_eats_restapp_marketing, mocked_time, pgsql,
):
    expected_token_rows = get_expected_token_rows(
        mocked_time, pgsql, token_ttl=datetime.timedelta(hours=1),
    )

    await taxi_eats_restapp_marketing.run_periodic_task(
        'periodic-tokens-cleanup',
    )
    assert get_token_rows(pgsql) == expected_token_rows


@pytest.mark.now(TOKEN_TABLE_INFO['now'])
@pytest.mark.config(**DEFAULT_CONFIG)
@pytest.mark.suspend_periodic_tasks('periodic-tokens-cleanup')
@pytest.mark.pgsql('eats_tokens', files=['insert_tokens.sql'])
async def test_periodic_cleanup_repeated(
        taxi_eats_restapp_marketing, mocked_time, pgsql,
):
    expected_token_rows = get_expected_token_rows(
        mocked_time, pgsql, token_ttl=datetime.timedelta(hours=1),
    )

    # Ensure repeated invocation works fine
    for _ in range(10):
        await taxi_eats_restapp_marketing.run_periodic_task(
            'periodic-tokens-cleanup',
        )
        assert get_token_rows(pgsql) == expected_token_rows


@pytest.mark.now(TOKEN_TABLE_INFO['now'])
@pytest.mark.config(
    EATS_RESTAPP_MARKETING_TOKENS_CLEANUP={
        'token-ttl-minutes': 2,
        'cleanup-period-minutes': 0,
    },
)
@pytest.mark.suspend_periodic_tasks('periodic-tokens-cleanup')
@pytest.mark.pgsql('eats_tokens', files=['insert_tokens.sql'])
async def test_periodic_cleanup_small_ttl(
        taxi_eats_restapp_marketing, mocked_time, pgsql,
):
    expected_token_rows = get_expected_token_rows(
        mocked_time, pgsql, token_ttl=datetime.timedelta(minutes=2),
    )

    await taxi_eats_restapp_marketing.run_periodic_task(
        'periodic-tokens-cleanup',
    )
    assert get_token_rows(pgsql) == expected_token_rows


@pytest.mark.now(TOKEN_TABLE_INFO['now'])
@pytest.mark.config(**DEFAULT_CONFIG)
@pytest.mark.suspend_periodic_tasks('periodic-tokens-cleanup')
@pytest.mark.pgsql('eats_tokens', files=['insert_tokens.sql'])
async def test_periodic_cleanup_config_update(
        taxi_eats_restapp_marketing, mocked_time, taxi_config, pgsql,
):
    expected_token_rows_1_hour = get_expected_token_rows(
        mocked_time, pgsql, token_ttl=datetime.timedelta(hours=1),
    )
    expected_token_rows_2_minutes = get_expected_token_rows(
        mocked_time, pgsql, token_ttl=datetime.timedelta(minutes=2),
    )
    assert expected_token_rows_1_hour != expected_token_rows_2_minutes

    await taxi_eats_restapp_marketing.run_periodic_task(
        'periodic-tokens-cleanup',
    )
    assert get_token_rows(pgsql) == expected_token_rows_1_hour

    taxi_config.set_values(
        {
            'EATS_RESTAPP_MARKETING_TOKENS_CLEANUP': {
                'token-ttl-minutes': 2,
                'cleanup-period-minutes': 0,
            },
        },
    )
    await taxi_eats_restapp_marketing.invalidate_caches()

    await taxi_eats_restapp_marketing.run_periodic_task(
        'periodic-tokens-cleanup',
    )
    assert get_token_rows(pgsql) == expected_token_rows_2_minutes
