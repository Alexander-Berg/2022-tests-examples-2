import pytest

from partner_offers.generated.cron import run_cron


@pytest.mark.now('2019-12-17T20:26:05+03:00')
@pytest.mark.pgsql('partner_offers', files=['basic_for_chains.sql'])
async def test_chain_merging(
        cron_context, patch, pgsql, mockserver, load_json,
):
    @mockserver.json_handler('/geocoder/yandsearch')
    def _geo_response(request):
        return load_json('chain_fix_response.json')

    @patch(
        'partner_offers.generated.cron.'
        'yt_wrapper.plugin.AsyncYTClient'
        '.read_table',
    )
    async def _yt_read(path, *args, **kwargs):
        return []

    await run_cron.main(
        ['partner_offers.crontasks.update_locations', '-t', '0'],
    )

    with pgsql['partner_offers'].cursor() as cursor:
        cursor.execute('SELECT id, geo_chain_id FROM partner ORDER BY id;')
        partners = list(cursor)
    with pgsql['partner_offers'].cursor() as cursor:
        cursor.execute(
            'SELECT business_oid, partner_id FROM location '
            'ORDER BY business_oid;',
        )
        locs = list(cursor)
    with pgsql['partner_offers'].cursor() as cursor:
        cursor.execute('SELECT id, partner_id FROM deal ORDER BY id;')
        deals = list(cursor)
    with pgsql['partner_offers'].cursor() as cursor:
        cursor.execute(
            'SELECT deal_id, location_id FROM active_deal_location'
            ' ORDER BY deal_id,location_id;',
        )
        active_pairs = list(cursor)
    assert partners == [(1, 1), (3, 2), (4, None)]
    assert locs == [(1, 1), (2, 1), (3, 3), (4, 4)]
    assert deals == [(1, 1), (2, 1)]
    assert active_pairs == [(1, 1), (2, 2)]


@pytest.mark.now('2019-12-17T20:26:05+03:00')
@pytest.mark.pgsql('partner_offers', files=['basic_for_locations_update.sql'])
async def test_content_fix(cron_context, patch, pgsql, mockserver, load_json):
    @mockserver.json_handler('/geocoder/yandsearch')
    def _geo_response(request):
        return load_json('location_update_response.json')

    @patch(
        'partner_offers.generated.cron.'
        'yt_wrapper.plugin.AsyncYTClient'
        '.read_table',
    )
    async def _yt_read(path, *args, **kwargs):
        results = [(1, 11), (1, 12), (2, 21)]
        return (
            {'chain_permalink': chain, 'company_permalink': company}
            for chain, company in results
        )

    await run_cron.main(
        ['partner_offers.crontasks.update_locations', '-t', '0'],
    )

    with pgsql['partner_offers'].cursor() as cursor:
        cursor.execute(
            'SELECT id, geo_chain_id, logo, name FROM partner ORDER BY id;',
        )
        partners = list(cursor)
    with pgsql['partner_offers'].cursor() as cursor:
        cursor.execute(
            'SELECT business_oid, partner_id, name, tz_offset FROM location '
            'ORDER BY business_oid;',
        )
        locs = list(cursor)
    assert partners == [
        (1, 1, 'https://example.com/image2.jpg', 'Big zombie shop'),
        (2, 2, 'https://tipsy.com/image2.jpg', 'Remonters'),
        (3, None, 'https://lemon.com/image2.jpg', 'Washers1'),
    ]
    assert locs == [
        (11, 1, 'Big zombie shop1', 14400),
        (12, 1, 'Big zombie shop2', 10800),
        (21, 2, 'Remonters1', 10800),
        (31, 3, 'Washers1', 10800),
    ]

    with pgsql['partner_offers'].cursor() as cursor:
        cursor.execute(
            'SELECT work_time_intervals FROM location '
            'ORDER BY business_oid;',
        )
        work_times = [x[0] for x in cursor]
    assert work_times == [
        [
            {'from': 1576555200, 'to': 1576609200},
            {'from': 1576641600, 'to': 1576695600},
            {'from': 1576728000, 'to': 1576782000},
            {'from': 1576814400, 'to': 1576868400},
            {'from': 1576900800, 'to': 1576954800},
            {'from': 1576987200, 'to': 1577041200},
            {'from': 1577073600, 'to': 1577127600},
        ],
        [
            {'from': 1576558800, 'to': 1576609200},
            {'from': 1576645200, 'to': 1576695600},
            {'from': 1576731600, 'to': 1576782000},
            {'from': 1576818000, 'to': 1576868400},
            {'from': 1576904400, 'to': 1576954800},
            {'from': 1576990800, 'to': 1577041200},
            {'from': 1577077200, 'to': 1577127600},
        ],
        [
            {'from': 1576558800, 'to': 1576614600},
            {'from': 1576645200, 'to': 1576701000},
            {'from': 1576731600, 'to': 1576787400},
            {'from': 1576818000, 'to': 1576873800},
            {'from': 1576904400, 'to': 1576960200},
            {'from': 1576990800, 'to': 1577046600},
            {'from': 1577077200, 'to': 1577133000},
        ],
        [
            {'from': 1576562400, 'to': 1576612800},
            {'from': 1576648800, 'to': 1576699200},
            {'from': 1576735200, 'to': 1576785600},
            {'from': 1576821600, 'to': 1576872000},
            {'from': 1576908000, 'to': 1576958400},
            {'from': 1576994400, 'to': 1577044800},
            {'from': 1577080800, 'to': 1577131200},
        ],
    ]
