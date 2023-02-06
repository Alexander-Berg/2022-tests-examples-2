from dmp_suite.maintenance.checks.reporter import CheckResult, CheckResultStat, ResultStatuses
from dmp_suite.maintenance.checks.base_check import BaseCheck


class FakeCheck(BaseCheck):
    @classmethod
    def add_arguments(cls, parser):
        parser.add_argument('--errors_total', type=int, required=True)
        parser.add_argument('--errors_new', type=int)
        return parser

    def run(self):
        return [CheckResult('test', errors_total=self.options['errors_total'], errors_new=self.options['errors_new'],
                            description='', tags=[])]


def get_stat(error_total, errors_new):
    argv = FakeCheck.parse_args(['--errors_total', str(error_total), '--errors_new', str(errors_new)])
    check = FakeCheck(vars(argv))
    return CheckResultStat(check, check.run())


def test_parse_check_argv():
    args = FakeCheck.parse_args(['--errors_total', '10'])
    assert args.errors_total == 10


def test_check_argv_to_options():
    check = FakeCheck(vars(FakeCheck.parse_args(['--errors_total', '10', '--errors_new', '5'])))
    assert check.options['errors_total'] == 10
    assert check.options['errors_new'] == 5


def test_result_of_fake_check():
    check = FakeCheck(vars(FakeCheck.parse_args(['--errors_total', '10', '--errors_new', '5'])))
    result = list(check.run())[0]
    assert result.errors_total == 10
    assert result.errors_new == 5


def test_star_result_status():
    assert get_stat(0, 0).result_status == ResultStatuses.OK
    assert get_stat(10, 0).result_status == ResultStatuses.ERRORS_OLD
    assert get_stat(10, 5).result_status == ResultStatuses.ERRORS_NEW
