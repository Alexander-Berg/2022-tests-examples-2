import pytest


@pytest.mark.config(
    EATS_PARTNERS_RESET_PASSWORD_SETTINGS={
        'cleaner_periodic': {
            'lifetime_token_seconds': 3600,
            'period_seconds': 3600,
        },
        'generate_link': {
            'link': 'http://link.com',
            'field_token': 'token',
            'field_email': 'email',
        },
    },
)
@pytest.mark.pgsql('eats_partners', files=['insert_partner_data.sql'])
@pytest.mark.parametrize(
    'count',
    [
        pytest.param(
            0,
            marks=[pytest.mark.now('2020-01-01T01:00:00Z')],
            id='empty_clean_token',
        ),
        pytest.param(
            1,
            marks=[pytest.mark.now('2020-10-01T01:00:00Z')],
            id='remove_one_token',
        ),
        pytest.param(
            2,
            marks=[pytest.mark.now('2021-01-01T01:00:00Z')],
            id='remove_two_tokens',
        ),
    ],
)
async def test_periodic_expired_tokens_cleaner_run(
        testpoint, count, taxi_eats_partners, pgsql,
):
    @testpoint('expired-tokens-cleaner::clean')
    def handle_finished(arg):
        pass

    await taxi_eats_partners.run_periodic_task(
        'eats-partners-expired-tokens-cleaner-periodic',
    )

    result = handle_finished.next_call()
    assert result == {'arg': count}
