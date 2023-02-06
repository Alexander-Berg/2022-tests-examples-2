import json

import pytest

from logs_from_yt.generated.cron import run_cron

CLOWNDUCTOR_V1_HOSTS = {
    '294212': [
        {
            'name': 'eda-eats-authproxy-pre-stable-1.vla.yandex.yp-c.net',
            'branch_id': 294212,
        },
    ],
    '294213': [
        {
            'name': 'eda-eats-authproxy-stable-1.vla.yandex.yp-c.net',
            'branch_id': 294213,
        },
        {
            'name': 'eda-eats-authproxy-stable-2.sas.yandex.yp-c.net',
            'branch_id': 294213,
        },
    ],
    '294214': [
        {
            'name': 'eda-eats-authproxy-testing-1.vla.yandex.yp-c.net',
            'branch_id': 294214,
        },
        {
            'name': 'eda-eats-authproxy-testing-2.sas.yandex.yp-c.net',
            'branch_id': 294214,
        },
    ],
    '295833': [
        {
            'name': 'taxi-supportai-pre-stable-1.vla.yandex.yp-c.net',
            'branch_id': 295833,
        },
    ],
    '295834': [
        {
            'name': 'taxi-supportai-stable-1.vla.yandex.yp-c.net',
            'branch_id': 295834,
        },
        {
            'name': 'taxi-supportai-stable-2.sas.yandex.yp-c.net',
            'branch_id': 295834,
        },
    ],
    '295835': [
        {
            'name': 'taxi-supportai-testing-1.vla.yandex.yp-c.net',
            'branch_id': 295835,
        },
        {
            'name': 'taxi-supportai-testing-2.sas.yandex.yp-c.net',
            'branch_id': 295835,
        },
    ],
}

ACTIVE_VERSIONS = {
    'ride_tech_logparser': {
        'meta': {},
        'content': {
            'parser': {
                'params': {
                    'unknown_key': '123',
                    'module_prefix_to_ignore': 'should be kept',
                },
            },
        },
    },
    'backend_py3_logparser': {
        'meta': {},
        'content': {
            'parser': {
                'params': {
                    'unknown_key': '123',
                    'module_ignore_set': 'should be kept',
                },
            },
        },
    },
}


