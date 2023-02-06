from aiohttp import web
import pytest

from clownductor.internal.db import flavors


@pytest.mark.parametrize(
    'cube_name',
    [
        'DispenserCubeWaitForService',
        'DispenserCubeSetSSDQuota',
        'DispenserCubeSetRAMQuota',
        'DispenserCubeSetCPUQuota',
        'DispenserGetQuotas',
    ],
)
@pytest.mark.features_on('enable_quota_count_hosts')
async def test_post_dispenser_cube_handles(
        web_app_client,
        cube_name,
        load_json,
        mock_dispenser,
        dispenser_get_quotas,
        dispenser_quotas_value,
):
    @mock_dispenser('/common/api/v1/projects')
    # pylint: disable=W0612
    async def handler(request):  # pylint: disable=unused-argument
        return web.json_response(
            {
                'result': [
                    {
                        'key': 'taxistoragepgaas',
                        'name': 'taxistoragedbaas',
                        'description': '',
                        'abcServiceId': 2219,
                        'responsibles': {'persons': [], 'yandexGroups': {}},
                        'members': {'persons': [], 'yandexGroups': {}},
                        'parentProjectKey': 'taxistorage',
                        'subprojectKeys': [
                            'taxipgaassomeservice',
                            'taxipgaaspgservice',
                        ],
                        'person': None,
                    },
                ],
            },
        )

    quotas_json = dispenser_quotas_value
    flavour = 's2.micro'

    @mock_dispenser('/db/api/v1/quotas/taxipgaassomeservice/mdb/ssd/ssd-quota')
    # pylint: disable=W0612
    async def ssd_handler(request):
        assert request.json == {'maxValue': 257698037760, 'unit': 'BYTE'}
        return web.json_response({})

    @mock_dispenser('/db/api/v1/quotas/taxipgaassomeservice/mdb/ram/ram-quota')
    # pylint: disable=W0612
    async def ram_handler(request):
        actual = quotas_json['result'][0]['ownActual']
        assert request.json == {
            'maxValue': 3 * flavors.ram_for(flavour) + actual,
            'unit': 'BYTE',
        }
        return web.json_response({})

    @mock_dispenser('/db/api/v1/quotas/taxipgaassomeservice/mdb/cpu/cpu-quota')
    # pylint: disable=W0612
    async def cpu_handler(request):
        actual = quotas_json['result'][3]['ownActual']
        assert request.json == {
            'maxValue': 3 * flavors.cpu_for(flavour) + actual,
            'unit': 'PERMILLE_CORES',
        }
        return web.json_response({})

    json_datas = load_json(f'{cube_name}.json')
    for json_data in json_datas:
        data_request = json_data['data_request']
        response = await web_app_client.post(
            f'/task-processor/v1/cubes/{cube_name}/', json=data_request,
        )
        assert response.status == 200
        content = await response.json()
        assert content == json_data['content_expected']
