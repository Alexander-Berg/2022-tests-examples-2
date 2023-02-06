import argparse

from dmp_suite import datetime_utils as dtu

from dmp_suite.greenplum.hnhm.transformation import HybridLoadGenerator
from dmp_suite.greenplum.task.hnhm import HybridLoadGeneratorTask


class MockGenerator(HybridLoadGenerator):
    def __init__(self) -> None:
        self.start_date = None
        self._targets = {}

    def run(self, start_date=None):
        self.start_date = start_date


def test_arg_in_hybrid_load_generator_task():
    generator = MockGenerator()
    task = HybridLoadGeneratorTask('test', generator)

    args = argparse.Namespace()
    args.start_date = None
    task._run_task(args)
    assert generator.start_date is None

    start_date = dtu.parse_datetime('2020-01-01')
    args.start_date = start_date
    task._run_task(args)
    assert generator.start_date == start_date
