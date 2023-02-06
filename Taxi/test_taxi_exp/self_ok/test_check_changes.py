import pytest

from taxi_exp.lib.context_operations import checking
from test_taxi_exp.helpers import experiment


@pytest.mark.parametrize(
    'current, new, ignored_paths, expected_result',
    [
        pytest.param(
            experiment.generate(),
            experiment.generate(),
            [],
            (False, None),
            id='no changes',
        ),
        pytest.param(
            experiment.generate(),
            experiment.generate(description='Change description'),
            [],
            (
                True,
                'value for key description '
                '(located by path `description`) is changed',
            ),
            id='check simple change',
        ),
        pytest.param(
            experiment.generate(clauses=[experiment.make_clause('first')]),
            experiment.generate(clauses=[experiment.make_clause('second')]),
            [],
            (
                True,
                'value for key title '
                '(located by path `clauses.0.title`) is changed',
            ),
            id='check deep change',
        ),
        pytest.param(
            experiment.generate(clauses=[experiment.make_clause('first')]),
            experiment.generate(clauses=[experiment.make_clause('second')]),
            ['clauses.*.title'],
            (False, None),
            id='ignore change keys in lists',
        ),
    ],
)
def test_check_changes(current, new, ignored_paths, expected_result):
    assert (
        checking.check_changes_is_complex(
            current_obj=current, new_obj=new, ignored_paths=ignored_paths,
        )
        == expected_result
    )
