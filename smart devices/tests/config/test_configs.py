import json
import os.path
from collections import defaultdict

from sandbox.projects.quasar.platform import (
    Platform,
    ANDROID_PLATFORMS,
    TV_PLATFORMS,
    get_effective_revisions,
    get_platform_path_key,
)

import yatest.common as yc
import pytest


def config_paths():
    blacklist = {
        Platform.X86_64,
        *TV_PLATFORMS,
        Platform.CENTAUR,
        Platform.WK7Y,
        Platform.LIGHTCOMM,
        Platform.YANDEXMODULE,
        Platform.PLUTO,
        Platform.LINKPLAY_A98,
        Platform.ELARI_A98,
        Platform.PRESTIGIO_SMART_MATE,
    }
    res = {}
    for platform in list(Platform):
        if platform in blacklist:
            continue
        for revision in get_effective_revisions(platform):
            path_key = get_platform_path_key(platform, revision)
            res_key = path_key.replace('/', '_')
            if platform in ANDROID_PLATFORMS:
                res[res_key] = [
                    "smart_devices/platforms/{}/config/quasar-dev.cfg".format(path_key),
                    "smart_devices/platforms/{}/config/quasar-prod.cfg".format(path_key),
                ]
            elif platform in {Platform.JBL_LINK_MUSIC, Platform.JBL_LINK_PORTABLE}:
                res[res_key] = "smart_devices/platforms/{}/config/quasar.cfg".format(path_key).replace(
                    "jbl_link_", "jbl_link/"
                )
            else:
                res[res_key] = "smart_devices/platforms/{}/config/quasar.cfg".format(path_key)
    res["functional_tests"] = "yandex_io/functional_tests/data_common/quasar.cfg"
    res["sample_app_android"] = "yandex_io/sample_app/android/config/quasar.cfg"
    res["sample_app_linux"] = "yandex_io/sample_app/linux/config/quasar.cfg"
    res["android_sdk"] = "yandex_io/android_sdk/config/quasar.cfg"
    res["services-iosdk-tv"] = "smart_devices/android/tv/services/services-iosdk-app/config/tv/quasar.cfg"
    res["services-iosdk-module2"] = "smart_devices/android/tv/services/services-iosdk-app/config/module2/quasar.cfg"
    res["centaur-app"] = "smart_devices/android/centaur-app/config/quasar.cfg"
    return res


def map_config_paths(platform, func):
    paths = CONFIG_PATHS[platform]
    assert isinstance(paths, (str, list))

    if isinstance(paths, str):
        return func(paths)
    else:  # list
        return [func(x) for x in paths]


CONFIG_PATHS = config_paths()


@pytest.mark.parametrize('platform', sorted(CONFIG_PATHS))
def test_config_canonization(platform):
    """Canonize all compiled configs.

    Final config files are canonized inside Arcadia to review changes in base configs.
    """
    return map_config_paths(platform, lambda x: yc.canonical_file(yc.build_path(x), local=True))


@pytest.mark.parametrize('platform', sorted(CONFIG_PATHS))
def test_config_unique_ports(platform):
    """Check that all values that look like port numbers are unique.

    Port conflicts generally cause inability to start and must be avoided.
    Since there is no way to determine if a certain value is actually a port number,
    some heuristics are applied: a value is assumed to be a port number if its key
    looks like it corresponds to a port and if the value itself is an integer or
    a string containing an integer.

    """

    def check_file(path):
        with open(yc.build_path(path), 'r') as f:
            config = json.loads(f.read())
        return check_unique_ports(config, os.path.basename(path))

    map_config_paths(platform, check_file)


def check_unique_ports(config, name):
    used_ports = defaultdict(set)
    for path, value in iter_json_leaf_values(config, prefix=(name,)):
        # Assume that all such keys look like "port", "foo_port" or "fooPort"
        if not path[-1].lower().endswith('port'):
            # key does not look like it specifies a port
            continue

        # NB: False positive keys should be skipped at this point, if any

        if isinstance(value, str) and value.isdigit():
            value = int(value)
        if not isinstance(value, int):
            # value does not look like a port number
            continue

        used_ports[value].add(' / '.join(path))

    messages = []
    for port, paths in used_ports.items():
        if len(paths) > 1:
            messages += [f'port {port}:']
            messages += [f'- {path} = {port}' for path in paths]

    if messages:
        messages += ['Unique ports:']
        messages += [
            f'- {path} = {port}' for port, paths in sorted(used_ports.items()) if len(paths) == 1 for path in paths
        ]

    ports_are_unique = len(messages) == 0
    assert ports_are_unique, 'Possible port conflicts are detected:\n' + '\n'.join(messages)


def iter_json_leaf_values(value, prefix=()):
    if isinstance(value, list):
        for idx, item in enumerate(value):
            yield from iter_json_leaf_values(item, prefix + (f'[{idx}]',))
    elif isinstance(value, dict):
        for key, item in value.items():
            yield from iter_json_leaf_values(item, prefix + (key,))
    else:
        yield prefix, value
