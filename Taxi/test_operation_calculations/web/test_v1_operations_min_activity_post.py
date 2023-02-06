import json

import pytest

from taxi import discovery


@pytest.mark.parametrize(
    'data, status, expected',
    (
        pytest.param(
            {'tariff_zone': 'moscow', 'tariffs': ['econom']},
            200,
            {'value': 0, 'variants': [10, 20]},
        ),
        pytest.param(
            {
                'tariff_zone': 'moscow',
                'tariffs': ['econom'],
                'brandings': ['no_full_branding'],
            },
            200,
            {'value': 10, 'variants': []},
        ),
        pytest.param(
            {
                'tariff_zone': 'moscow',
                'tariffs': ['econom'],
                'tags': ['some_tag'],
            },
            200,
            {'value': 20, 'variants': []},
        ),
    ),
)
async def test_v1_operations_current_rules_post(
        web_app_client,
        patch_aiohttp_session,
        response_mock,
        open_file,
        data,
        status,
        expected,
):
    with open_file(
            'test_data_billing_nmfg_rules.json', mode='rb', encoding=None,
    ) as fp:
        test_data = json.load(fp)

    @patch_aiohttp_session(
        discovery.find_service('billing_subventions').url + '/v1/rules/select',
        'POST',
    )
    def _patch_request(method, url, **kwargs):
        args = kwargs['json']
        rules = test_data['subventions']
        branding_type = args.get('branding_type', None)
        filtered_rules = []
        for rule in rules:
            if branding_type and branding_type != rule.get(
                    'branding_type', None,
            ):
                continue
            filtered_rules.append(rule)
        return response_mock(json={'subventions': filtered_rules})

    data['date_from'] = '2021-12-12'
    data['date_to'] = '2021-12-13'
    response = await web_app_client.post(
        '/v1/operations/min_activity/',
        headers={'X-Yandex-Login': 'test_robot'},
        json=data,
    )
    assert response.status == status
    data = await response.json()
    assert data == expected
