import pytest

import atlas.domain.anomaly as atlas_anomaly


@pytest.fixture
def test_anomaly():
    return atlas_anomaly.Anomaly(
        _id='test_anomaly',
        created=1581341391,
        updated=1581341411,
        status='created',
        start_ts=1580907600,
        end_ts=1580907840,
        author='test_user',
        description='test anomaly',
        duty_task='<link to tracker issue>',
        losses={
            'orders': 300
        },
        notifications=None,
        level='minor',
        source='all'
    )


def test_from_to_dict_transformation(test_anomaly):
    dct = test_anomaly.to_dict()
    anomaly = atlas_anomaly.Anomaly.from_dict(dct)

    for attr_name in ['_id', 'created', 'updated', 'start_ts', 'end_ts',
                      'author', 'description', 'duty_task', 'losses',
                      'notifications', 'severity_level', 'order_source']:
        assert getattr(test_anomaly, attr_name) == getattr(anomaly, attr_name)


def test_to_dict(test_anomaly):
    expected = dict(
        _id='test_anomaly',
        created=1581341391,
        updated=1581341411,
        status='created',
        start_ts=1580907600,
        end_ts=1580907840,
        author='test_user',
        description='test anomaly',
        duty_task='<link to tracker issue>',
        losses={
            'orders': 300
        },
        notifications={},
        level='minor',
        source='all'
    )
    actual = test_anomaly.to_dict()

    assert actual == expected
