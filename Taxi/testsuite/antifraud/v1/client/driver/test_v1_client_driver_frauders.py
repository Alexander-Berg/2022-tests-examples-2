import pytest


def _test_base(taxi_antifraud, expected_drivers):
    response = taxi_antifraud.get('v1/client/driver/frauders')
    assert response.status_code == 200
    response_json = response.json()
    response_json['drivers'] = sorted(
        response_json['drivers'], key=lambda v: v['unique_driver_id'],
    )
    assert response_json == {'drivers': expected_drivers}


@pytest.mark.now('2019-01-10T10:00:00+0000')
def test_frauders_base(taxi_antifraud):
    _test_base(
        taxi_antifraud,
        [
            {
                'unique_driver_id': 'fraud_udi1',
                'frauder': True,
                'reason': 'bad_signature',
            },
        ],
    )


@pytest.mark.parametrize(
    'limit,expected',
    [
        (
            5,
            [
                {
                    'unique_driver_id': 'fraud_udi1',
                    'frauder': True,
                    'reason': 'bad_signature',
                },
                {
                    'unique_driver_id': 'fraud_udi2',
                    'frauder': True,
                    'reason': 'bad_signature',
                },
                {
                    'unique_driver_id': 'fraud_udi3',
                    'frauder': True,
                    'reason': 'bad_signature',
                },
                {
                    'unique_driver_id': 'fraud_udi4',
                    'frauder': True,
                    'reason': 'bad_signature',
                },
                {
                    'unique_driver_id': 'fraud_udi5',
                    'frauder': True,
                    'reason': 'bad_signature',
                },
            ],
        ),
        (4, []),
    ],
)
@pytest.mark.now('2019-01-10T10:00:00+0000')
def test_frauders_fallback(taxi_antifraud, config, limit, expected):
    config.set_values({'AFS_MAX_FRAUD_DRIVERS': limit})
    _test_base(taxi_antifraud, expected)
