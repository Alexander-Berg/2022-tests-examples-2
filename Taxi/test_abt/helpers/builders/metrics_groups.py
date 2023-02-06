from __future__ import annotations

import typing as tp

import yaml

from test_abt import consts
from . import base


class MetricsGroupConfigBuilder(base.BaseBuilder):
    metrics: tp.List[dict]
    precomputes: tp.List[dict]
    observations: tp.Optional[dict] = None

    def __init__(self, facets_builder):
        self.facets_builder = facets_builder

        self.metrics = []
        self.precomputes = []

    def add_value_metric(
            self,
            name: str = consts.DEFAULT_VALUE_METRIC_NAME,
            title: str = consts.DEFAULT_VALUE_METRIC_TITLE,
            value: str = consts.DEFAULT_VALUE_COLUMN,
            description: str = consts.DEFAULT_METRIC_DESCRIPTION,
            greater_is_better: tp.Optional[bool] = None,
    ) -> MetricsGroupConfigBuilder:
        config: tp.Dict[str, tp.Any] = {
            'name': name,
            'title': title,
            'params': {'type': 'value', 'value': value},
            'description': description,
        }
        if greater_is_better is not None:
            config['greater_is_better'] = greater_is_better
        self.metrics.append(config)
        return self

    def add_ratio_metric(
            self,
            name: str = consts.DEFAULT_RATIO_METRIC_NAME,
            title: str = consts.DEFAULT_RATIO_METRIC_TITLE,
            numerator: str = consts.DEFAULT_NUMERATOR_COLUMN,
            denominator: str = consts.DEFAULT_DENOMINATOR_COLUMN,
            description: str = consts.DEFAULT_METRIC_DESCRIPTION,
            greater_is_better: tp.Optional[bool] = None,
    ) -> MetricsGroupConfigBuilder:
        config: tp.Dict[str, tp.Any] = {
            'name': name,
            'title': title,
            'params': {
                'type': 'ratio',
                'numerator': numerator,
                'denominator': denominator,
            },
            'description': description,
        }
        if greater_is_better is not None:
            config['greater_is_better'] = greater_is_better
        self.metrics.append(config)
        return self

    def add_precomputes(
            self,
            cluster: str = consts.DEFAULT_YT_CLUSTER,
            path: str = consts.DEFAULT_YT_PATH,
            facets: tp.Optional[dict] = None,
    ) -> MetricsGroupConfigBuilder:
        assert not self.precomputes, self.precomputes
        self.precomputes.append(
            {
                'storage': {'yt': [{'cluster': cluster, 'path': path}]},
                'facets': facets if facets else self.facets_builder.build(),
            },
        )
        return self

    def add_observations(
            self,
            cluster: str = consts.DEFAULT_YT_CLUSTER,
            path: str = consts.DEFAULT_YT_PATH,
            args: tp.Optional[tp.List[dict]] = None,
            time: str = consts.DEFAULT_OBSERVATIONS_TIME,
            measures: tp.Optional[tp.List[str]] = None,
    ) -> MetricsGroupConfigBuilder:
        assert self.observations is None, self.observations
        self.observations = {
            'storage': {'cluster': cluster, 'path': path},
            'arguments': (
                args if args is not None else consts.DEFAULT_OBSERVATIONS_ARGS
            ),
            'time': time,
            'measures': (
                measures
                if measures is not None
                else consts.DEFAULT_OBSERVATIONS_MEASURES
            ),
        }
        return self

    def build(self) -> dict:
        _ensure(self.metrics, 'metrics')
        _ensure(self.precomputes, 'precomputes')

        if self.observations is None:
            self.add_observations()

        obj: tp.Dict[tp.Any, tp.Any] = {
            'metrics': self.metrics,
            'precomputes': self.precomputes,
            'observations': self.observations,
        }

        return obj

    def build_yaml(self) -> str:
        return yaml.dump(self.build())


def _ensure(obj: tp.Any, obj_name: str) -> None:
    assert obj, f'{obj_name} is required for metrics group config'
