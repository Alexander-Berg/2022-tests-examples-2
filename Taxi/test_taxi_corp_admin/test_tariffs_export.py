import datetime

import pytest

NOW = datetime.datetime.utcnow().replace(microsecond=0)


@pytest.mark.now(NOW.isoformat())
async def test_tariffs_export(
        patch, load_json, taxi_corp_admin_client, load_binary, mockserver,
):
    @mockserver.json_handler('/corp-tariffs/v1/tariff/current')
    async def _get_tariff_current(request):
        return mockserver.make_response(
            json=load_json('get_tariff_corp.json'), status=200,
        )

    @mockserver.json_handler('/tariffs/v1/tariff_zones')
    async def _get_tariff_zones(request):
        return mockserver.make_response(
            json={
                'zones': [
                    {
                        'name': 'obninsk',
                        'time_zone': 'Europe/Moscow',
                        'country': 'rus',
                        'translation': 'Обнинск',
                        'currency': 'RUB',
                    },
                ],
            },
            status=200,
        )

    response = await taxi_corp_admin_client.post(
        '/v1/tariffs/export',
        json={
            'zones': ['obninsk'],
            'tariff_plan_series_id': 'tariff_plan_series_id_1',
        },
    )
    assert response.status == 200
    result = await response.content.read()
    result = result.decode('utf-8-sig').replace('\r', '')
    expected = (
        load_binary('tariffs_result.csv')
        .decode('utf-8-sig')
        .replace('\r\n', '')
    )
    assert result == expected
