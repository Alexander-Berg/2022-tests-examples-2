from dataclasses import dataclass

from station_finder import StationFinder
from time_window_aggregator import aggregate_over_window


@dataclass
class InputRow:
    features: dict[bytes, float]
    need_return: bool
    order_id: bytes
    dttm: bytes


INPUT_ROWS = [
    InputRow(order_id=b'1', dttm=b'2020-01-01 00:00:00', need_return=False, features={b'foo:max,avg:90': 1}),
    InputRow(order_id=b'2', dttm=b'2020-02-01 00:00:00', need_return=True, features={b'foo:max,avg:90': 2}),
    InputRow(order_id=b'3', dttm=b'2020-03-01 00:00:00', need_return=False, features={b'foo:max,avg:90': 3}),
    InputRow(order_id=b'4', dttm=b'2020-04-01 00:00:00', need_return=True, features={b'foo:max,avg:90': 4}),
]


EXPECTED_OUTPUT_ROWS = [
    dict(order_id=b'2', features={b'foo_avg_90_days': 1.0, b'foo_max_90_days': 1.0}),
    dict(order_id=b'4', features={b'foo_avg_90_days': 2.5, b'foo_max_90_days': 3.0}),
]


def test_time_window_aggregator():
    output_rows = list(aggregate_over_window(None, INPUT_ROWS))
    assert output_rows == EXPECTED_OUTPUT_ROWS


def test_station_finder():
    nearest_stations = StationFinder(
        # id    lon    lat
        b'10\t51.67\t64.19\n'
        b'20\t37.12\t65.57\n'
        b'30\t51.05\t69.24\n'
        b'40\t64.19\t51.05\n'
    )
    assert nearest_stations(64.2, 51.6, k=1) == [10]
    assert nearest_stations(64.2, 51.6, k=3) == [10, 30, 20]
    assert nearest_stations(51.6, 64.2, k=3) == [40, 10, 30]
