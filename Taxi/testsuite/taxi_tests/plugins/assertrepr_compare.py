from taxi_tests.utils import comparison


def pytest_addoption(parser):
    """
    :param parser: pytest's argument parser
    """
    group = parser.getgroup('common')
    group.addoption(
        '--assert-mode',
        choices=['default', 'combine', 'analyze'],
        default='combine',
        help='Assertion representation mode, combined by default',
    )
    group.addoption(
        '--assert-depth',
        type=int,
        default=None,
        help='Depth of assertions, use 0 for simple print different items',
    )


# pylint: disable=invalid-name
def pytest_assertrepr_compare(config, op, left, right):
    assertion_mode = config.option.assert_mode
    if (
            # pylint: disable=unidiomatic-typecheck
            assertion_mode == 'default'
            or op != '=='
            or type(left) is not type(right)
            or type(left) not in comparison.TYPES
    ):
        return None
    add_full_diff = assertion_mode == 'combine'
    add_empty_lines = config.option.verbose > 1
    return comparison.compare_pair(
        left,
        right,
        add_empty_lines=add_empty_lines,
        add_full_diff=add_full_diff,
        depth=config.option.assert_depth,
    )
