import os
import csv

from collections import namedtuple


def pytest_addoption(parser):
    """
    fields in the data.csv should be:

    Category,Security Level,Test Case,Platform Type,Expected Result,License URL,Content URL,Actual Results,Test Status
    """
    parser.addoption(
        "--wv_cases",
        action="store",
        default='data.csv',
        help="Path to csv file with WV test data",
    )

    parser.addoption(
        "--exoplayer_demo",
        action="store",
        default='exoplayer_demo.apk',
        help="Path to apk to install to the device",
    )


WVCase = namedtuple('WVCase', ['name', 'expected', 'license_url', 'content_url'])


def read_cases(option):
    with open(os.path.abspath(option), newline='') as csv_file:
        return [
            WVCase(
                name=row['Test Case'],
                expected=row['Expected Result'],
                license_url=row['License URL'],
                content_url=row['Content URL'],
            )
            for row in csv.DictReader(csv_file)
        ]


def pytest_generate_tests(metafunc):
    if "wv_case" in metafunc.fixturenames:
        cases = read_cases(metafunc.config.getoption("wv_cases"))
        metafunc.parametrize("wv_case", cases, ids=[c.name for c in cases])
