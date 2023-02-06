import logging
import os.path
import subprocess
import sys

import pytest

from taxi_stq import _runner

logger = logging.getLogger(__name__)


@pytest.mark.filldb(_fill=False)
def test_check_imports():
    import taxi.core.db  # noqa
    with pytest.raises(_runner.ForbiddenImportError):
        _runner._check_imports(logger)


@pytest.mark.filldb(_fill=False)
def test_stq_runner(patch):
    env = os.environ.copy()
    env['PYTHONPATH'] = ':'.join(sys.path)
    subprocess.check_output(
        [sys.executable, '-m', _runner.__name__, '--check-only'], env=env,
    )
