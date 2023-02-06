from __future__ import annotations

import datetime
import typing as tp

from taxi.util import dates as dates_utils

from abt import consts as app_consts
from abt import models
from abt.logic import revisions as revisions_logic
from test_abt import consts
from . import base


class ExperimentInfoBuilder(base.BaseBuilder):
    def __init__(
            self,
            name: str = consts.DEFAULT_EXPERIMENT_NAME,
            description: str = consts.DEFAULT_EXPERIMENT_DESCRIPTION,
    ):
        self._name = name
        self._description = description
        self._revisions: tp.List[tp.Dict[str, tp.Any]] = []

    def add_revision(
            self,
            revision_id: int = consts.DEFAULT_REVISION_ID,
            started_at: datetime.datetime = consts.DEFAULT_REVISION_STARTED_AT,
            ended_at: tp.Optional[
                datetime.datetime
            ] = consts.DEFAULT_REVISION_ENDED_AT,
            available_days: tp.Optional[tp.List[dict]] = None,
            create_default_group: bool = True,
    ) -> ExperimentInfoBuilder:
        if not available_days:
            available_days = [
                {
                    'day': day,
                    'type': revisions_logic.compute_day_type(
                        day, started_at, ended_at,
                    ),
                }
                for day in consts.DEFAULT_REVISION_DATA_AVAILABLE_DAYS
            ]

        self._revisions.append(
            {
                'id': revision_id,
                'started_at': dates_utils.timestring(started_at),
                'ended_at': (
                    dates_utils.timestring(ended_at) if ended_at else None
                ),
                'data_available_days': available_days,
                'experiment_groups': [],
            },
        )

        if create_default_group:
            self.add_revision_group(revision_id=revision_id)

        return self

    def add_revision_group(
            self,
            revision_id: int = consts.DEFAULT_REVISION_ID,
            group_id: int = consts.DEFAULT_REVISION_GROUP_ID,
            title: str = consts.DEFAULT_REVISION_GROUP_TITLE,
            is_control: bool = False,
            is_selected: bool = False,
    ) -> ExperimentInfoBuilder:
        for revision in self._revisions:
            if revision['id'] == revision_id:
                revision['experiment_groups'].append(
                    {
                        'id': group_id,
                        'title': title,
                        'is_control': is_control,
                        'is_selected': is_selected,
                    },
                )

        return self

    def build(self) -> dict:
        return {
            'experiment': {
                'name': self._name,
                'description': self._description,
                'status': 'running',
            },
            'revisions': self._revisions,
        }


class V2ExperimentsBuilder(base.BaseBuilder):
    _name: str
    _description: str
    _tracker_task: tp.Optional[str]
    _revisions: tp.List[dict]

    def __init__(
            self,
            name: str = consts.DEFAULT_EXPERIMENT_NAME,
            description: str = consts.DEFAULT_EXPERIMENT_DESCRIPTION,
            tracker_task: tp.Optional[
                str
            ] = consts.DEFAULT_EXPERIMENT_TRACKER_TASK,
    ):
        self._name = name
        self._description = description
        self._tracker_task = tracker_task
        self._revisions = []

    def add_revision(
            self,
            revision_id: int = consts.DEFAULT_REVISION_ID,
            started_at: datetime.datetime = consts.DEFAULT_REVISION_STARTED_AT,
            ended_at: tp.Optional[
                datetime.datetime
            ] = consts.DEFAULT_REVISION_ENDED_AT,
            available_days: tp.Optional[tp.List[dict]] = None,
    ) -> V2ExperimentsBuilder:
        if not available_days:
            available_days = [
                {
                    'day': day,
                    'type': revisions_logic.compute_day_type(
                        day, started_at, ended_at,
                    ),
                }
                for day in consts.DEFAULT_REVISION_DATA_AVAILABLE_DAYS
            ]

        self._revisions.append(
            {
                'id': revision_id,
                'started_at': dates_utils.timestring(started_at),
                'ended_at': (
                    dates_utils.timestring(ended_at) if ended_at else None
                ),
                'data_available_days': available_days,
            },
        )

        return self

    def set_tracker_task(
            self, tracker_task: tp.Optional[str],
    ) -> V2ExperimentsBuilder:
        self._tracker_task = tracker_task
        return self

    def build(self) -> dict:
        resp: tp.Dict[str, tp.Any] = {
            'experiment': {
                'name': self._name,
                'description': self._description,
            },
            'revisions': self._revisions,
        }

        if self._tracker_task:
            resp['experiment']['tracker_task'] = self._tracker_task

        return resp


