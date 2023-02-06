# coding: utf-8

from __future__ import print_function
import pytest

def pytest_addoption(parser):
    group = parser.getgroup("terminal reporting")
    group._addoption('--output_file', type=str, help="Save to file the pytest session information")

def pytest_configure(config):
    pytest.output_file = config.getoption('output_file')


def pytest_terminal_summary(terminalreporter):
    if pytest.output_file:
        with open(pytest.output_file, 'w') as f:
            for rep in terminalreporter.stats.get('passed', []) + terminalreporter.stats.get('failed', []):
                    print('\t'.join([rep.nodeid, rep.outcome, rep.longreprtext]), file=f)
