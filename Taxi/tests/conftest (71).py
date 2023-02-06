import os.path
import pathlib
import sys

ROOT_PATH = pathlib.Path(__file__).parent.parent
TESTSUITE_PATH = ROOT_PATH / '..' / '..' / 'submodules' / 'testsuite'

sys.path.append(str(TESTSUITE_PATH))
sys.path.append(str(ROOT_PATH))


pytest_plugins = ['taxi_testsuite.plugins.profiling_junitxml']


def pytest_addoption(parser):
    parser.addoption(
        '--tests-dir',
        default=os.path.normpath(
            os.path.join(os.path.dirname(__file__), '..', '..'),
        ),
        help='Path to tests-pytest directory.',
    )
