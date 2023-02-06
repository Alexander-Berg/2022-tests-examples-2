import os
import pytest


def test_device_config():
    from signalq_pyml import get_engine
    from signalq_pyml import get_profile

    directory, _ = os.path.split(os.path.abspath(__file__))

    path = os.path.join(
        directory, 'static', 'test_config', 'device_config.conf',
    )

    assert get_engine(config_path=path) == 'yandex'
    assert get_profile(config_path=path) is None


def test_available_profiles():
    import glob
    from signalq_pyml import builtin_config_path
    from signalq_pyml import profiles

    glob_string = os.path.join(builtin_config_path, '*')
    available = [os.path.split(p)[1] for p in glob.glob(glob_string)]

    for p in profiles:
        assert p in available


@pytest.mark.skip(reason='conflicts with other tests')
def test_unversioned_config(load_json, get_pytest_signalq_config):
    import signalq_pyml

    from signalq_pyml import builtin_config_path
    from signalq_pyml import builtin_config_fstring
    from signalq_pyml import device_config_fstring
    from signalq_pyml import device_config_path

    from signalq_pyml import processors
    from signalq_pyml.core import logging

    directory, _ = os.path.split(os.path.abspath(__file__))
    statics = os.path.join(directory, 'static', 'test_config')

    signalq_pyml.device_config_file = os.path.join(
        statics, 'device_config.conf',
    )
    signalq_pyml.device_config_path = builtin_config_path
    signalq_pyml.device_config_fstring = builtin_config_fstring

    ml_config_path = os.path.join(statics, 'unversioned.json')
    processor = processors.Runner.from_config_file(ml_config_path)

    # patching this device specific thing back
    logging.patch_logging_names_upper()
    processors.Runner.pack_face_info = processors.node.pack_face_info_builtin
    signalq_pyml.device_config_path = device_config_path
    signalq_pyml.device_config_fstring = device_config_fstring
    assert processor.with_fallback


def test_device_config_path():
    from signalq_pyml import device_config_fstring
    from signalq_pyml import device_config_path
    from signalq_pyml import get_config_path

    config_path = get_config_path(
        mode='car',
        cv='yandex',
        config_path=device_config_path,
        config_fstring=device_config_fstring,
    )

    assert config_path == '/etc/signalq/profiles/car/analytics_yandex.json'
