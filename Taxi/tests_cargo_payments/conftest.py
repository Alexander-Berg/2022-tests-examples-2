# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import pytest

from cargo_payments_plugins import *  # noqa: F403 F401


@pytest.fixture(name='load_json_var')
def _load_json_var(load_json):
    def load_json_var(path, **variables):
        def var_hook(obj):
            varname = obj['$var']
            return variables[varname]

        return load_json(path, object_hook={'$var': var_hook})

    return load_json_var
