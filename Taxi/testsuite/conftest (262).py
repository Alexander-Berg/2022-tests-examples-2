# pylint: disable=redefined-outer-name
import pytest

# root conftest for service eats-performer-statistics
pytest_plugins = ['eats_performer_statistics_plugins.pytest_plugins']


@pytest.fixture()
def get_cursor(pgsql):
    def do_get_cursor():
        return pgsql['eats_performer_statistics'].dict_cursor()

    return do_get_cursor


@pytest.fixture()
def get_statistics(get_cursor):
    def do_get_statistics(
            performer_id=None, metric_name=None, metric_interval=None,
    ):
        cursor = get_cursor()
        cursor.execute(
            """SELECT *
            FROM eats_performer_statistics.statistics
            WHERE (%(performer_id)s IS NULL OR performer_id = %(performer_id)s)
            AND (%(metric_name)s IS NULL OR metric_name = %(metric_name)s)
            AND (%(metric_interval)s IS NULL
                OR metric_interval = %(metric_interval)s)
            ORDER BY performer_id, metric_name, metric_interval""",
            {
                'performer_id': performer_id,
                'metric_name': metric_name,
                'metric_interval': metric_interval,
            },
        )
        return cursor.fetchall()

    return do_get_statistics
