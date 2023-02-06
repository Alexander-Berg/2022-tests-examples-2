from functools import partial

import pytest

from pahtest.fake import FakeTest
from pahtest.results import ActionResult, Results
from pahtest.errors import ResultsFilterArgsError

from tests.unit.utils import get_test_result


def test_action_result_output_waiting(tap, action):
    # - show waiting attempts for failed result
    res = ActionResult(
        name='Waiting failed', success=False,
        description='Desc waiting failed', attempts=10, test=action
    )
    tap.eq_ok(
        res.as_tap(),
        f'not ok 1 - {res.description}'
        f'\n# Waiting failed with 10 attempts, 0.20s step, 20.0s timeout',
        'Waiting attempts show.'
    )

    # - don't show waiting attempts for success result
    res = ActionResult(
        name='Waiting failed', success=True,
        description='Desc waiting failed', attempts=10, test=action
    )
    tap.eq_ok(
        res.as_tap(), f'ok 1 - {res.description}', 'Waiting attempts no show.'
    )


@pytest.mark.skip('Took it from functional tests. Needed to improve.')
def test_action_result_output(tap):
    # - ok output with description for ok test
    res = ActionResult(
        name='First test', success=True, description='Just result.'
    )
    tap.eq_ok(res.as_tap(1), f'ok 1 - {res.description}', 'Succeed result.')

    # - failed output with message for failed test
    res = ActionResult(
        name='Second test',
        success=False, description='Just result.', message='Just error message.'
    )
    tap.eq_ok(
        res.as_tap(2), f'not ok 2 - {res.description}\n# {res.message}',
        'Failed result.'
    )

    # - failed output with empty message
    res = ActionResult(
        name='Third test',
        success=False, description='Just result.', message=''
    )
    tap.eq_ok(
        res.as_tap(3), f'not ok 3 - {res.description}',
        'Failed result.'
    )


@pytest.mark.skip('Took it from functional tests. Needed to improve.')
def test_plugins_output(tap):
    results = Results([
        ActionResult(
            name='First test', success=True, description='Just result.'
        ),
        ActionResult(
            name='Second test',
            success=False, description='Just result.',
            message='Just error message.'
        ),
        ActionResult(
            name='Third test',
            success=False, description='Just result.', message=''
        ),
    ])
    tap.eq_ok(
        results.as_tap(),
        f'1..3'
        f'\nok 1 - Just result.'
        f'\nnot ok 2 - Just result.'
        f'\n# Just error message.'
        f'\nnot ok 3 - Just result.'
        f'\nLooks like you failed 2 tests of 3',
        'Results object as tap is correct.'
    )
    tap()


@pytest.mark.skip('Took it from functional tests. Needed to improve.')
def test_subtests_tap():
    r = ActionResult(
        name='get_ok', success=False, description='Some test.',
        subresults=Results([
            ActionResult(
                name='has',
                success=True, description='First subtest.',
            ),
            ActionResult(
                name='has',
                success=True, description='Second subtest.',
            ),
            ActionResult(
                name='has',
                success=False, description='Third subtest.',
                message='Error for the third.'
            ),
        ])
    )
    out = r.as_tap(number=1)
    print('\nTap output:', out)
    assert '  ok 1 - First subtest.' in out
    assert '  ok 2 - Second subtest.' in out
    assert '  not ok 3 - Third subtest.' in out
    assert '  # Error for the third.' in out
    assert '1..3' in out
    assert '  Looks like you failed 1 tests of 3' in out
    assert 'not ok 1 - Some test.' in out


def test_results_filter_by():
    """
    Test the whole Results([]).filter_by(field__operator=value)
    syntax by example with "message__has='some'".
    """
    test = FakeTest(tag='1')
    tr = partial(get_test_result, test=test)
    result_matched = tr(message='with some message')
    result_matched_again = tr(message='some msg again')
    result_not_matched = tr(message='1')
    result_empty = tr(message='')
    #
    assert [] == Results([]).f(message__has='some').list
    #
    assert [] == Results([result_empty]).f(message__has='some').list
    #
    assert [result_matched] == Results([result_matched]).f(message__has='').list
    #
    got = (
        Results([result_matched, result_not_matched])
        .f(message__has='some')
        .list
    )
    assert [result_matched] == got
    #
    got = (
        Results([result_matched, result_matched_again])
        .f(message__has='some')
        .list
    )
    assert [result_matched, result_matched_again] == got
    #
    got = (
        Results([result_matched, result_matched_again])
        .f(message__has='some')
        .f(message__has='message')
        .list
    )
    assert [result_matched] == got
    #
    with pytest.raises(ResultsFilterArgsError) as e:
        Results([]).f(keywrong='value')
    #
    assert 'Got keywrong=value' in str(e.value)
