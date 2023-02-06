# pylint: disable=import-error

import typing

# pylint: disable=import-error
from sql_hints.lib import checker
from sql_hints.lib import manager
from sql_hints.lib.checkers import all as all_checkers


def check_string(raw: str) -> typing.List[checker.Remark]:
    opts = manager.Options([manager.CheckerMatcher('.*')])
    return manager.check_raw_string(
        'filepath', opts, all_checkers.get_all_checkers(), raw,
    )
