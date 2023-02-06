from collections import OrderedDict

import pytest


def test_get_tables_and_views_to_create_order(restorer):
    restorer.donors_ch.tables_info = {
        'db1': OrderedDict(
            table1={
                'create_table_query': '',
                'engine': 'Table'
            },
            view1={
                'create_table_query': '',
                'engine': 'View'
            },
            mat_view1={
                'create_table_query': '',
                'engine': 'MaterializedView'
            },
            view2={
                'create_table_query': '',
                'engine': 'View'
            }
        ),
        'db2': OrderedDict(
            table1={
                'create_table_query': '',
                'engine': 'Table'
            },
            table2={
                'create_table_query': '',
                'engine': 'Table'
            }
        )
    }

    assert restorer._get_tables_and_views_to_create()[:-1] == (
        {
            'db1': [('table1', '')],
            'db2': [('table1', ''), ('table2', '')]
        },
        {
            'db1': [('mat_view1', ''), ('view1', ''), ('view2', '')]
        }
    )


@pytest.mark.parametrize('view_exists, result', [
    (False, {}),
    (True, {'db1': [('.inner.kek', '')]})
])
def test_get_tables_and_views_to_create_inner(restorer, view_exists, result):
    if view_exists:
        restorer.donors_ch.inner_table_views.add('db1.`.inner.kek`')
    restorer.donors_ch.tables_info = {
        'db1': {
            '.inner.kek': {
                'create_table_query': '',
                'engine': 'Table'
            }
        }
    }

    assert restorer._get_tables_and_views_to_create()[:-1] == (result, {})