class ComputeMetricsBuilder(base.BaseBuilder):
    _control_group: models.RevisionsGroup
    _test_groups: tp.List[models.RevisionsGroup]
    _metrics_groups: tp.List[dict]

    def __init__(
            self,
            control_group: models.RevisionsGroup,
            test_groups: tp.List[models.RevisionsGroup],
    ):
        self._control_group = control_group
        self._test_groups = test_groups
        self._metrics_groups = []

    def add_metrics_group(
            self,
            *,
            metrics_group: models.MetricsGroup,
            metrics: tp.Optional[tp.List[dict]] = None,
    ) -> ComputeMetricsBuilder:
        self._metrics_groups.append(
            {
                'id': metrics_group.id,
                'description': metrics_group.description,
                'is_collapsed': metrics_group.is_collapsed,
                'enabled': metrics_group.enabled,
                'owners': metrics_group.owners,
                'scopes': metrics_group.scopes,
                'title': metrics_group.title,
                'created_at': metrics_group.created_at_timestring,
                'updated_at': metrics_group.updated_at_timestring,
                'position': metrics_group.position,
                'version': metrics_group.version,
            },
        )

        if metrics is not None:
            self._metrics_groups[-1]['metrics'] = self._enrich_with_groups_ids(
                metrics,
            )

        return self

    def _enrich_with_groups_ids(self, metrics: tp.List[dict]) -> tp.List[dict]:
        for metric in metrics:
            metric['experiment_groups']['control'][
                'id'
            ] = self._control_group.group_id

            assert len(metric['experiment_groups']['test']) == len(
                self._test_groups,
            ), 'Number of metrics groups != number of groups'

            for i, group in enumerate(metric['experiment_groups']['test']):
                assert 'id' not in group, 'Set group in __init__'
                group['id'] = self._test_groups[i].group_id

        return metrics

    def build(self) -> dict:
        return {
            'experiment_groups': {
                'control': {
                    'id': self._control_group.group_id,
                    'title': self._control_group.title,
                },
                'test': [
                    {'id': group.group_id, 'title': group.title}
                    for group in self._test_groups
                ],
            },
            'metrics_groups': self._metrics_groups,
        }

    @classmethod
    def create_metric(
            cls,
            *,
            test: tp.List[dict],
            control_value: tp.Optional[
                str
            ] = app_consts.METRIC_VALUE_PLACEHOLDER,
            name: str = consts.DEFAULT_VALUE_METRIC_NAME,
            title: str = consts.DEFAULT_VALUE_METRIC_TITLE,
            description: str = consts.DEFAULT_METRIC_DESCRIPTION,
            docs_url: str = consts.DEFAULT_DOCS_URL_TEMPLATE,
            is_verified: bool = False,
    ):
        return {
            'name': name,
            'title': title,
            'description': description,
            'docs_url': docs_url,
            'is_verified': is_verified,
            'experiment_groups': {
                'control': {'metric': {'value': control_value}},
                'test': test,
            },
        }

    @classmethod
    def create_test_metric_values(
            cls,
            *,
            value: str = app_consts.METRIC_VALUE_PLACEHOLDER,
            abs_diff: str = app_consts.METRIC_VALUE_PLACEHOLDER,
            rel_diff: str = app_consts.METRIC_VALUE_PLACEHOLDER,
            mannwhitneyu: str = app_consts.METRIC_VALUE_PLACEHOLDER,
            shapiro: str = app_consts.METRIC_VALUE_PLACEHOLDER,
            ttest: str = app_consts.METRIC_VALUE_PLACEHOLDER,
            background: str = consts.DEFAULT_BACKGROUND_COLOR,
            font: str = consts.DEFAULT_FONT_COLOR,
            color_alias: str = consts.DEFAULT_COLOR_ALIAS,
            is_colored: bool = False,
            wiki_color: str = consts.DEFAULT_WIKI_COLOR,
    ) -> dict:
        return {
            'metric': {
                'value': value,
                'diff': {'abs': abs_diff, 'relative': rel_diff},
                'pvalues': {
                    'mannwhitneyu': mannwhitneyu,
                    'shapiro': shapiro,
                    'ttest': ttest,
                },
                'colors': {
                    'background': background,
                    'font': font,
                    'alias': color_alias,
                    'wiki': wiki_color,
                },
                'is_colored': is_colored,
            },
        }


_BUILDERS: tp.Dict[str, tp.Type[base.BaseBuilder]] = {
    '/v1/experiments': ExperimentInfoBuilder,
    '/v1/metrics': ComputeMetricsBuilder,
    '/v2/experiments': V2ExperimentsBuilder,
}


def find_builder(path: str) -> tp.Type[base.BaseBuilder]:
    builder = _BUILDERS.get(path)
    assert builder, f'No response builder for path: {path}'
    return builder
