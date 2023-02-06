#!/usr/bin/env python3.7
import argparse
import os
import pathlib
import re
import subprocess
import typing

import get_services

ROOT_DIR = pathlib.Path(__file__).parent.parent
INT_IMAGE_PAT = re.compile(
    r'(^registry.yandex.net/(?:taxi|eda)/.*):\$\{.*:?-test\}$',
)
SERVICES_DIR = 'services' + os.sep
BASE_IMG_TMP = 'taxi-integration-%s-base'


def get_source_code_services() -> typing.List[str]:
    services = []
    if (ROOT_DIR / 'backend' / 'debian' / 'changelog').exists():
        services.append('taxi-backend')
    if (ROOT_DIR / 'eats-core' / 'debian' / 'changelog').exists():
        services.append('eats-core')
    # TODO(aselutin): remove this loop in TAXITOOLS-4167
    for config in ROOT_DIR.glob(
            'backend-cpp/build-integration/testsuite/services/*.service',
    ):
        name = form_taxi_service(config.stem)
        if name in ('taxi-pickuppoints', 'taxi-driver-dispatcher'):
            continue
        services.append(name)
    for config in ROOT_DIR.glob(
            '../../../build-dir/testsuite/services/*.service',
    ):
        name = form_taxi_service(config.stem)
        if name in ('taxi-pickuppoints', 'taxi-driver-dispatcher'):
            continue
        services.append(name)

    changed_python_services = get_changed_python_services()
    excess_services = {
        'taxi-protocol',  # intersect with backend-cpp
        'taxi-antifraud',  # intersect with backend-cpp
        'taxi-replication',  # remove in TAXITOOLS-2239
    }
    changed_python_services -= excess_services
    services.extend(list(changed_python_services))

    # TODO(aselutin): remove hacks in TAXITOOLS-3416
    for service in ROOT_DIR.glob('../../../build-dir/services/*'):
        name = form_taxi_service(service.name)
        services.append(name)

    # TODO(itrofimow): remove hacks in TAXITOOLS-3416
    # for service in ROOT_DIR.glob('uservices/bionic-build/services/*'):
    #    name = form_taxi_service(service.name)
    #    services.append(name)

    return services


def get_changed_python_services() -> typing.Set[str]:
    if not os.path.exists('backend-py3/Makefile'):
        return set()

    env_changed_projects = os.getenv('CHANGED_PROJECTS', '')
    if env_changed_projects:
        return gather_changed_services(env_changed_projects)
    return get_all_python_services()


def gather_changed_services(env_changed_projects: str) -> typing.Set[str]:
    changed_services: typing.Set[str] = set()

    for project in env_changed_projects.split():
        if project.startswith(SERVICES_DIR):
            service_name = project[len(SERVICES_DIR) :]
            changed_services.add(form_taxi_service(service_name))
    return changed_services


def get_all_python_services() -> typing.Set[str]:
    services: typing.Set[str] = set()
    for service_path in ROOT_DIR.glob('backend-py3/services/*/'):
        if any(service_path.glob('*/generated')):
            services.add(form_taxi_service(service_path.name))

    return services


def form_taxi_service(service: str) -> str:
    if service.startswith('taxi'):
        return service
    return 'taxi-' + service


def get_base_image(services: dict) -> str:
    platform = os.getenv('PLATFORM', 'xenial')
    dc_service_name = BASE_IMG_TMP % platform
    return get_services.prepare_image(services[dc_service_name]['image'])


def is_image_exist(image: str) -> bool:
    check_result = subprocess.run(
        ['docker', 'images', '-q', image], capture_output=True,
    )
    return bool(check_result.stdout)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'docker_compose',
        default=None,
        type=str,
        nargs='*',
        metavar='DOCKER_FILE',
        help='Path to docker-compose.yml to be processed',
    )
    args = parser.parse_args()

    source_code_services = get_source_code_services()
    services = get_services.load_services(args.docker_compose)
    base_image = get_base_image(services)
    for service, params in get_services.iter_images(services):
        image = params['image']
        match = INT_IMAGE_PAT.match(image)
        if not match:
            continue
        image = match.group(1)
        orig_image = image + ':latest'
        test_image = image + ':test'
        if service in source_code_services:
            if service == 'eats-core':
                print('eats-core was build from source')
                continue
            orig_image = base_image

        if not is_image_exist(orig_image):
            continue
        subprocess.run(['docker', 'tag', orig_image, test_image], check=True)


if __name__ == '__main__':
    main()
