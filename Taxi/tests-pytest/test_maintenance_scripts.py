import os
import os.path
import re

import pytest

from taxi_maintenance import run
from taxi_maintenance import stuff

MODNAME_RE = re.compile(r'^[a-z_][0-9a-z_]*$', re.IGNORECASE)


def _get_staff_module_names():
    result = []
    maintenance_dir = os.path.dirname(stuff.__file__)
    for name in os.listdir(maintenance_dir):
        modname, ext = os.path.splitext(name)
        if (ext not in ('.py', '') or
            not MODNAME_RE.match(modname) or
            modname == '__init__'
        ):
            continue

        if (os.path.isdir(os.path.join(maintenance_dir, name)) and
            ext == '' and
            os.path.isfile(
                os.path.join(maintenance_dir, name, '__init__.py')
            )
        ):
            task_module_name = '%s.main' % modname
        else:
            task_module_name = modname
        result.append(task_module_name)
    return result


@pytest.mark.parametrize('name', _get_staff_module_names())
@pytest.mark.filldb(_fill=False)
@pytest.mark.asyncenv('blocking')
def test_maintenance_scripts(name):
    command = run.StuffCommand(name)
    assert command.lock_time > 0
