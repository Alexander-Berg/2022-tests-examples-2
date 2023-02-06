import copy
import dataclasses
import numbers
import typing


def _escape_key(key):
    return key.replace('.', '_')


def _extend_prefix(prefix, key):
    return '.'.join([prefix, key]).lstrip('.')


# pylint: disable=too-many-branches
def _get_sensors(prefix, obj, current_labels, current_label_name=None):
    for key in obj:
        # should not happen, too late to process anyway
        if key == '$meta':
            raise f'Unexpected metadata at {prefix}'

        value = obj[key]
        labels = copy.copy(current_labels)
        label_name = current_label_name

        children_label_name = None
        path = None

        # HACK: these may have no metadata, add it by hand
        if prefix == 'http' and key in ('by-path', 'by-handler'):
            path = prefix
            children_label_name = 'http_' + key[3:]

        # parse metadata if present
        if isinstance(value, dict):
            metadata = value.pop('$meta', None)
            if isinstance(metadata, dict):
                if 'solomon_skip' in metadata:
                    path = prefix
                elif 'solomon_rename' in metadata:
                    path = _extend_prefix(
                        prefix, _escape_key(metadata['solomon_rename']),
                    )

                if 'solomon_label' in metadata:
                    label_name = metadata['solomon_label']

                if 'solomon_children_labels' in metadata:
                    children_label_name = metadata['solomon_children_labels']

        if label_name is not None:
            path = prefix
            labels[label_name] = key

        if path is None:
            path = _extend_prefix(prefix, _escape_key(key))

        # now process the value
        if isinstance(value, dict):
            yield from _get_sensors(path, value, labels, children_label_name)
        else:
            # Solomon does not accept string values, but we have some for
            # compatibility reasons
            if isinstance(value, str):
                try:
                    value = float(value)
                except ValueError as exc:
                    raise exc

            if isinstance(value, numbers.Number):
                labels['sensor'] = path
                yield labels, value


@dataclasses.dataclass
class SolomonMetric:
    labels: typing.Dict[str, str]
    value: numbers.Number


@dataclasses.dataclass
class SolomonMetrics:
    metrics: typing.List[SolomonMetric]

    def __init__(self, metrics_json):
        self.metrics = []
        for labels, value in _get_sensors('', metrics_json, {}):
            self.metrics.append(SolomonMetric(labels=labels, value=value))

    def find_metric(self, matching_labels) -> typing.Optional[SolomonMetric]:
        for metric in self.metrics:
            if self._match_metrics(metric, matching_labels):
                return metric
        return None

    @staticmethod
    def _match_metrics(metric, matching_labels):
        # check each matching label exists in metric.labels
        for label_name, label_key in matching_labels.items():
            label_exists = False
            for metric_label_name, metric_label_key in metric.labels.items():
                if (
                        metric_label_name == label_name
                        and metric_label_key == label_key
                ):
                    label_exists = True
                    break
            if not label_exists:
                return False
        return True
