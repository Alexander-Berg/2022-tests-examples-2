import json

from aiohttp import web
import bson
import pytest


@pytest.mark.config(
    OPERATION_CALCULATIONS_NMFG_MAX_SUBGMV={'__default__': 0.1, 'spb': 0.2},
)
@pytest.mark.parametrize(
    'key, expected_status, expected_result',
    (
        pytest.param('ok', 200, {}),
        pytest.param(
            'conflict',
            400,
            {
                'code': '400',
                'message': (
                    'Some sub-operations contain the same time intervals'
                ),
            },
        ),
        pytest.param(
            'large sub-gmv',
            400,
            {
                'code': 'BadRequest::SubGmvLimit',
                'details': {'current_sub_gmv': 0.11, 'max_sub_gmv': 0.1},
                'message': 'Sub/gmv greater than limit',
            },
        ),
        pytest.param('recalc', 200, {}),
        pytest.param(
            'invalid_recalc',
            400,
            {
                'code': 'BadRequest::InvalidGuarantees',
                'details': {'0': {'steps': [2]}},
                'message': 'Invalid guarantees',
            },
        ),
        pytest.param('ok', 200, {}),
        pytest.param(
            'bad_start',
            400,
            {
                'code': 'BadRequest::BadStartDate',
                'message': 'Subvention start date in the past',
            },
        ),
    ),
)
@pytest.mark.now('2019-12-31T22:00:00+00:00')
async def test_v2_operations_post(
        web_app_client,
        open_file,
        key,
        expected_status,
        expected_result,
        mock_taxi_tariffs,
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
                    {
                        'tariff_settings': {'timezone': 'Europe/Moscow'},
                        'zone': 'lytkarino',
                    },
                ],
            },
        )

    with open_file('test_data.json', mode='rb', encoding=None) as fp:
        test_data = json.load(fp)
    response = await web_app_client.post(
        '/v2/operations/',
        json=test_data[key],
        headers={'X-Yandex-Login': 'test_robot'},
    )

    data = await response.json()
    assert response.status == expected_status
    if expected_status == 200:
        task_id = data.pop('task_id')
        assert bson.ObjectId.is_valid(task_id)
        assert data == {}
    else:
        assert data == expected_result
