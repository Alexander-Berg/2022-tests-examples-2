import pytest

from clowny_search.generated.cron import run_cron
from clowny_search.models import abc_members as a_m


async def _get_members_from_db(context, conn):
    query, args = context.sqlt.list_members()
    return await conn.fetch(query, *args)


@pytest.fixture(name='abc_members_value')
def _abc_members_value(mockserver, relative_load_json):
    def _wrapper(request, fired_employee=None):
        assert request.method in ['GET']
        if request.method == 'GET':
            return relative_load_json(
                'test_collect_abc_members/get_members_2_services.json',
            )
        return {}

    return _wrapper


@pytest.mark.config(CLOWNDUCTOR_ABC_API_V4_USAGE={'get_members': True})
@pytest.mark.pgsql('clowny_search', files=['add_test_data.sql'])
@pytest.mark.parametrize(
    'expected',
    [
        pytest.param(
            [
                a_m.AbcMembers(
                    login='eatroshkin', abc_slug='taxiinfraclownyperforator',
                ),
                a_m.AbcMembers(
                    login='elrusso', abc_slug='taxidevopsclownysearch',
                ),
                a_m.AbcMembers(
                    login='elrusso', abc_slug='taxiinfraclownyperforator',
                ),
                a_m.AbcMembers(
                    login='karachevda', abc_slug='taxidevopsclownysearch',
                ),
                a_m.AbcMembers(login='elrusso', abc_slug='taxidevservice404'),
                a_m.AbcMembers(login='deoevgen', abc_slug='taxideoevgen_no'),
                a_m.AbcMembers(
                    login='eatroshkin', abc_slug='taxiinfraclownyperforator',
                ),
                a_m.AbcMembers(login='isharov', abc_slug='test_slug'),
                a_m.AbcMembers(
                    login='karachevda', abc_slug='taxidevopsclownysearch',
                ),
            ],
            marks=pytest.mark.config(
                CLOWNY_SEARCH_COLLECT_ABC_CRON_SETTINGS={
                    'dry-run': False,
                    'max_retries_abc_get_members': 3,
                    'max_delete_element_count': 2,
                    'max_insert_element_count': 2,
                    'chunk_sleep_duration': 1,
                    'retries_abc_get_members_duration': 1,
                    'service_chunk_size': 1,
                },
            ),
        ),
        pytest.param(
            [
                a_m.AbcMembers(
                    login='elrusso', abc_slug='taxiinfraclownyperforator',
                ),
                a_m.AbcMembers(
                    login='elrusso', abc_slug='taxidevopsclownysearch',
                ),
                a_m.AbcMembers(login='elrusso', abc_slug='taxidevservice404'),
                a_m.AbcMembers(login='deoevgen', abc_slug='taxideoevgen_no'),
                a_m.AbcMembers(
                    login='eatroshkin', abc_slug='taxiinfraclownyperforator',
                ),
                a_m.AbcMembers(login='deoevgen', abc_slug='taxideoevgen_no'),
                a_m.AbcMembers(login='isharov', abc_slug='test_slug'),
            ],
            marks=pytest.mark.config(
                CLOWNY_SEARCH_COLLECT_ABC_CRON_SETTINGS={
                    'dry-run': True,
                    'max_retries_abc_get_members': 3,
                    'max_delete_element_count': 2,
                    'max_insert_element_count': 2,
                    'chunk_sleep_duration': 1,
                    'retries_abc_get_members_duration': 1,
                    'service_chunk_size': 1,
                },
            ),
        ),
    ],
)
async def test_cron_collect_abc_members(
        mock_stats, mock_clown, web_context, abc_members, expected,
):
    await run_cron.main(
        ['clowny_search.crontasks.collect_abc_members', '-t', '0'],
    )
    async with web_context.pg.primary.acquire() as conn:
        members = await _get_members_from_db(web_context, conn)
        result = [
            a_m.AbcMembers(login=member['login'], abc_slug=member['abc_slug'])
            for member in members
        ]
        assert set(result) == set(expected)
