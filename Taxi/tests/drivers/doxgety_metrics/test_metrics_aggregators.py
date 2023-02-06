from typing import Any, Dict

import six

from nile.api.v1 import Record
from nile.api.v1 import clusters
from nile.api.v1.local import StreamSource, ListSink

from projects.drivers.doxgety_metrics.nile_blocks import (
    get_metrics_aggregators,
)

from taxi_pyml.common.time_utils import DEFAULT_DATE_PARSER, SECONDS_IN_DAY
from taxi_pyml.common.time_utils import parse_timedelta

DATE = DEFAULT_DATE_PARSER('2021-06-01')
TIMESTAMP = int(DATE.timestamp())


def create_orders_record(days_back: int) -> Dict[str, Any]:
    return Record(
        agglomeration=b'br_moscow',
        unique_driver_id=b'gosling',
        log_source=b'orders',
        currency_rate=1,
        currency_code='RUB',
        order_cost=300,
        tariff_zone=b'moscow',
        timestamp=TIMESTAMP - days_back * SECONDS_IN_DAY,
        fraud_order_flg=False,
        utc_order_dt=six.ensure_binary(
            (DATE - parse_timedelta(f'{days_back}d')).strftime('%Y-%m-%d'),
        ),
    )


def create_deprecated_sessions_record(
        days_back: int, status: str = 'driving',
) -> Dict[str, Any]:
    return Record(
        unique_driver_id=b'gosling',
        log_source=b'deprecated_sessions',
        tariff_zone=b'moscow',
        duration_sec=420,
        distance_km=13.37,
        status=status,
        timestamp=TIMESTAMP - days_back * SECONDS_IN_DAY,
    )


INPUT = (
    [create_orders_record(i) for i in range(23)]
    + [create_deprecated_sessions_record(i) for i in range(23)]
    + [
        create_deprecated_sessions_record(i, status=b'verybusy')
        for i in range(23)
    ]
    + [
        create_deprecated_sessions_record(i, status=b'unavailable')
        for i in range(23)
    ]
)


def test_metrics_aggregators():
    aggregators = get_metrics_aggregators(DATE)
    job = clusters.MockCluster().job()
    job.table('input').label('input').groupby('unique_driver_id').aggregate(
        **aggregators,
    ).put('output').label('output')
    output = []
    job.local_run(
        sources={'input': StreamSource(INPUT)},
        sinks={'output': ListSink(output)},
    )

    assert len(output) == 1
    output = output[0].to_dict()
    assert output['unique_driver_id'] == b'gosling'
    assert output['agglomeration'] == [(b'br_moscow', 23)]
    assert output['agglomeration_mode'] == b'br_moscow'
    assert output['tariff_zone'] == [(b'moscow', 23)]
    assert output['tariff_zone_mode'] == b'moscow'
    assert output['currency_code_mode'] == 'RUB'
    assert output['currency_rate'] == [(1, 23)]
    assert output['currency_rate_mode'] == 1
    assert output['n_drivers'] == 1

    for i in list(range(1, 8)) + [14, 21]:
        assert output[f'order_cost_{i}'] == 300 * i

    for i in [7, 14, 21]:
        assert output[f'worked_days_{i}'] == i
        assert output[f'n_orders_{i}'] == i


if __name__ == '__main__':
    test_metrics_aggregators()
