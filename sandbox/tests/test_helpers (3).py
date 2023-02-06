import pytest

from sandbox.projects.yabs.bases.YabsServerMakeBinBases.helpers import (
    base_requires_mysql,
    get_importer_queries,
    get_mysql_queries,
)


def test_get_importer_queries():
    print_info = {
        "i1": {
            "mkdb_queries": ["q1", "q2"],
        },
        "i2": {
            "mkdb_queries": ["q2", "q3"],
        },
        "i3": {}
    }
    assert set(get_importer_queries(print_info)) == {"q2", "q1", "q3"}


def test_get_mysql_queries():
    mkdb_info = {
        "Queries": [
            {
                "Name": "mysql_query",
                "Type": "MySql",
            },
            {
                "Name": "yt_query",
                "Type": "Yt",
            }
        ]
    }
    assert get_mysql_queries(mkdb_info) == ["mysql_query"]


@pytest.mark.parametrize(('base', 'requires_mysql'), [
    ('base_1', True),
    ('base_2', False),
])
def test_base_requires_mysql(base, requires_mysql):
    mkdb_info = {
        "base_1": {
            "Queries": [
                {
                    "Name": "base_1_mysql_query",
                    "Type": "MySql",
                },
                {
                    "Name": "base_1_yt_query",
                    "Type": "Yt",
                }
            ]
        },
        "base_2": {
            "Queries": [
                {
                    "Name": "base_2_mysql_query",
                    "Type": "MySql",
                },
                {
                    "Name": "base_2_yt_query",
                    "Type": "Yt",
                }
            ]
        }

    }
    importer_queries = ["base_2_mysql_query"]
    assert base_requires_mysql(mkdb_info[base], importer_queries) == requires_mysql
