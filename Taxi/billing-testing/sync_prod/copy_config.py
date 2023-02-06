# coding: utf8

from importlib import util
import inspect
import logging
import os
import subprocess
from typing import List
from typing import Set

import yaml

logger = logging.getLogger(__name__)


def copy_prod_config(
        config_filename: str,
        backend_services: List[str],
        backend_path: str,
        uservices: List[str],
        uservices_path: str,
        skip_configs: List[str],
) -> bool:
    configs_set = _get_services_configs(backend_services, backend_path).union(
        _get_services_configs(uservices, uservices_path),
    )
    for config in skip_configs:
        configs_set.discard(config)
    configs_dict = {}
    count = 0
    error_count = 0
    logger.info(f'requesting {len(configs_set)} configs values...')
    for config_name in configs_set:
        proc = subprocess.run(
            ['taxi-config', 'get', config_name],
            stdout=subprocess.PIPE,
            encoding='utf-8',
        )
        if proc.returncode == 0:
            configs_dict[config_name] = yaml.load(
                proc.stdout.strip(), Loader=yaml.Loader,
            )
            count = count + 1
        else:
            logger.info(f'can\'t get value for {config_name}')
            error_count = error_count + 1
    logger.info(f'saving {count} configs ({error_count} errors)...')

    with open(file=config_filename, mode='w', encoding='utf-8') as stream:
        dumped = yaml.dump({'configs': configs_dict}, default_flow_style=False)
        stream.write(dumped)
    return True


def _get_services_configs(services: List[str], path: str) -> Set[str]:
    configs_set: Set[str] = set()
    for service_name in services:
        service_path = os.path.abspath(
            os.path.join(os.path.join(path, 'services'), service_name),
        )
        configs_set = configs_set.union(
            _get_service_configs(service_path, service_name),
        )
    return configs_set


def _get_service_configs(service_path: str, service_name: str) -> Set[str]:
    service_yaml_path = os.path.join(service_path, 'service.yaml')
    configs_set: Set[str] = set()
    if os.path.isfile(service_yaml_path):
        with open(
                file=service_yaml_path, mode='r', encoding='utf-8',
        ) as stream:
            service_config = yaml.load(stream, Loader=yaml.Loader)
            configs = service_config.get('config')
            if not configs:
                configs = service_config.get('configs', {}).get('names')
            if configs:
                logger.info(
                    f'{service_name}: getting config from service.yaml',
                )
                for config in configs:
                    configs_set.add(config)
            else:
                service_folder = service_name.replace('-', '_')
                config_py_path = os.path.join(
                    os.path.join(service_path, service_folder), 'config.py',
                )
                if os.path.isfile(config_py_path):
                    logger.info(f'{service_name}: parsing config.py')

                    spec = util.spec_from_file_location(
                        service_folder, config_py_path,
                    )
                    loader = spec.loader
                    assert loader
                    config_module = util.module_from_spec(spec)
                    loader.exec_module(config_module)  # type: ignore
                    config_class = config_module.Config  # type: ignore
                    configs_set = {
                        field[0]
                        for field in inspect.getmembers(
                            config_class,
                            lambda a: (
                                not inspect.isroutine(a)
                                and not inspect.isbuiltin(a)
                            ),
                        )
                        if not field[0].startswith('_')
                        and field[0] not in ['cache_loaded', 'task_name']
                    }
                else:
                    logger.info(
                        f'{service_name}: config not found in service.yaml'
                        'and config.py doesn\'t exist',
                    )
    logger.info(f'{len(configs_set)} configs found')
    return configs_set
