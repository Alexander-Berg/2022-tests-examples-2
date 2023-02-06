import importlib

import pytest

from taxi.conf import core_settings


@pytest.mark.parametrize(
    'queue,worker', core_settings.STQ_WORKERS.items())
@pytest.mark.filldb(_fill=False)
@pytest.mark.asyncenv('blocking')
def test_new_stq_modules(queue, worker):
    modname, funcname = worker['task_function'].rsplit('.', 1)
    module = importlib.import_module(modname)
    assert hasattr(module, funcname)
