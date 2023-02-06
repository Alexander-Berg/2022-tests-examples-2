import json

import pytest

from eats_retail_retail_parser.generated.cron import run_cron

CRON_SETTINGS = [
    'eats_retail_retail_parser.crontasks.update_partners_slots',
    '-t',
    '0',
]


async def test_should_not_start_if_disabled(
        cron_context, cron_runner, mockserver,
):
    @mockserver.handler('/security/oauth/token')
    def get_test_get_token(request):
        return {}

    await run_cron.main(CRON_SETTINGS)

    assert not get_test_get_token.has_calls


@pytest.mark.config(
    EATS_RETAIL_RETAIL_PARSER_PARTNERS_SLOTS_SETTINGS={
        'cron_enabled': True,
        'place_group_ids': ['place_group_id_123'],
    },
)
@pytest.mark.pgsql('eats_retail_retail_parser', files=['add_slots_data.sql'])
async def test_should_insert_new_slots(
        cron_context, cron_runner, pgsql, mockserver, load_json,
):
    @mockserver.handler('/security/oauth/token')
    def get_test_get_token(request):
        return mockserver.make_response(
            json.dumps(load_json('test_token.json')), 200,
        )

    @mockserver.handler('/shops/nearest_delivery_times')
    def get_test_get_slotst(request):
        return mockserver.make_response(
            json.dumps(load_json('slots.json')), 200,
        )

    assert _get_count(pgsql) == 0

    await run_cron.main(CRON_SETTINGS)

    assert get_test_get_token.has_calls
    assert get_test_get_slotst.has_calls
    assert _get_count(pgsql) == 2


def _get_count(pgsql):
    with pgsql['eats_retail_retail_parser'].cursor() as cursor:
        cursor.execute(f'select count(*) from partner_slot')
        count = list(row[0] for row in cursor)[0]
    return count
