import os.path
import sys


def pytest_addoption(parser):
    parser.addoption(
        '--tests-dir',
        default=os.path.normpath(
            os.path.join(os.path.dirname(__file__), '..'),
        ),
        help='Path to tests-pytest directory.',
    )
    parser.addoption(
        '--yt-upload-settings',
        nargs='*',
        help='Paths to directories containing settings for yt upload.',
    )


def pytest_configure(config):
    tests_dir = config.getoption('--tests-dir')
    sys.path.extend(
        [
            os.path.join(tests_dir, os.pardir, 'tools'),
            os.path.join(tests_dir, os.pardir, 'uploads', 'lib'),
        ],
    )
