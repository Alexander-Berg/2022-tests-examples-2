import json
import os

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from pilorama_plugins import *  # noqa: F403 F401
import pytest
import yaml


USERVER_CONFIG_HOOKS = ['patch_pilorama_config']
PILORAMA_CONFIG_FNAME = 'pilorama_config.yaml'
PILORAMA_CUSTOM_CONFIGS_DIR = 'pilorama_custom_conf_dir'
SERVICE_LOGS_FNAME = 'pilorama_service_logs.log'
TEMP_SERVICE_LOGS_FNAME = 'temp_pilorama_service_logs.log'
SINCEDB_FNAME = 'pilorama.sincedb'


@pytest.fixture(scope='session')
def patch_pilorama_config(worker_id, testsuite_build_dir):
    def patch_config(config, config_vars):
        config_path = testsuite_build_dir / PILORAMA_CONFIG_FNAME
        sincedb_path = testsuite_build_dir / SINCEDB_FNAME

        if sincedb_path.exists():
            sincedb_path.unlink()

        with config_path.open('w') as outfile:
            yaml.dump(
                [
                    {
                        'file': {
                            'path': 'stub',
                            'sincedb_path': str(sincedb_path),
                        },
                        'filter': {},
                        'output': {'hosts': ['stub'], 'index': 'stub'},
                    },
                ],
                outfile,
            )

        config_vars['pilorama_rules'] = str(config_path)

        custom_configs_dir = testsuite_build_dir / PILORAMA_CUSTOM_CONFIGS_DIR
        if custom_configs_dir.exists():
            custom_configs_dir.rmdir()

        config_vars['pilorama_custom_rules'] = str(custom_configs_dir)

    return patch_config


@pytest.fixture
def fill_pilorama_config(load_json, testsuite_build_dir):
    def _impl(fname):
        sincedb_path = testsuite_build_dir / SINCEDB_FNAME
        service_logs_path = testsuite_build_dir / SERVICE_LOGS_FNAME

        config_entry = load_json(fname)
        config_entry['file']['path'] = str(service_logs_path)
        config_entry['file']['sincedb_path'] = str(sincedb_path)

        with (testsuite_build_dir / PILORAMA_CONFIG_FNAME).open(
                'w',
        ) as outfile:
            yaml.dump([config_entry], outfile)

    return _impl


@pytest.fixture
def fill_service_logs(load, testsuite_build_dir):
    def _impl(service_logs_fname):
        with open(
                testsuite_build_dir / TEMP_SERVICE_LOGS_FNAME, 'w',
        ) as outfile:
            outfile.write(load(service_logs_fname))

        os.replace(
            testsuite_build_dir / TEMP_SERVICE_LOGS_FNAME,
            testsuite_build_dir / SERVICE_LOGS_FNAME,
        )

    return _impl


@pytest.fixture
def check_bulk_request(load):
    def _impl(request, expected_fname):
        data = [
            json.loads(line)
            for line in request.get_data().decode('utf-8').splitlines()
        ]
        exp_data = [
            json.loads(line) for line in load(expected_fname).splitlines()
        ]

        assert len(data) == len(exp_data)

        for item, exp_item in zip(data, exp_data):
            for key, exp_value in exp_item.items():
                assert item[key] == exp_value

    return _impl


@pytest.fixture(autouse=True)
async def setup_pilorama(taxi_pilorama, testsuite_build_dir):
    sincedb_path = testsuite_build_dir / SINCEDB_FNAME
    if sincedb_path.exists():
        sincedb_path.unlink()

    service_logs_path = testsuite_build_dir / SERVICE_LOGS_FNAME
    if service_logs_path.exists():
        service_logs_path.unlink()

    yield

    await taxi_pilorama.run_task('pilorama/stop')
