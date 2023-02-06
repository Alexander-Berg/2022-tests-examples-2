# pylint: disable=W0212
import pytest

from taxi.util import dates as dates_utils

from abt import models
from abt.logic import revisions as revisions_logic
from abt.logic import revisions_groups as revisions_groups_logic


CONTROL_GROUP_BY_REGEX = models.RevisionsGroup(
    revision_id=1, group_id=1, title='control group',
)
ANOTHER_CONTROL_GROUP_BY_REGEX = models.RevisionsGroup(
    revision_id=1, group_id=2, title='controlcontrol',
)
CONTROL_GROUP_BY_FLAGS = models.RevisionsGroup(
    revision_id=1,
    group_id=3,
    title='some title',
    flags=models.RevisionsGroupFlags(is_signal=True),
)
ANOTHER_CONTROL_GROUP_BY_FLAGS = models.RevisionsGroup(
    revision_id=1,
    group_id=4,
    title='group title',
    flags=models.RevisionsGroupFlags(is_signal=True),
)
TEST_GROUP = models.RevisionsGroup(
    revision_id=1, group_id=5, title='just test group',
)
ANOTHER_TEST_GROUP = models.RevisionsGroup(
    revision_id=1, group_id=6, title='just test group',
)
TECH_GROUP = models.RevisionsGroup(
    revision_id=1,
    group_id=7,
    title='technical group',
    flags=models.RevisionsGroupFlags(is_tech_group=True),
)
TECH_GROUP_CONTROL_REGEX = models.RevisionsGroup(
    revision_id=1,
    group_id=8,
    title='control group',
    flags=models.RevisionsGroupFlags(is_tech_group=True),
)
TECH_GROUP_CONTROL_FLAGS = models.RevisionsGroup(
    revision_id=1,
    group_id=9,
    title='tech group',
    flags=models.RevisionsGroupFlags(is_signal=True, is_tech_group=True),
)
PAIRED_SIGNAL_CONTROL_FLAGS = models.RevisionsGroup(
    revision_id=1,
    group_id=10,
    title='paired signal',
    flags=models.RevisionsGroupFlags(is_signal=True, is_paired_signal=True),
)


@pytest.mark.parametrize(
    'day,revision_start,revision_end,expected',
    [
        pytest.param(
            '2020-01-01',
            dates_utils.parse_timestring_aware('2019-12-20T10:10:10+0000'),
            dates_utils.parse_timestring_aware('2019-12-30T10:10:10+0000'),
            'after',
            id='Day starts after revision ends',
        ),
        pytest.param(
            '2020-01-01',
            dates_utils.parse_timestring_aware('2020-02-01T10:10:10+0000'),
            dates_utils.parse_timestring_aware('2020-02-03T10:10:10+0000'),
            'before',
            id='Day ends before revision starts',
        ),
        pytest.param(
            '2020-01-10',
            dates_utils.parse_timestring_aware('2020-01-01T10:10:10+0000'),
            dates_utils.parse_timestring_aware('2020-02-01T10:10:10+0000'),
            'inside',
            id='Day inside revision',
        ),
        pytest.param(
            '2020-01-10',
            dates_utils.parse_timestring_aware('2020-01-01T10:10:10+0000'),
            None,
            'inside',
            id='Day inside endless revision',
        ),
        pytest.param(
            '2020-01-01',
            dates_utils.parse_timestring_aware('2020-01-01T10:00:00+0000'),
            dates_utils.parse_timestring_aware('2020-01-01T11:00:00+0000'),
            'inside',
            id='Revision lives inside day',
        ),
        pytest.param(
            '2020-01-01',
            dates_utils.parse_timestring_aware('2020-01-01T10:00:00+0000'),
            None,
            'inside',
            id='Revision starts inside day and live',
        ),
        pytest.param(
            '2020-01-01',
            dates_utils.parse_timestring_aware('2019-01-01T10:00:00+0000'),
            dates_utils.parse_timestring_aware('2020-01-01T11:00:00+0000'),
            'inside',
            id='Revision ends inside day',
        ),
        pytest.param(
            '2020-01-01',
            dates_utils.parse_timestring_aware('2020-01-01T23:59:59+0000'),
            None,
            'inside',
            id='Revision starts inside day. Check UTC',
        ),
        pytest.param(
            '2020-01-01',
            dates_utils.parse_timestring_aware('2019-01-01T10:00:00+0000'),
            dates_utils.parse_timestring_aware('2020-01-01T00:00:01+0000'),
            'inside',
            id='Revision ends inside day. Check UTC',
        ),
    ],
)
def test_day_type_calculation(day, revision_start, revision_end, expected):
    assert (
        revisions_logic.compute_day_type(day, revision_start, revision_end)
        == expected
    )


