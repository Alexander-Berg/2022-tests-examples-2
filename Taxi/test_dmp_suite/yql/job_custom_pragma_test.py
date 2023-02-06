import mock

from taxidwh_settings import DictSettingsSource, StringToTupleSourceProxy

from connection.yql import (
    add_job_cpu_monitor_to_yql_query,
    add_use_default_tentative_trees_pragma,
)

def mock_settings(test_data):
    return mock.patch(
        'connection.yql.settings',
        new=StringToTupleSourceProxy(
            DictSettingsSource(test_data)
        )
    )


def test_job_cpu_monitor_pragma_added_correctly():
    initial_query = 'select 1;'
    expected_query = (
        "pragma yt.OperationSpec = '{"
            "job_cpu_monitor={"
                "min_cpu_limit=0.1;"
                "enable_cpu_reclaim=true;"
                "relative_upper_bound=0.9;"
                "relative_lower_bound=0.7;"
                "increase_coefficient=1.2;"
                "decrease_coefficient=0.6;"
            "};"
        "}';"
        "\n"
        "\n"
        "select 1;"
    )
    assert expected_query == add_job_cpu_monitor_to_yql_query(initial_query)


@mock_settings({'yt': {'use_default_tentative_pool_trees': True}})
def test_tentative_trees_pragma_set():
    initial_query = 'select 1;'
    expected_query = (
        "pragma yt.PoolTrees = 'physical';"
        "\n"
        "pragma yt.UseDefaultTentativePoolTrees = 'true';"
        "\n"
        "select 1;"
    )
    assert expected_query == add_use_default_tentative_trees_pragma(initial_query)


@mock_settings({'yt': {'use_default_tentative_pool_trees': False}})
def test_tentative_trees_pragma_notset():
    initial_query = 'select 1;'
    assert initial_query == add_use_default_tentative_trees_pragma(initial_query)
