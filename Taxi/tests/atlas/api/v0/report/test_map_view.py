# coding: utf-8
import pytest

from atlas.api.v0.report import map_view
from atlas.domain import metric

@pytest.fixture
def metric_v2():
    return metric.Metric(
        _id='test_metric_v2',
        version=2,
        sql_query_raw=u'''
--DEFINE_ATLAS_BLOCK REPORT::MAP START
--REGISTER_PARAM DateRange ts
SELECT
    quadkey,
    SUM(requests_volume) as value
FROM
    some_database.some_table
WHERE
    {{ filter.ts('dttm_utc_1_min') }}
GROUP BY
    quadkey
--DEFINE_ATLAS_BLOCK REPORT::MAP END
'''
        # TODO other params
    )


@pytest.fixture
def local_metric_storage(mocker, metric_v2):
    from test_helpers import DictMetricsStorage
    mocker.patch('atlas.domain.metric.storage', DictMetricsStorage())
    metric.storage.create(metric_v2)


def test_build_metric_v2_internal_query(metric_v2):
    report_inputs = {
        'car_class': ['econom'],
        'metrics': ['test_metric_v2'],
        'city': u'Аккра',
        'date_from': 1567555200,  # 2019-09-04 00:00:00
        'date_to': 1567558800,  # 2019-09-04 01:00:00
        'granularity': '2',
        'quadkeys': None,
        'utcoffset': 0
    }

    expected_result = u'''(
SELECT quadkey, value as value_0
FROM (--REGISTER_PARAM DateRange ts
SELECT
    quadkey,
    SUM(requests_volume) as value
FROM
    some_database.some_table
WHERE
    dttm_utc_1_min BETWEEN 1567555200 AND 1567558799
GROUP BY
    quadkey)
)'''

    report = map_view.MapReport(report_inputs)
    assert expected_result == report.build_metric_query(metric_v2, index=0)


@pytest.mark.skip('undone test')
def test_prepare_map_query_per_cluster(local_metric_storage):
    report_inputs = {
        'car_class': ['econom', 'comfort'],
        'metrics': ['test_metric_v2'],
        'city': u'Аккра',
        'date_from': 1567555200,  # 2019-09-04 00:00:00
        'date_to': 1567558800,  # 2019-09-04 01:00:00
        'granularity': '2',
        'quadkeys': None,
        'utcoffset': 0
    }

    expected_query = u'''
    dsfasdf
'''
    report = map_view.MapReport(report_inputs)
    assert [(expected_query, 'clickhouse_test_cluster')] == report.prepare_report_queries()