@pytest.mark.config(
    ABT_REVISION_CONTROL_GROUP_REGEX_LIST=['control', 'controlcontrol'],
)
@pytest.mark.parametrize(
    ['groups', 'expected'],
    [
        pytest.param(
            [], revisions_groups_logic.IdentifyResults(), id='empty_list',
        ),
        pytest.param(
            [CONTROL_GROUP_BY_REGEX],
            revisions_groups_logic.IdentifyResults(control_group=1),
            id='one_control_only',
        ),
        pytest.param(
            [TEST_GROUP],
            revisions_groups_logic.IdentifyResults(),
            id='one_test_only',
        ),
        pytest.param(
            [CONTROL_GROUP_BY_REGEX, TEST_GROUP],
            revisions_groups_logic.IdentifyResults(
                control_group=1, test_groups=[5],
            ),
            id='one_control_one_test_regex',
        ),
        pytest.param(
            [CONTROL_GROUP_BY_FLAGS, TEST_GROUP],
            revisions_groups_logic.IdentifyResults(
                control_group=3, test_groups=[5],
            ),
            id='one_control_one_test_flags',
        ),
        pytest.param(
            [CONTROL_GROUP_BY_REGEX, TEST_GROUP, ANOTHER_TEST_GROUP],
            revisions_groups_logic.IdentifyResults(control_group=1),
            id='one_control_many_test',
        ),
        pytest.param(
            [CONTROL_GROUP_BY_REGEX, CONTROL_GROUP_BY_FLAGS, TEST_GROUP],
            revisions_groups_logic.IdentifyResults(control_group=3),
            id='many_control_groups_one_flag',
        ),
        pytest.param(
            [
                CONTROL_GROUP_BY_REGEX,
                ANOTHER_CONTROL_GROUP_BY_REGEX,
                TEST_GROUP,
            ],
            revisions_groups_logic.IdentifyResults(),
            id='many_control_groups_all_regex',
        ),
        pytest.param(
            [
                CONTROL_GROUP_BY_FLAGS,
                ANOTHER_CONTROL_GROUP_BY_FLAGS,
                TEST_GROUP,
            ],
            revisions_groups_logic.IdentifyResults(),
            id='many_control_groups_all_flags',
        ),
        pytest.param(
            [
                CONTROL_GROUP_BY_REGEX,
                TECH_GROUP_CONTROL_REGEX,
                TECH_GROUP_CONTROL_FLAGS,
                TEST_GROUP,
            ],
            revisions_groups_logic.IdentifyResults(
                control_group=1, test_groups=[5],
            ),
            id='tech_groups_control_regex',
        ),
        pytest.param(
            [
                CONTROL_GROUP_BY_FLAGS,
                TECH_GROUP_CONTROL_REGEX,
                TECH_GROUP_CONTROL_FLAGS,
                TEST_GROUP,
            ],
            revisions_groups_logic.IdentifyResults(
                control_group=3, test_groups=[5],
            ),
            id='tech_groups_control_flags',
        ),
        pytest.param(
            [TEST_GROUP, ANOTHER_TEST_GROUP, PAIRED_SIGNAL_CONTROL_FLAGS],
            revisions_groups_logic.IdentifyResults(
                control_group=10, test_groups=[6],
            ),
            id='control_group_with_paired_signal_flag',
        ),
        pytest.param(
            [ANOTHER_CONTROL_GROUP_BY_REGEX, TEST_GROUP],
            revisions_groups_logic.IdentifyResults(
                control_group=2, test_groups=[5],
            ),
            id='one_control_group_matches_by_many_regexes',
        ),
    ],
)
def test_identify_groups(groups, expected, web_context):
    assert (
        revisions_groups_logic.identify_groups(groups, web_context.config)
        == expected
    )


@pytest.mark.parametrize(
    ['groups', 'expected'],
    [
        pytest.param([], None, id='empty_list'),
        pytest.param([PAIRED_SIGNAL_CONTROL_FLAGS], None, id='only_one_group'),
        pytest.param(
            [TEST_GROUP, CONTROL_GROUP_BY_FLAGS],
            None,
            id='no_paired_signal_groups',
        ),
        pytest.param(
            [PAIRED_SIGNAL_CONTROL_FLAGS, TEST_GROUP], None, id='wrong_list',
        ),
        pytest.param(
            [TEST_GROUP, PAIRED_SIGNAL_CONTROL_FLAGS], 5, id='only_two_groups',
        ),
        pytest.param(
            [TEST_GROUP, PAIRED_SIGNAL_CONTROL_FLAGS, ANOTHER_TEST_GROUP],
            5,
            id='paired_signal_group_in_the_middle',
        ),
        pytest.param(
            [TEST_GROUP, ANOTHER_TEST_GROUP, PAIRED_SIGNAL_CONTROL_FLAGS],
            6,
            id='paired_signal_group_last',
        ),
    ],
)
def test_get_previous_group_id(groups, expected):
    assert (
        revisions_groups_logic._get_previous_group_id(
            groups, PAIRED_SIGNAL_CONTROL_FLAGS.group_id,
        )
        == expected
    )
