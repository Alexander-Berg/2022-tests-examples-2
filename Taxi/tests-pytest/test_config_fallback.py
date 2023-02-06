import pytest

from taxi import config
from taxi.config import configs
from taxi.config import exceptions


@pytest.mark.parametrize('varname', config.all_names)
@pytest.mark.filldb(_fill=False)
@pytest.mark.asyncenv('blocking')
def test_config_params(varname):
    if varname.startswith('_'):
        return
    assert varname.isupper()
    value = getattr(configs, varname)
    try:
        value.validate(value.default)
    except exceptions.ValidationError as exc:
        pytest.fail('%s: %s' % (varname, str(exc)))