@pytest.mark.config(
    LOGS_FROM_YT_LOGS_SATURATOR={
        'concurrent_fetches_to_clownductor': 10,
        'cluster_types_to_map': ['nanny', 'conductor'],
        'configs_to_update': [
            {
                'id': 'ride_tech_logparser',
                'params_keys_to_keep': ['module_prefix_to_ignore'],
                'versions_to_retain': 10,
            },
            {
                'id': 'backend_py3_logparser',
                'params_keys_to_keep': ['module_ignore_set'],
                'versions_to_retain': 10,
            },
        ],
    },
)
async def test_ok(cron_context, mockserver, clown_cache_mocks):
    @mockserver.json_handler('/clownductor/v1/hosts/')
    def _clownductor_v1_hosts(request):
        if request.args['branch_id'] not in CLOWNDUCTOR_V1_HOSTS.keys():
            return []
        return CLOWNDUCTOR_V1_HOSTS[request.args['branch_id']]

    @mockserver.json_handler(
        '/health-ui/api/public/logshatter/config/version/active',
    )
    def _get_active_version_health_ui(request):
        assert request.headers['Authorization'] == 'OAuth health-ui-oauth'
        return ACTIVE_VERSIONS[request.args['configId']]

    @mockserver.json_handler(
        '/health-ui/api/public/logshatter/config/version/createNewVersion',
    )
    def _post_new_version_health_ui(request):
        assert request.headers['Content-Type'] == 'application/json'
        assert request.headers['Authorization'] == 'OAuth health-ui-oauth'
        params = request.json['parser']['params']
        if request.json['id']['configId'] == 'ride_tech_logparser':
            assert params['module_prefix_to_ignore'] == 'should be kept'
        elif request.json['id']['configId'] == 'backend_py3_logparser':
            assert params['module_ignore_set'] == 'should be kept'

        assert (
            json.loads(
                params['eda-eats-authproxy-pre-stable-1.vla.yandex.yp-c.net'],
            )
            == {
                'namespace': 'eda',
                'project': 'eda',
                'service': 'eats-authproxy',
                'env': 'prestable',
            }
        )
        assert (
            json.loads(
                params['eda-eats-authproxy-stable-1.vla.yandex.yp-c.net'],
            )
            == {
                'namespace': 'eda',
                'project': 'eda',
                'service': 'eats-authproxy',
                'env': 'stable',
            }
        )
        assert (
            json.loads(
                params['eda-eats-authproxy-stable-2.sas.yandex.yp-c.net'],
            )
            == {
                'namespace': 'eda',
                'project': 'eda',
                'service': 'eats-authproxy',
                'env': 'stable',
            }
        )
        assert (
            json.loads(
                params['eda-eats-authproxy-testing-1.vla.yandex.yp-c.net'],
            )
            == {
                'namespace': 'eda',
                'project': 'eda',
                'service': 'eats-authproxy',
                'env': 'testing',
            }
        )
        assert (
            json.loads(
                params['eda-eats-authproxy-testing-2.sas.yandex.yp-c.net'],
            )
            == {
                'namespace': 'eda',
                'project': 'eda',
                'service': 'eats-authproxy',
                'env': 'testing',
            }
        )
        assert (
            json.loads(
                params['taxi-supportai-pre-stable-1.vla.yandex.yp-c.net'],
            )
            == {
                'namespace': 'taxi',
                'project': 'taxi-ml',
                'service': 'supportai',
                'env': 'prestable',
            }
        )
        assert (
            json.loads(params['taxi-supportai-stable-1.vla.yandex.yp-c.net'])
            == {
                'namespace': 'taxi',
                'project': 'taxi-ml',
                'service': 'supportai',
                'env': 'stable',
            }
        )
        assert (
            json.loads(params['taxi-supportai-stable-2.sas.yandex.yp-c.net'])
            == {
                'namespace': 'taxi',
                'project': 'taxi-ml',
                'service': 'supportai',
                'env': 'stable',
            }
        )
        assert (
            json.loads(params['taxi-supportai-testing-1.vla.yandex.yp-c.net'])
            == {
                'namespace': 'taxi',
                'project': 'taxi-ml',
                'service': 'supportai',
                'env': 'testing',
            }
        )
        assert (
            json.loads(params['taxi-supportai-testing-2.sas.yandex.yp-c.net'])
            == {
                'namespace': 'taxi',
                'project': 'taxi-ml',
                'service': 'supportai',
                'env': 'testing',
            }
        )
        return {'configId': request.json['id']['configId'], 'versionNumber': 0}

    @mockserver.json_handler(
        '/health-ui/api/public/logshatter/config/version/delete',
    )
    def _delete_old_versions_health_ui(request):
        assert request.headers['Authorization'] == 'OAuth health-ui-oauth'
        return {}

    await run_cron.main(['logs_from_yt.crontasks.logs_saturator', '-t', '0'])


@pytest.mark.config(
    LOGS_FROM_YT_LOGS_SATURATOR={
        'concurrent_fetches_to_clownductor': 10,
        'cluster_types_to_map': ['nanny', 'conductor'],
        'configs_to_update': [
            {
                'id': 'unknown_config',
                'params_keys_to_keep': [],
                'versions_to_retain': 10,
            },
            {
                'id': 'ride_tech_logparser',
                'params_keys_to_keep': [],
                'versions_to_retain': 10,
            },
        ],
    },
)
async def test_errors(cron_context, mockserver, clown_cache_mocks):
    @mockserver.json_handler('/clownductor/v1/hosts/')
    def _clownductor_v1_hosts(request):
        if request.args['branch_id'] not in CLOWNDUCTOR_V1_HOSTS.keys():
            return []
        return CLOWNDUCTOR_V1_HOSTS[request.args['branch_id']]

    @mockserver.json_handler(
        '/health-ui/api/public/logshatter/config/version/active',
    )
    def _get_active_version_health_ui(request):
        if request.args['configId'] == 'unknown_config':
            return mockserver.make_response(status=404, json={})
        return ACTIVE_VERSIONS[request.args['configId']]

    @mockserver.json_handler(
        '/health-ui/api/public/logshatter/config/version/createNewVersion',
    )
    def _post_new_version_health_ui(request):
        assert request.json['id']['configId'] != 'unknown_config'
        return mockserver.make_response(status=404, json={})

    @mockserver.json_handler(
        '/health-ui/api/public/logshatter/config/version/delete',
    )
    def _delete_old_versions_health_ui(request):
        assert False

    await run_cron.main(['logs_from_yt.crontasks.logs_saturator', '-t', '0'])
