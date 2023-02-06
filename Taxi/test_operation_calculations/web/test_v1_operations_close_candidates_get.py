import json

from aiohttp import web
import pytest

from taxi import discovery


@pytest.mark.parametrize('key, expected_status', (pytest.param('ok', 200),))
@pytest.mark.pgsql(
    'operation_calculations', files=['pg_operations_params.sql'],
)
async def test_v1_operations_close_candidates_get(
        web_app_client,
        patch_aiohttp_session,
        response_mock,
        mock_taxi_tariffs,
        open_file,
        key,
        expected_status,
):
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

    with open_file(
            'test_data_billing_nmfg_rules.json', mode='rb', encoding=None,
    ) as fp:
        test_data = json.load(fp)

    @patch_aiohttp_session(
        discovery.find_service('billing_subventions').url + '/v1/rules/select',
        'POST',
    )
    def _patch_request(method, url, **kwargs):
        rules = test_data['subventions']
        return response_mock(json={'subventions': rules})

    response = await web_app_client.get(
        '/v1/operations/close_candidates',
        params={'task_id': '61711eb7b7e4790047d4fe50'},
    )
    assert expected_status == response.status
    data = await response.json()
    important_fields = [
        (
            obj['subvention_rule_id'],
            obj['branding_type'],
            obj['tags'],
            obj['should_close'],
        )
        for obj in data['rules']
    ]
    important_fields.sort(key=lambda x: x[0])
    assert important_fields == [
        (
            'group_id/3d2874ba-000b-4822-a531-5e49e246233b',
            'no_full_branding',
            [],
            False,
        ),
        (
            'group_id/4ff869ef-d4d5-489b-a75b-c8fba03f7f15',
            'unspecified',
            ['moscow_center_car'],
            False,
        ),
        (
            'group_id/5168b7b4-64a7-4f3d-a12d-982913a4f11f',
            'unspecified',
            ['some_tag'],
            False,
        ),
        (
            'group_id/c8dacfbd-1424-40a9-9af8-ee2830b5ba1c',
            'unspecified',
            [],
            True,
        ),
    ]
