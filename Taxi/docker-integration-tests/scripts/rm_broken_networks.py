#!/usr/bin/env python3
import json
import subprocess


def main():
    delete_containers()
    networks = get_networks()
    for network in networks:
        fix_network_if_broken(network)


def delete_containers():
    containers = subprocess.check_output(
        ['docker-compose', 'ps', '-q'],
        encoding='utf-8',
    )
    if not containers:
        return

    for container in containers.strip().split('\n'):
        subprocess.run(
            ['docker', 'rm', '-f', '-v', container],
        )


def get_networks():
    whitelist = ['host', 'bridge', 'none']
    networks = subprocess.check_output(
        ['docker', 'network', 'ls', '--format', '{{.Name}}'],
        encoding='utf-8',
    )
    if not networks:
        return []

    return [
        network for network in networks.strip().split('\n')
        if network not in whitelist
    ]


def fix_network_if_broken(network_name):
    network = docker_inspect(network_name, 'network')
    if not network:
        return
    broken = False

    for container_id, container_data in network['Containers'].items():
        if docker_inspect(container_id, 'container') is None:
            broken = True
            subprocess.run(
                ['docker', 'network', 'disconnect', '-f',
                 network_name, container_data['Name']],
            )
    if broken:
        subprocess.run(
            ['docker', 'network', 'rm', network_name],
        )


def docker_inspect(object_name, object_type):
    proc = subprocess.run(
        ['docker', object_type, 'inspect', object_name],
        stdout=subprocess.PIPE,
        encoding='utf-8',
    )
    if proc.returncode != 0:
        return None
    return json.loads(proc.stdout)[0]


if __name__ == '__main__':
    main()
