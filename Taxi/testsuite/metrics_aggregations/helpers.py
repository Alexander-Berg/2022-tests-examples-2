import copy
import dataclasses
import typing

import pytest


Labels = typing.Dict[str, str]


@dataclasses.dataclass(frozen=True)
class Metric:
    labels: Labels
    value: int


def _get_metrics(
        metrics_json: dict, current_label_name: str,
) -> typing.Iterable[Metric]:
    def _get_metrics_inner(
            metrics_json: dict, current_label_name: str, current_labels: dict,
    ):
        for key in metrics_json:
            value = metrics_json[key]
            labels = copy.copy(current_labels)

            labels[current_label_name] = key

            if isinstance(value, dict):
                children_label_name = value.pop('$meta', {}).get(
                    'solomon_children_labels',
                )

                assert children_label_name is not None, (
                    f'`solomon_children_labels` metadata'
                    f' not found for key `{key}`'
                )

                yield from _get_metrics_inner(
                    value, children_label_name, labels,
                )
            else:
                assert isinstance(value, int), (
                    f'invalid value type for key `{key}`` in metrics json:'
                    f' expected integer, found `{type(value)}`'
                )
                if isinstance(value, int) and not isinstance(value, bool):
                    yield Metric(labels=labels, value=value)

    return _get_metrics_inner(metrics_json, current_label_name, {})


def _is_sub_dict(left: typing.Optional[dict], right: dict) -> bool:
    if not left:
        return True

    for key in left:
        if key not in right:
            return False

        if left[key] != right[key]:
            return False

    return True


def _get_metrics_by_label_values(
        metrics_json: dict, labels: typing.Optional[dict],
) -> typing.List[Metric]:
    result = []
    # top-level attribute is a sensor name,
    # the way it works in solomon-sender scripts
    for metric in _get_metrics(metrics_json, current_label_name='sensor'):
        if not _is_sub_dict(labels, metric.labels):
            continue

        result.append(metric)
    return result


async def _get_sensor_json(monitor, sensor: str) -> dict:
    metrics_json = await monitor.get_metric(sensor)
    # adding artificial root so that metric parsing logic
    # can retrieve it too as 'sensor' label
    return {sensor: metrics_json}


# pylint: disable=invalid-name
@pytest.fixture
def get_metrics_by_label_values():
    async def _get(
            monitor, sensor: str, labels: Labels,
    ) -> typing.List[Metric]:
        sensor_json = await _get_sensor_json(monitor, sensor)
        return _get_metrics_by_label_values(sensor_json, labels)

    return _get


# pylint: disable=invalid-name
@pytest.fixture
def get_single_metric_by_label_values():
    async def _get(
            monitor, sensor: str, labels: Labels,
    ) -> typing.Optional[Metric]:
        sensor_json = await _get_sensor_json(monitor, sensor)
        metrics = _get_metrics_by_label_values(sensor_json, labels)
        assert (
            len(metrics) <= 1
        ), f'more than one metric found for labels {labels}: {metrics}'
        if not metrics:
            return None

        return metrics[0]

    return _get


def diff(
        old: typing.List[Metric], new: typing.List[Metric],
) -> typing.List[Metric]:
    def _make_key(labels: Labels) -> typing.Tuple[typing.Tuple[str, str], ...]:
        return tuple(sorted(labels.items()))

    old_map = {_make_key(metric.labels): metric for metric in old}

    result = []
    for new_metric in new:
        metric_key = _make_key(new_metric.labels)
        old_metric = old_map.get(metric_key)
        if old_metric is None:
            result.append(new_metric)
            continue

        value_diff = new_metric.value - old_metric.value
        if value_diff != 0:
            result.append(Metric(labels=new_metric.labels, value=value_diff))

    return result


class MetricsCollector:
    collected: bool

    def __init__(
            self, monitor, sensor: str, labels: typing.Optional[Labels] = None,
    ):
        self._monitor = monitor
        self._sensor = sensor
        self._labels = labels

        self._previous_metrics = None
        self.collected = False
        self._collected_metrics: typing.List[Metric] = []

    async def __aenter__(self):
        sensor_json = await _get_sensor_json(self._monitor, self._sensor)
        self._previous_metrics = _get_metrics_by_label_values(
            sensor_json, self._labels,
        )
        return self

    async def __aexit__(self, exc_type, exc, tb):
        assert self._previous_metrics is not None
        new_sensor_json = await _get_sensor_json(self._monitor, self._sensor)
        new_metrics = _get_metrics_by_label_values(
            new_sensor_json, self._labels,
        )

        self._collected_metrics = diff(self._previous_metrics, new_metrics)
        self.collected = True

    def get_single_collected_metric(self) -> typing.Optional[Metric]:
        assert self.collected, 'metrics have not been collected yet'
        assert len(self._collected_metrics) <= 1, (
            f'more than one metric collected'
            ' for labels {self._labels}: {self._collected_metrics}'
        )

        if not self._collected_metrics:
            return None

        return self._collected_metrics[0]

    @property
    def collected_metrics(self) -> typing.List[Metric]:
        assert self.collected, 'metrics have not been collected yet'
        return self._collected_metrics
