import json
import os
from typing import Iterator
from typing import List

import yatest.common  # pylint: disable=import-error


CURRENT_DIRECTORY = os.path.dirname(__file__)
DIRNAME = os.path.join(
    CURRENT_DIRECTORY, 'static', 'test_collected_rules', 'files', 'services',
)


def list_services() -> Iterator[str]:
    for service in os.listdir(DIRNAME):
        if os.path.isdir(os.path.join(DIRNAME, service)):
            yield service


def collect_rules(service: str) -> List[dict]:
    rules = []
    dirname = os.path.join(DIRNAME, service)
    filepaths = []
    for dirpath, _, filenames in os.walk(dirname):
        for filename in filenames:
            if filename == 'collected-rules.json':
                filepaths.append(os.path.join(dirpath, filename))

    for filepath in sorted(filepaths):
        with open(filepath, 'r') as ifile:
            contents = json.load(ifile)
            rules.extend(contents)
    return rules


async def fetch_metas(
        proxy: str, rules: List[dict], taxi_authproxy_manager, taxi_config,
) -> List[dict]:
    metas = []

    print(f'Import [', flush=True, end='')

    for rule in rules:
        metas.append(
            {
                'rule': rule,
                'meta': await fetch_meta(
                    proxy, rule, taxi_authproxy_manager, taxi_config,
                ),
            },
        )

    # Finish the line with dots
    print(']')

    return metas


async def fetch_meta(
        proxy: str, rule: dict, taxi_authproxy_manager, taxi_config,
) -> dict:
    dev_teams = taxi_config.get('AUTHPROXY_MANAGER_DEFAULT_DEV_TEAM_BY_PROXY')
    put_params = {
        'proxy': proxy,
        'rule-name': rule['input']['rule_name'],
        'maintained-by': dev_teams[proxy],
    }
    response = await taxi_authproxy_manager.put(
        f'/v1/rules/by-name/',
        json=rule,
        headers={'content-type': 'application/json'},
        params=put_params,
    )
    response.raise_for_status()

    response = await taxi_authproxy_manager.post(
        f'/v1/rules/meta',
        headers={'content-type': 'application/json'},
        params={'proxy': proxy},
        json={'rule_names': [rule['input']['rule_name']]},
    )
    response.raise_for_status()

    meta = response.json()['rule_metas'][0]['headers_info']

    response = await taxi_authproxy_manager.delete(
        f'/v1/rules/by-name/',
        headers={'content-type': 'application/json'},
        params=put_params,
    )
    response.raise_for_status()

    # show the progress
    print('.', flush=True, end='')

    return meta


def process_metas(service: str, metas: List[dict]):
    filepath = os.path.join(
        DIRNAME, service, 'testsuite', 'static', 'meta_headers_cache.json',
    )

    if yatest.common.get_param('am_copy_mode'):
        print(f'Updating file {filepath}...')
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as ofile:
            json.dump(
                metas, ofile, indent=2, sort_keys=True, ensure_ascii=False,
            )
            ofile.write('\n')
    else:
        with open(filepath, 'r') as ifile:
            contents = json.load(ifile)
        assert (
            metas == contents
        ), f'"{filepath} contents differ from the a-m\'s output of {service}\'s rules'


async def test_meta_uptodate(
        load_json, taxi_authproxy_manager, testpoint, mockserver, taxi_config,
):
    @mockserver.json_handler(
        '/api-proxy-manager/admin/v2/misc/find-endpoints-by-url-prefix',
    )
    def _mock(request):
        return {'match': []}

    @testpoint('probability-validation')
    def _tp_probability(data):
        return {}

    for service in list_services():
        rules = collect_rules(service)
        metas = await fetch_metas(
            service, rules, taxi_authproxy_manager, taxi_config,
        )
        process_metas(service, metas)
