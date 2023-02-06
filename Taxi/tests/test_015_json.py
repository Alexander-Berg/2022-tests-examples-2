import json
import os.path

from easytap import Tap

SQL_DIR = os.path.join(os.path.dirname(__file__), 'sql')


def test_base():
    tap = Tap(14, 'Json default tests')
    tap.import_ok('dbtpl', 'импорт dbtpl')

    import dbtpl    # noqa

    agent = dbtpl.agent(SQL_DIR)
    tap.ok(agent, 'agent created')

    j = {'a': 'b', 'c': 'd'}
    sql, binds = agent.inline('select {{ json| j }}', {'json': j})
    tap.isa_ok(sql, str, 'sql')
    tap.isa_ok(binds, list, 'binds')
    tap.eq_ok(sql, 'select $1', 'sql request')
    tap.eq_ok(binds, [json.dumps(j)], 'binds')

    sql, binds = agent.inline('select {{ json |j |i }}', {'json': j})
    tap.isa_ok(sql, str, 'sql')
    tap.isa_ok(binds, list, 'binds')
    tap.eq_ok(sql, 'select $1', 'sql request (|i - ignored)')
    tap.eq_ok(binds, [json.dumps(j)], 'binds')

    sql, binds = agent.inline('select {{ json |j |q }}', {'json': j})
    tap.isa_ok(sql, str, 'sql')
    tap.isa_ok(binds, list, 'binds')
    tap.eq_ok(sql, 'select $1', 'sql request (|i - ignored)')
    tap.eq_ok(binds, [json.dumps(j)], 'binds')
    assert tap.done_testing()


def test_json_redefine():
    tap = Tap(14, 'Json default tests')
    tap.import_ok('dbtpl', 'импорт dbtpl')

    import dbtpl    # noqa

    agent = dbtpl.agent(SQL_DIR, json_encoder=lambda x: '=' + json.dumps(x))
    tap.ok(agent, 'agent created')

    j = {'a': 'b', 'c': 'd'}
    sql, binds = agent.inline('select {{ json| j }}', {'json': j})
    tap.isa_ok(sql, str, 'sql')
    tap.isa_ok(binds, list, 'binds')
    tap.eq_ok(sql, 'select $1', 'sql request')
    tap.eq_ok(binds, ['=' + json.dumps(j)], 'binds')

    sql, binds = agent.inline('select {{ json |j |i }}', {'json': j})
    tap.isa_ok(sql, str, 'sql')
    tap.isa_ok(binds, list, 'binds')
    tap.eq_ok(sql, 'select $1', 'sql request (|i - ignored)')
    tap.eq_ok(binds, ['=' + json.dumps(j)], 'binds')

    sql, binds = agent.inline('select {{ json |j |q }}', {'json': j})
    tap.isa_ok(sql, str, 'sql')
    tap.isa_ok(binds, list, 'binds')
    tap.eq_ok(sql, 'select $1', 'sql request (|i - ignored)')
    tap.eq_ok(binds, ['=' + json.dumps(j)], 'binds')
    assert tap.done_testing()
