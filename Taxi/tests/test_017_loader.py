import os.path

import jinja2

from easytap import Tap

SQL_DIR = os.path.join(os.path.dirname(__file__), 'sql')


def test_base():
    tap = Tap()

    tap.plan(7)
    tap.import_ok('dbtpl', 'импорт dbtpl')

    import dbtpl

    loader_dict = {
        'test.sql': """
            SELECT
                *
            FROM
                "{{ table |i }}"
            WHERE
                "id" = {{ id }}
        """
    }

    agent = dbtpl.agent(loader=jinja2.DictLoader(loader_dict))
    tap.ok(agent, 'agent created')

    sql, binds = agent('test.sql', {'id': 123, 'table': 'users'})
    tap.isa_ok(sql, str, 'sql created')
    tap.isa_ok(binds, list, 'binds created')
    tap.eq(binds, [123], 'bindvars')
    tap.like(sql, r'"users"', 'immediate insert')
    tap.like(sql, r'"id" = \$1', 'quote insert')

    assert tap.done_testing()
