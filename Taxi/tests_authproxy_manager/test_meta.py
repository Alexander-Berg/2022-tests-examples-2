import aiohttp
import pytest

from tests_authproxy_manager import utils


@pytest.mark.parametrize(
    'proxy,url,proxy_urls',
    [
        (
            'passenger-authorizer',
            'https://kibana.taxi.yandex-team.ru/app/kibana#/discover?_g=()&_a='
            '(columns:!(host),index:\'f8e70880-c75c-11e9-8a12-ddb2ef5a51ea\','
            'interval:auto,query:(language:kuery,query:\'(cgroups: '
            'taxi_tc OR cgroups: taxi_tc_eu) AND rule_name: '
            '"name1"\'),sort:!(!(\'@timestamp\',desc)))',
            [
                'https://tc.mobile.yandex.net/4.0/',
                'https://uc.taxi.yandex.net/4.0/',
                'https://legal.rostaxi.org/4.0/',
                'https://tc.rostaxi.org/4.0/',
                'https://tc.tst.mobile.yandex.net/4.0/',
                'https://tc-tst.mobile.yandex.net/4.0/',
            ],
        ),
        (
            'ya-authproxy',
            'https://kibana.taxi.yandex-team.ru/app/kibana#/discover?_g=()&_a='
            '(columns:!(host),index:\'f8e70880-c75c-11e9-8a12-ddb2ef5a51ea\','
            'interval:auto,query:(language:kuery,query:\'(ngroups: '
            'taxi_ya-authproxy_stable OR ngroups: '
            'taxi_ya-authproxy_pre_stable) AND '
            'rule_name: '
            '"name1"\'),sort:!(!(\'@timestamp\',desc)))',
            [
                'https://ya-authproxy.taxi.yandex.net/4.0/',
                'https://ya-authproxy.taxi.yandex.ru/4.0/',
                'https://ya-authproxy.taxi.yandex.kz/4.0/',
                'https://ya-authproxy.taxi.yandex.com/4.0/',
                'https://business.taxi.yandex.ru/4.0/',
            ],
        ),
        (
            'grocery-authproxy',
            'https://kibana.taxi.yandex-team.ru/app/kibana#/discover?_g=()&_a='
            '(columns:!(host),index:\'f8e70880-c75c-11e9-8a12-ddb2ef5a51ea\','
            'interval:auto,query:(language:kuery,query:\'(ngroups: '
            'lavka_grocery-authproxy_stable OR ngroups: '
            'lavka_grocery-authproxy_pre_stable) AND '
            'rule_name: '
            '"name1"\'),sort:!(!(\'@timestamp\',desc)))',
            ['https://grocery-authproxy.lavka.yandex.net/4.0/'],
        ),
    ],
)
async def test_meta(authproxy_manager, proxy, url, proxy_urls, mockserver):
    @mockserver.handler(
        '/api-proxy-manager/admin/v2/misc/find-endpoints-by-url-prefix',
    )
    async def _mock_apm(request):
        assert request.query == {'tvm': 'mock', 'path_prefix': '/4.0/'}
        assert request.get_data() == b''

        return aiohttp.web.json_response(
            status=200,
            data={
                'match': [
                    {
                        'cluster': 'c',
                        'id': 'i',
                        'original-path': '',
                        'prestable': False,
                        'enabled': True,
                    },
                ],
            },
        )

    rule_name = 'name1'
    response = await authproxy_manager.v1_rules_by_name_put(
        proxy=proxy,
        name=rule_name,
        maintained_by='common_components',
        rule=utils.adjust_rule({'input': {'rule_name': rule_name}}),
    )
    assert response.status == 201

    response = await authproxy_manager.v1_rules_meta(
        proxy=proxy, rule_names=[rule_name],
    )
    assert response.status == 200

    rule_metas = response.json()['rule_metas']
    assert len(rule_metas) == 1
    rule_meta = rule_metas[0]

    del rule_meta['headers_info']
    assert rule_meta == {
        'rule_name': rule_name,
        'kibana_url': url,
        'api-proxy-links': [{'cluster': 'c', 'id': 'i'}],
    }

    # Note: 'headers_info' is checked in a specific authproxy testsuite

    assert _mock_apm.times_called == 1


async def test_apiproxy_404(authproxy_manager, mockserver):
    @mockserver.handler(
        '/api-proxy-manager/admin/v2/misc/find-endpoints-by-url-prefix',
    )
    async def _mock_apm(request):
        assert request.query == {'tvm': 'mock', 'path_prefix': '/4.0/'}
        assert request.get_data() == b''

        return aiohttp.web.json_response(
            status=404, data={'code': 'resource_not_found', 'message': 'ttt'},
        )

    proxy = 'grocery-authproxy'
    rule_name = 'name1'
    response = await authproxy_manager.v1_rules_by_name_put(
        proxy=proxy,
        name=rule_name,
        maintained_by='common_components',
        rule=utils.adjust_rule({'input': {'rule_name': rule_name}}),
    )
    assert response.status == 201

    response = await authproxy_manager.v1_rules_meta(
        proxy=proxy, rule_names=[rule_name],
    )
    assert response.status == 200

    rule_metas = response.json()['rule_metas']
    assert len(rule_metas) == 1
    rule_meta = rule_metas[0]
    assert rule_meta['api-proxy-links'] == []

    assert _mock_apm.times_called == 1
