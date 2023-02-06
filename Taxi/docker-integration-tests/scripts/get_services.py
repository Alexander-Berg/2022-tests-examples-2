#!/usr/bin/env python3
import argparse
import os
import subprocess
import sys

import utils


DOCKER_COMPOSE = 'docker-compose.yml'
REGISTRY = 'registry.yandex.net'
PLATFORM_SUBST = '${PLATFORM:-xenial}'
ENTITIES_DIRS = ('services' + os.sep, 'libraries' + os.sep)


def substitute_envvar(line: str) -> str:
    return subprocess.check_output(
        ['bash', '-c', 'eval echo -n "%s"' % line],
    ).decode('utf-8')


def prepare_image(image: str) -> str:
    image = substitute_envvar(image)
    if ':' not in image:
        image += ':latest'
    return image


def _find_dependencies(service_name, all_services, services_to_load_by_name):
    if service_name in services_to_load_by_name:
        return

    service = all_services[service_name]
    services_to_load_by_name[service_name] = service

    for dep_service_name in service.get('depends_on', []):
        _find_dependencies(
            dep_service_name, all_services, services_to_load_by_name,
        )

    extends_service = service.get('extends', {}).get('service')
    if extends_service:
        _find_dependencies(
            extends_service, all_services, services_to_load_by_name,
        )


def load_services_recursively(service_name, docker_compose_files=None):
    all_services = load_services(docker_compose_files=docker_compose_files)

    services_to_load_by_name = {}
    _find_dependencies(service_name, all_services, services_to_load_by_name)

    return services_to_load_by_name


def load_services(docker_compose_files=(DOCKER_COMPOSE,)):
    services = {}
    for file in docker_compose_files:
        yml = utils.load_yaml(file)
        if 'services' in yml:
            services.update(yml['services'])

    return services


def iter_images(services, prefix='', platform=''):
    for name, params in services.items():
        image = params.get('image')
        if not image or not image.startswith(REGISTRY + prefix):
            continue

        if platform and platform not in image and PLATFORM_SUBST not in image:
            continue

        yield name, params


def get_prefixed_service_name(project: str) -> str:
    service_name = _remove_entity_prefix(project)
    if service_name.startswith('taxi') or service_name.startswith('eats'):
        return service_name
    return 'taxi-%s' % service_name


def _remove_entity_prefix(name: str) -> str:
    for entity_dir in ENTITIES_DIRS:
        if name.startswith(entity_dir):
            return name[len(entity_dir) :]
    return name


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'docker_compose',
        default=[DOCKER_COMPOSE],
        type=str,
        nargs='*',
        metavar='DOCKER_FILE',
        help='Path to docker-compose.yml to be processed',
    )
    parser.add_argument(
        '--service',
        default='',
        help='If provided - return image string instead of services list',
    )
    parser.add_argument(
        '--platform', default='', help='Target platform (xenial/bionic)',
    )
    parser.add_argument(
        '--prefix',
        default='',
        help='Target prefix (/taxi/taxi-integration/ for example)',
    )
    parser.add_argument('--images', action='store_true', help='Show images')
    args = parser.parse_args()

    services = load_services(args.docker_compose)

    result = []

    if args.service:
        if args.service not in services:
            print(
                'Service',
                args.service,
                'not found in integration tests',
                file=sys.stderr,
            )
            exit(1)
        result.append(prepare_image(services[args.service]['image']))
    elif args.images:
        for name, params in iter_images(services, args.prefix, args.platform):
            result.append(prepare_image(params['image']))
    else:
        for name, params in iter_images(services, args.prefix, args.platform):
            result.append(name)

    print('\n'.join(result))


if __name__ == '__main__':
    main()
