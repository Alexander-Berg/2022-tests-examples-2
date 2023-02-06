from typing import Optional, List

import six

import atlas.domain


class DictMetricsStorage(object):
    """In memory variant of class `atlas.domain.metric.MetricsStorage`"""

    def __init__(self):
        self._metrics = {}

    def create(self, metric):
        # type: (atlas.domain.Metric) -> None
        self._metrics[metric.id] = metric

    def get(self, metric_id):
        # type: (str) -> Optional[atlas.domain.Metric]
        return self._metrics[metric_id]

    def replace(self, metric):
        self._metrics[metric.id] = metric

    def delete(self, metric_id):
        # type: (str) -> None
        del self._metrics[metric_id]

    def get_list(self, mongo_filter=None):
        # type: (...) -> List[atlas.domain.Metric]
        if mongo_filter is not None:
            raise RuntimeError

        return list(metric for metric in six.itervalues(self._metrics))

    def get_protected_edit_metrics(self) \
            -> List[atlas.domain.metric.ProtectedEditMetricIDMRole]:
        return [
            atlas.domain.metric.ProtectedEditMetricIDMRole(
                id=metric.id,
                en_name=metric.en,
                ru_name=metric.metric
            )
            for metric in self._metrics.values()
        ]

    def get_protected_view_group(self, metric_id: str) -> Optional[str]:
        return self._metrics.get(metric_id, {}).get('protected_view_group')

    def exists(self, metric_id):
        return metric_id in self._metrics
