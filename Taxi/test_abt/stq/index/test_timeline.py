import datetime

import pytest

from abt import models
from abt.repositories import dto as repos_dto
from abt.services.index import dto
from abt.services.index import timeline as timeline_module
from test_abt import consts


EXPERIMENT = models.Experiment(
    id=1, name='test', type=models.ExperimentType.Experiment,
)

ITEM_UPDATED = consts.DEFAULT_REVISION_STARTED_AT + datetime.timedelta(
    days=123,
)


@pytest.mark.parametrize(
    ['initial_revisions', 'history_items', 'expected_revisions'],
    [
        pytest.param(
            [
                models.Revision(
                    id=10,
                    experiment_id=1,
                    started_at=consts.DEFAULT_REVISION_STARTED_AT,
                    ended_at=None,
                    data_available_days=[],
                    business_revision_id=1,
                    business_min_version_id=10,
                    business_max_version_id=10,
                ),
            ],
            [
                dto.RevisionHistoryItem(
                    revision_id=11, biz_revision_id=1, updated=ITEM_UPDATED,
                ),
            ],
            [
                models.Revision(
                    id=10,
                    experiment_id=1,
                    started_at=consts.DEFAULT_REVISION_STARTED_AT,
                    ended_at=None,
                    data_available_days=[],
                    business_revision_id=1,
                    business_min_version_id=10,
                    business_max_version_id=11,
                ),
            ],
            id='update max business revision',
        ),
        pytest.param(
            [
                models.Revision(
                    id=10,
                    experiment_id=1,
                    started_at=consts.DEFAULT_REVISION_STARTED_AT,
                    ended_at=None,
                    data_available_days=[],
                    business_revision_id=1,
                    business_min_version_id=10,
                    business_max_version_id=10,
                ),
            ],
            [
                dto.RevisionHistoryItem(
                    revision_id=11, biz_revision_id=2, updated=ITEM_UPDATED,
                ),
            ],
            [
                models.Revision(
                    id=10,
                    experiment_id=1,
                    started_at=consts.DEFAULT_REVISION_STARTED_AT,
                    ended_at=ITEM_UPDATED,
                    data_available_days=[],
                    business_revision_id=1,
                    business_min_version_id=10,
                    business_max_version_id=10,
                ),
                models.Revision(
                    id=11,
                    experiment_id=1,
                    started_at=ITEM_UPDATED,
                    ended_at=None,
                    data_available_days=[],
                    business_revision_id=2,
                    business_min_version_id=11,
                    business_max_version_id=11,
                ),
            ],
            id='create new revision and update prev ended_at',
        ),
        pytest.param(
            [],
            [
                dto.RevisionHistoryItem(
                    revision_id=11, biz_revision_id=2, updated=ITEM_UPDATED,
                ),
                dto.RevisionHistoryItem(
                    revision_id=12, biz_revision_id=2, updated=ITEM_UPDATED,
                ),
            ],
            [
                models.Revision(
                    id=11,
                    experiment_id=1,
                    started_at=ITEM_UPDATED,
                    ended_at=None,
                    data_available_days=[],
                    business_revision_id=2,
                    business_min_version_id=11,
                    business_max_version_id=12,
                ),
            ],
            id='no revisions before updates',
        ),
        pytest.param(
            [
                models.Revision(
                    id=11,
                    experiment_id=1,
                    started_at=consts.DEFAULT_REVISION_STARTED_AT,
                    ended_at=None,
                    data_available_days=[],
                    business_revision_id=2,
                    business_min_version_id=11,
                    business_max_version_id=12,
                ),
            ],
            [
                dto.RevisionHistoryItem(
                    revision_id=11, biz_revision_id=2, updated=ITEM_UPDATED,
                ),
            ],
            [
                models.Revision(
                    id=11,
                    experiment_id=1,
                    started_at=consts.DEFAULT_REVISION_STARTED_AT,
                    ended_at=None,
                    data_available_days=[],
                    business_revision_id=2,
                    business_min_version_id=11,
                    business_max_version_id=12,
                ),
            ],
            id='item revision <= current revision',
        ),
        pytest.param(
            [
                models.Revision(
                    id=11,
                    experiment_id=1,
                    started_at=consts.DEFAULT_REVISION_STARTED_AT,
                    ended_at=consts.DEFAULT_REVISION_STARTED_AT
                    + datetime.timedelta(days=43),
                    data_available_days=[],
                    business_revision_id=1,
                    business_min_version_id=11,
                    business_max_version_id=20,
                ),
                models.Revision(
                    id=21,
                    experiment_id=1,
                    started_at=consts.DEFAULT_REVISION_STARTED_AT
                    + datetime.timedelta(days=43),
                    ended_at=None,
                    data_available_days=[],
                    business_revision_id=2,
                    business_min_version_id=21,
                    business_max_version_id=21,
                ),
            ],
            [
                dto.RevisionHistoryItem(
                    revision_id=17, biz_revision_id=1, updated=ITEM_UPDATED,
                ),
            ],
            [
                models.Revision(
                    id=11,
                    experiment_id=1,
                    started_at=consts.DEFAULT_REVISION_STARTED_AT,
                    ended_at=consts.DEFAULT_REVISION_STARTED_AT
                    + datetime.timedelta(days=43),
                    data_available_days=[],
                    business_revision_id=1,
                    business_min_version_id=11,
                    business_max_version_id=20,
                ),
                models.Revision(
                    id=21,
                    experiment_id=1,
                    started_at=consts.DEFAULT_REVISION_STARTED_AT
                    + datetime.timedelta(days=43),
                    ended_at=None,
                    data_available_days=[],
                    business_revision_id=2,
                    business_min_version_id=21,
                    business_max_version_id=21,
                ),
            ],
            id='nothing happened with item from the middle of the timeline',
        ),
        pytest.param(
            [
                models.Revision(
                    id=11,
                    experiment_id=1,
                    started_at=consts.DEFAULT_REVISION_STARTED_AT,
                    ended_at=None,
                    data_available_days=[],
                    business_revision_id=1,
                    business_min_version_id=11,
                    business_max_version_id=11,
                ),
            ],
            [
                dto.RevisionHistoryItem(
                    revision_id=12, biz_revision_id=1, updated=ITEM_UPDATED,
                ),
                dto.RevisionHistoryItem(
                    revision_id=13,
                    biz_revision_id=2,
                    updated=ITEM_UPDATED + datetime.timedelta(days=13),
                ),
                dto.RevisionHistoryItem(
                    revision_id=15,
                    biz_revision_id=3,
                    updated=ITEM_UPDATED + datetime.timedelta(days=23),
                ),
                dto.RevisionHistoryItem(
                    revision_id=17,
                    biz_revision_id=3,
                    updated=ITEM_UPDATED + datetime.timedelta(days=56),
                ),
            ],
            [
                models.Revision(
                    id=11,
                    experiment_id=1,
                    started_at=consts.DEFAULT_REVISION_STARTED_AT,
                    ended_at=ITEM_UPDATED + datetime.timedelta(days=13),
                    data_available_days=[],
                    business_revision_id=1,
                    business_min_version_id=11,
                    business_max_version_id=12,
                ),
                models.Revision(
                    id=13,
                    experiment_id=1,
                    started_at=ITEM_UPDATED + datetime.timedelta(days=13),
                    ended_at=ITEM_UPDATED + datetime.timedelta(days=23),
                    data_available_days=[],
                    business_revision_id=2,
                    business_min_version_id=13,
                    business_max_version_id=13,
                ),
                models.Revision(
                    id=15,
                    experiment_id=1,
                    started_at=ITEM_UPDATED + datetime.timedelta(days=23),
                    ended_at=None,
                    data_available_days=[],
                    business_revision_id=3,
                    business_min_version_id=15,
                    business_max_version_id=17,
                ),
            ],
            id='several updates',
        ),
    ],
)
def test_update_revisions(
        initial_revisions, history_items, expected_revisions,
):
    timeline = timeline_module.ExperimentTimeline(
        EXPERIMENT, initial_revisions,
    )

    timeline.update_revisions(history_items)

    assert timeline.revisions == expected_revisions


