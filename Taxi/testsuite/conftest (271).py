# pylint: disable=redefined-outer-name
import pytest

# root conftest for service eats-picker-statistics
pytest_plugins = ['eats_picker_statistics_plugins.pytest_plugins']


@pytest.fixture()
def get_cursor(pgsql):
    def do_get_cursor():
        return pgsql['eats_picker_statistics'].dict_cursor()

    return do_get_cursor


@pytest.fixture()
def get_statistics(get_cursor):
    def do_get_statistics(
            picker_id=None, metric_name=None, metric_interval=None,
    ):
        cursor = get_cursor()
        cursor.execute(
            """SELECT *
            FROM eats_picker_statistics.statistics
            WHERE (%(picker_id)s IS NULL OR picker_id = %(picker_id)s)
            AND (%(metric_name)s IS NULL OR metric_name = %(metric_name)s)
            AND (%(metric_interval)s IS NULL
                OR metric_interval = %(metric_interval)s)
            ORDER BY picker_id, metric_name, metric_interval""",
            {
                'picker_id': picker_id,
                'metric_name': metric_name,
                'metric_interval': metric_interval,
            },
        )
        return cursor.fetchall()

    return do_get_statistics
