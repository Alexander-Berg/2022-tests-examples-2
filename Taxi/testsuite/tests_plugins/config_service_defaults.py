import json
import pathlib

import pytest

try:
    import library.python.resource
    IS_ARCADIA = True
except ImportError:
    IS_ARCADIA = False


CHECK_CONFIG_ERROR = (
    'Your are trying to override config value using '
    '@pytest.mark.config({}) '
    'that does not seem to be used by your service.\n\n'
    'In case you really need to disable this check please add the '
    'following mark to your testcase:\n\n'
    '@pytest.mark.disable_config_check'
)


class UnknownConfigError(RuntimeError):
    pass


def pytest_configure(config):
    config.addinivalue_line(
        'markers', 'disable_config_check: disable config mark keys check',
    )


@pytest.fixture(name='config_service_defaults', scope='session')
def _config_service_defaults(service_build_dir: pathlib.Path):
    if IS_ARCADIA:
        return json.loads(
            library.python.resource.find(  # pylint: disable=no-member
                'testsuite:taxi_config_fallback.json',
            ),
        )
    path = service_build_dir / 'taxi_config_fallback.json'
    if path.exists():
        with open(path, 'r', encoding='utf-8') as file:
            return json.load(file)
    return {}


@pytest.fixture(autouse=True)
def check_config_marks(request, config_service_defaults):
    if request.node.get_closest_marker('disable_config_check'):
        return
    unknown_configs = set()
    for marker in request.node.iter_markers('config'):
        for key in marker.kwargs:
            if key not in config_service_defaults:
                unknown_configs.add(key)
    if unknown_configs:
        # TODO: get rid of warnings then turn into exception
        message = CHECK_CONFIG_ERROR.format(
            ', '.join(f'{key}=...' for key in sorted(unknown_configs)),
        )
        raise UnknownConfigError(message)
