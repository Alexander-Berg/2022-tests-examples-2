import atlas.domain.metric as dmetric


def test_metric_repr():
    metric = dmetric.Metric(
        _id='test_metric',
        database='tst_db',
        table='tst_table'
    )

    assert repr(metric) == 'Metric(id="test_metric", database="tst_db", table="tst_table")'
