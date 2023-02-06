import collections
import os.path
import typing

# Service config descriptor
ServiceConfig = collections.namedtuple(
    'ServiceConfig', [
        'binary',
        'config',
        'source_dir',
        'secdist_dev',
        'output_secdist_path',
        'secdist_template',
    ],
)

_SERVICE_CONFIG_CACHE: typing.Dict[str, ServiceConfig] = {}


def load_path(path):
    if path not in _SERVICE_CONFIG_CACHE:
        service_vars = {}
        with open(path) as fp:
            for line in fp:
                key, value = line.strip().split('=', 1)
                service_vars[key] = value

        _SERVICE_CONFIG_CACHE[path] = ServiceConfig(
            binary=service_vars['BINARY'],
            config=service_vars['CONFIG'],
            source_dir=service_vars['SOURCE_DIR'],
            secdist_dev=service_vars['SECDIST_DEV'],
            output_secdist_path=service_vars['OUTPUT_SECDIST_PATH'],
            secdist_template=service_vars['SECDIST_TEMPLATE'],
        )
    return _SERVICE_CONFIG_CACHE[path]


def service_config(service_name, build_dir):
    service_path = os.path.abspath(
        os.path.join(
            build_dir,
            'testsuite/services/%s.service' % service_name,
        ),
    )
    return load_path(service_path)