@pytest.mark.parametrize(
    [
        'initial_revisions',
        'precomputes_revisions',
        'expected_apply_result',
        'expected_revisions',
    ],
    [
        pytest.param(
            [
                models.Revision(
                    id=11,
                    experiment_id=1,
                    started_at=consts.DEFAULT_REVISION_STARTED_AT,
                    ended_at=consts.DEFAULT_REVISION_STARTED_AT
                    + datetime.timedelta(days=43),
                    data_available_days=[],
                    business_revision_id=1,
                    business_min_version_id=11,
                    business_max_version_id=20,
                ),
                models.Revision(
                    id=21,
                    experiment_id=1,
                    started_at=consts.DEFAULT_REVISION_STARTED_AT
                    + datetime.timedelta(days=43),
                    ended_at=None,
                    data_available_days=[],
                    business_revision_id=2,
                    business_min_version_id=21,
                    business_max_version_id=21,
                ),
            ],
            [
                repos_dto.PrecomputesRevision(
                    revision_id=12,
                    data_available_days=['a', 'b', 'c'],
                    facets=[],
                ),
                repos_dto.PrecomputesRevision(
                    revision_id=15,
                    data_available_days=['b', 'c', 'd', 'e'],
                    facets=[],
                ),
                repos_dto.PrecomputesRevision(
                    revision_id=1, data_available_days=['d', 'e'], facets=[],
                ),
            ],
            dto.ApplyResult(success=False, broken_revisions=[1]),
            [
                models.Revision(
                    id=15,
                    experiment_id=1,
                    started_at=consts.DEFAULT_REVISION_STARTED_AT,
                    ended_at=consts.DEFAULT_REVISION_STARTED_AT
                    + datetime.timedelta(days=43),
                    data_available_days=['b', 'c', 'd', 'e'],
                    business_revision_id=1,
                    business_min_version_id=11,
                    business_max_version_id=20,
                ),
                models.Revision(
                    id=21,
                    experiment_id=1,
                    started_at=consts.DEFAULT_REVISION_STARTED_AT
                    + datetime.timedelta(days=43),
                    ended_at=None,
                    data_available_days=[],
                    business_revision_id=2,
                    business_min_version_id=21,
                    business_max_version_id=21,
                ),
            ],
            id='with one broken revision',
        ),
        pytest.param(
            [
                models.Revision(
                    id=11,
                    experiment_id=1,
                    started_at=consts.DEFAULT_REVISION_STARTED_AT,
                    ended_at=None,
                    data_available_days=[],
                    business_revision_id=1,
                    business_min_version_id=11,
                    business_max_version_id=20,
                ),
            ],
            [
                repos_dto.PrecomputesRevision(
                    revision_id=12,
                    data_available_days=['a', 'b', 'c'],
                    facets=[],
                ),
            ],
            dto.ApplyResult(success=True, broken_revisions=[]),
            [
                models.Revision(
                    id=12,
                    experiment_id=1,
                    started_at=consts.DEFAULT_REVISION_STARTED_AT,
                    ended_at=None,
                    data_available_days=['a', 'b', 'c'],
                    business_revision_id=1,
                    business_min_version_id=11,
                    business_max_version_id=20,
                ),
            ],
            id='no broken revisions',
        ),
    ],
)
def test_apply_precomputes_revisions(
        initial_revisions,
        precomputes_revisions,
        expected_apply_result,
        expected_revisions,
):
    timeline = timeline_module.ExperimentTimeline(
        EXPERIMENT, initial_revisions,
    )

    apply_result = timeline.apply_precomputes_revisions(precomputes_revisions)

    assert apply_result == expected_apply_result
    assert timeline.revisions == expected_revisions
