import json
import pprint
import re
from typing import List

import pytest


def pytest_addoption(parser):
    group = parser.getgroup('service runner', 'servicerunner')
    group.addoption(
        '--collect-proxy-rules-meta',
        action='store_true',
        help='Collect meta_headers for authorization proxies',
    )


class MetaHeaders:
    def validate_request(
            self,
            prefilter_headers: List[str],
            prefilter_cookies: List[str],
            prefilter_json_body: List[str],
            postfilter_headers: List[str],
            postfilter_cookies: List[str],
    ) -> None:
        new_headers = [
            name
            for name in postfilter_headers
            if name not in prefilter_headers
        ]

        def validate_single_variant(variant):
            # All input required params must be present
            for iparam in variant['input_data']['parameters']:
                if not iparam['required']:
                    continue

                if iparam['type'] == 'header':
                    container = prefilter_headers
                    what = 'HTTP header'
                elif iparam['type'] == 'cookie':
                    container = prefilter_cookies
                    what = 'HTTP cookie'
                elif iparam['type'] == 'json-body':
                    container = prefilter_json_body
                    what = 'JSON body'
                else:
                    assert False

                name = iparam['name'].lower()
                if name not in container:
                    raise Exception(
                        f'Client HTTP request must contain {what} "{name}", '
                        'but it is missing.',
                    )

            # All output required params must be present
            for uparam in variant['upstream_data']['parameters']:
                if not uparam['required']:
                    continue

                if uparam['type'] == 'header':
                    container = postfilter_headers
                    what = 'HTTP header'
                elif uparam['type'] == 'cookie':
                    container = postfilter_cookies
                    what = 'HTTP cookie'
                else:
                    assert False

                name = uparam['name'].lower()
                if name not in container:
                    # exception for TVM service ticket:
                    # TVM_ENABLED=False in testsuite
                    if name != 'x-ya-service-ticket':
                        raise Exception(
                            f'The proxy is ought to add {what} "{name}", '
                            'but it is missing in proxy upstream '
                            'HTTP request.',
                        )

            # All new headers must be defined in meta
            for name in new_headers:
                for uparam in variant['upstream_data']['parameters']:
                    if (
                            uparam['name'].lower() == name
                            and uparam['type'].lower() == 'header'
                    ):
                        # ok, found
                        break
                else:
                    raise Exception(
                        f'The proxy added HTTP header "{name}", '
                        'but it is not declared.',
                    )

        variants = self.meta_headers['variants']
        err_msg = ''
        for variant in variants:
            try:
                validate_single_variant(variant)
                break
            except Exception as exc:  # pylint: disable=broad-except
                variant_pp = pprint.pformat(variant, indent=2)
                err_msg += f'\nvariant: {variant_pp}\nerror: {exc}\n'
        else:
            num = len(variants)
            assert False, (
                f'The request doesn\'t conform to any of {num} variant(s). '
                f'The request data is:\n'
                f'  input headers: {prefilter_headers}\n'
                f'  input cookies: {prefilter_cookies}\n'
                f'  output headers: {postfilter_headers}\n'
                f'  new headers: {new_headers}\n'
                f'  output cookies: {postfilter_cookies}\n'
                f'\nThe errors for specific variants are: {err_msg}'
            )

    def __init__(self, routing_rule: dict, meta_headers: dict):
        self.meta_headers = meta_headers


@pytest.fixture(name='collected_rules_filename')
def _collected_rules_filename():
    return None


@pytest.fixture(scope='session', name='store_meta_rules')
def _store_meta_rules(pytestconfig):
    class Store:
        def __init__(self):
            self.rules = {}

        def add_rule(self, filename, rule):
            if filename not in self.rules:
                self.rules[filename] = []

            rules = self.rules[filename]
            if rule not in rules:
                rules.append(rule)

    def store_to_files(store) -> None:
        for filename in store.rules:
            rules = store.rules[filename]
            for rule in rules:
                upstream = rule['output']['upstream']
                rule['output']['upstream'] = re.sub(
                    'http://localhost:[0-9]*', 'http://example.com', upstream,
                )

            rules.sort(
                key=lambda x: (
                    x['input']['rule_name'],
                    x['output']['upstream'],
                ),
            )

            with open(filename, 'w') as ofile:
                json.dump(rules, ofile, indent=2, sort_keys=True)
                ofile.write('\n')

    store = Store()
    try:
        yield store
    finally:
        if pytestconfig.option.collect_proxy_rules_meta:
            store_to_files(store)


@pytest.fixture()
async def routing_rules_meta_validation(
        testpoint,
        routing_rules,
        load_json,
        store_meta_rules,
        collected_rules_filename,
        pytestconfig,
):
    """Validate that the routed request matches the a-m cached meta_headers
       from services/SERVICE/testsuite/*/static/meta_rules.json
       """

    validate = not pytestconfig.option.collect_proxy_rules_meta

    shared = {}

    meta_rules = load_json('meta_headers_cache.json')

    @testpoint('proxy_prefilter')
    def _tp_proxy_prefilter(data):
        shared['trace_id'] = data['trace_id']
        shared['headers'] = data['headers']
        shared['cookies'] = data['cookies']
        shared['json-body'] = data['json-body']

    @testpoint('proxy_postfilter')
    def _tp_proxy_postfilter(data):
        def select_rule(rule_name):
            rules = routing_rules.get_rules()
            for rule in rules:
                if rule['input']['rule_name'] == rule_name:
                    return rule
            assert (
                False
            ), f'No rule with name "{rule_name}" in routing_rules fixture'
            return None

        def select_meta_headers(rule: dict) -> MetaHeaders:
            for mh_item in meta_rules:
                if (
                        mh_item['rule']['input'] == rule['input']
                        and mh_item['rule']['proxy'] == rule['proxy']
                        and mh_item['rule']['rule_type'] == rule['rule_type']
                ):
                    return MetaHeaders(rule, mh_item['meta'])

            assert False, f'Rule not found in mh cache, rule = {rule}'
            return None

        def lower(lst: List[str]) -> List[str]:
            return [x.lower() for x in lst]

        trace_id = data['trace_id']
        prefilter_headers = lower(shared['headers'])
        prefilter_cookies = lower(shared['cookies'])
        prefilter_json_body = lower(shared['json-body'])

        postfilter_headers = lower(data['headers'])
        postfilter_cookies = lower(data['cookies'])

        assert trace_id == shared['trace_id']

        rule = select_rule(data['rule_name'])

        if validate:
            mheaders = select_meta_headers(rule)

            mheaders.validate_request(
                prefilter_headers,
                prefilter_cookies,
                prefilter_json_body,
                postfilter_headers,
                postfilter_cookies,
            )

        filename = collected_rules_filename
        store_meta_rules.add_rule(filename, rule)

    yield
