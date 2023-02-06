# pylint: disable=redefined-outer-name

from clowny_balancer.generated.cron import run_cron

EXPECTED_RESULTS = [{'protocol': 'https'}, {'protocol': 'http'}]


async def test_sync_with_awacs(
        patch,
        awacs_mockserver,
        mockserver,
        cron_context,
        relative_load_plaintext,
        load_json,
):
    awacs_mockserver()

    @mockserver.json_handler('/client-awacs/api/ListDomains/')
    def _list_domains(_):
        return load_json('list_domains.json')

    @mockserver.json_handler('/client-awacs/api/ListUpstreams/')
    def _list_upstreams(_):
        return load_json('list_upstreams.json')

    @mockserver.json_handler('/client-awacs/api/ListBackends/')
    def _list_backends(_):
        return load_json('list_backends.json')

    await run_cron.main(
        ['clowny_balancer.crontasks.sync_with_awacs', '-t', '0'],
    )

    eps = await cron_context.pg.primary.fetch(
        'SELECT protocol FROM balancers.entry_points ep ORDER BY id;',
    )
    for i, j in zip(eps, EXPECTED_RESULTS):
        assert i['protocol'] == j['protocol'], (i, j)

    removed_ep = await cron_context.pg.primary.fetch(
        'SELECT * FROM balancers.entry_points ep WHERE ep.id = 3;',
    )
    assert removed_ep[0]['is_deleted'] is not None
