from libstall.pg.rawfetch import raw_fetch


async def test_raw_fetch(tap):
    results = await raw_fetch('tlibstall', 'tests/select_variable.sqlt',
                              variable='hello')
    tap.eq_ok(len(results), 2, 'Two shard')
    tap.eq_ok(results[0][0].get('text'), 'hello', 'text on shard 0 is hello')
    tap.eq_ok(results[1][0].get('text'), 'hello', 'text on shard 1 is hello')
