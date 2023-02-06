#!/usr/bin/taxi-python3

import requests
import socket


def report(
    clowny_search_fqdn: str,
    program_name: str,
    program_version: str,
    fqdn: str,
) -> None:
    url = f'http://{clowny_search_fqdn}/v1/packages/report-version'

    response = requests.put(
        url,
        params={
            'package_name': program_name,
            'fqdn': fqdn,
        },
        json={
            'package_version': program_version,
        }
    )
    response.raise_for_status()

    print(
        f'The sidecar version ({program_name}={program_version}) '
        f'at "{fqdn}" '
        f'has been successfully reported to {clowny_search_fqdn}'
    )


def get_clowny_search_fqdn() -> str:
    try:
        with open('/etc/yandex/environment.type', 'r') as ifile:
            environment = ifile.read().strip()
            if environment == 'production':
                return 'clowny-search.taxi.yandex.net'
    except Exception:
        pass

    return 'clowny-search.taxi.tst.yandex.net'


def main():
    report(
        clowny_search_fqdn=get_clowny_search_fqdn(),
        program_name='second-unit',
        program_version='0.0.12testing37243',
        fqdn=socket.gethostname(),
    )


if __name__ == '__main__':
    main()
