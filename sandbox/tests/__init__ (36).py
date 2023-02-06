import collections
import pytest

from browser.infra.library.conflict_score.conflict_score import PrConflictScoreInfo
from sandbox.projects.browser.conflict_score.BrowserReportPrConflictScore import utils


PrConflictScoreInfoCommentCase = collections.namedtuple(
    'PrConflictScoreInfoCommentCase',
    ['comment_text', 'pr_conflict_score_info']
)


TEST_CASES = [
    PrConflictScoreInfoCommentCase(
        comment_text='Total conflict_score: `+29 (380 -> 409)`',
        pr_conflict_score_info=PrConflictScoreInfo(
            total_conflict_score_change=29, from_conflict_score=380, target_conflict_score=409,
            conflict_score_change_by_file=None
        )
    ),
    PrConflictScoreInfoCommentCase(
        comment_text='Total conflict_score: `-4230 (4230 -> 0)`',
        pr_conflict_score_info=PrConflictScoreInfo(
            total_conflict_score_change=-4230, from_conflict_score=4230, target_conflict_score=0,
            conflict_score_change_by_file=None
        )
    ),
    PrConflictScoreInfoCommentCase(
        comment_text='Total conflict_score: `+1 (419 -> 420)`',
        pr_conflict_score_info=PrConflictScoreInfo(
            total_conflict_score_change=1, from_conflict_score=419, target_conflict_score=420,
            conflict_score_change_by_file=None
        )
    ),
    PrConflictScoreInfoCommentCase(
        comment_text='Total conflict_score: `-1 (414 -> 413)`',
        pr_conflict_score_info=PrConflictScoreInfo(
            total_conflict_score_change=-1, from_conflict_score=414, target_conflict_score=413,
            conflict_score_change_by_file=None
        )
    ),
    PrConflictScoreInfoCommentCase(
        comment_text='Total conflict_score: `+0 (750 -> 750)`',
        pr_conflict_score_info=PrConflictScoreInfo(
            total_conflict_score_change=0, from_conflict_score=750, target_conflict_score=750,
            conflict_score_change_by_file=None
        )
    ),
    PrConflictScoreInfoCommentCase(
        comment_text='Total conflict_score: `+0 (0 -> 0)`',
        pr_conflict_score_info=PrConflictScoreInfo(
            total_conflict_score_change=0, from_conflict_score=0, target_conflict_score=0,
            conflict_score_change_by_file=None
        )
    ),
]


@pytest.mark.parametrize(
    'case',
    TEST_CASES,
    ids=lambda case: str(case.comment_text)
)
def test__parse_pr_conflict_score_comment__returns_value(case):
    """
    :type case: PrConflictScoreInfoCommentCase
    """
    result = utils.parse_pr_conflict_score_comment(case.comment_text)
    assert result.total_conflict_score_change == case.pr_conflict_score_info.total_conflict_score_change
    assert result.from_conflict_score == case.pr_conflict_score_info.from_conflict_score
    assert result.target_conflict_score == case.pr_conflict_score_info.target_conflict_score
    assert result.conflict_score_change_by_file is None


@pytest.mark.parametrize(
    'case',
    TEST_CASES,
    ids=lambda case: str(case.comment_text)
)
def test__render_pr_conflict_score_comment__returns_value(case):
    """
    :type case: PrConflictScoreInfoCommentCase
    """
    pr_conflict_score_info = case.pr_conflict_score_info

    comment_text = utils.render_pr_conflict_score_comment(
        total_conflict_score_change=pr_conflict_score_info.total_conflict_score_change,
        previous_total_conflict_score=pr_conflict_score_info.from_conflict_score,
        current_total_conflict_score=pr_conflict_score_info.target_conflict_score,
    )

    assert comment_text == case.comment_text


@pytest.mark.parametrize(
    'comment_text',
    [
        'А почему тут стало всегда true ?',
        'Давай более полное название тесту дадим\n`MoveTheOnlyTab` -> `MoveAloneTabToNewWindow`\nИли в этом духе.\n',
        'Added veto.\n**Too high conflict score change**\nThis Pull Request increases the conflict score too high'
        ' (threshold is 30). Add one of veto-approvers (dmgor) to review this PR',
        'Removed `conflict_score` veto.',
    ]
)
def test_parse_pr_conflict_score_info_from_comment_returns_none(comment_text):
    """
    :type comment_text: str
    """
    assert utils.parse_pr_conflict_score_comment(comment_text) is None
