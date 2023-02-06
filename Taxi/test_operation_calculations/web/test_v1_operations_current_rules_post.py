import json

from aiohttp import web
import pytest

from taxi import discovery


@pytest.mark.parametrize(
    'data, status, expected_rules',
    (
        pytest.param(
            {'tariff_zone': 'moscow', 'tariffs': ['econom']},
            200,
            [
                '3d2874ba-000b-4822-a531-5e49e246233b',
                '5168b7b4-64a7-4f3d-a12d-982913a4f11f',
                'c8dacfbd-1424-40a9-9af8-ee2830b5ba1c',
                '4ff869ef-d4d5-489b-a75b-c8fba03f7f15',
            ],
        ),
        pytest.param(
            {
                'tariff_zone': 'moscow',
                'tariffs': ['econom'],
                'brandings': ['no_full_branding'],
            },
            200,
            ['3d2874ba-000b-4822-a531-5e49e246233b'],
        ),
        pytest.param(
            {
                'tariff_zone': 'moscow',
                'tariffs': ['econom'],
                'tags': ['some_tag'],
            },
            200,
            ['5168b7b4-64a7-4f3d-a12d-982913a4f11f'],
        ),
    ),
)
async def test_v1_operations_current_rules_post(
        web_app_client,
        patch_aiohttp_session,
        mock_taxi_tariffs,
        response_mock,
        open_file,
        data,
        status,
        expected_rules,
):
    with open_file(
            'test_data_billing_nmfg_rules.json', mode='rb', encoding=None,
    ) as fp:
        test_data = json.load(fp)

    @mock_taxi_tariffs('/v1/tariff_settings/bulk_retrieve')
    def _tariff_settings_handler(request):
        return web.json_response(
            {
                'zones': [
                    {
                        'tariff_settings': {'timezone': 'Europe/Moscow'},
                        'zone': 'moscow',
                    },
                ],
            },
        )

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

    response = await web_app_client.post(
        '/v1/operations/current_rules/',
        headers={'X-Yandex-Login': 'test_robot'},
        json=data,
    )
    assert response.status == status
    data = await response.json()
    assert len(data) == len(expected_rules)
    expected_data = [
        test_data['expected'][rule_id] for rule_id in expected_rules
    ]
    assert data == expected_data
