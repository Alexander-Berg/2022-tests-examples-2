import contextlib
import datetime

import pytest

from taxi_agglomerations import models
from taxi_agglomerations.generated.web import web_context as web_context_


@pytest.mark.parametrize(
    '',
    (
        pytest.param(
            marks=pytest.mark.config(AGGLOMERATIONS_USE_TARIFFS_CLIENT=True),
        ),
        pytest.param(
            marks=pytest.mark.config(AGGLOMERATIONS_USE_TARIFFS_CLIENT=False),
        ),
    ),
)
@pytest.mark.parametrize(
    'tariff_name, expected_geoarea, raised_exception',
    (
        pytest.param(
            'moscow',
            models.tariff.Tariff('moscow', 'RUB'),
            False,
            id='moscow',
        ),
        pytest.param(
            'inserted',
            models.tariff.Tariff('inserted', 'RUB'),
            False,
            id='inserted',
        ),
        pytest.param('not existed', None, True, id='not_found'),
    ),
)
async def test_tariff_repository(
        web_context: web_context_.Context,
        caplog,
        tariff_name,
        expected_geoarea,
        raised_exception,
        mockserver,
        load_json,
):
    repository = web_context.tariff_repository
    cache = web_context.tariff_cache.get_cache()
    tariff_data = {
        'activation_zone': 'inserted_activation',
        'home_zone': 'inserted',
        'categories': [{'id': '11', 'currency': 'RUB'}],
        'updated': datetime.datetime.utcnow(),
    }

    @mockserver.json_handler('/taxi-tariffs/v1/tariff_zones/archive')
    async def _mock(request):
        tariffs = load_json('db_tariffs.json') + [tariff_data]
        zones = [
            {
                'name': tariff_['home_zone'],
                'time_zone': 'Europe/Moscow',
                'country': 'russia',
                'currency': 'RUB',
            }
            for tariff_ in tariffs
        ]
        return {'zones': zones}

    @mockserver.json_handler('/taxi-tariffs/v1/tariff/current')
    async def _mock_current_tariff(request):
        tariffs = load_json('db_tariffs.json') + [tariff_data]
        zone = next(
            (
                {
                    'home_zone': tariff_['home_zone'],
                    'activation_zone': tariff_['home_zone'] + '_activation',
                    'time_zone': 'Europe/Moscow',
                    'country': 'russia',
                    'categories': [
                        {
                            'id': 'unique_id',
                            'add_minimal_to_paid_cancel': False,
                            'category_name': 'vip',
                            'category_type': 'application',
                            'currency': 'RUB',
                            'day_type': 2,
                            'minimal': 840,
                            'name_key': 'interval.24h',
                            'paid_cancel_fix': 30,
                            'time_from': '00:00',
                            'time_to': '23:59',
                            'category_name_key': 'vip',
                            'included_one_of': [],
                            'meters': [],
                            'special_taximeters': [],
                            'zonal_prices': [],
                        },
                    ],
                    'date_from': '2019-09-10T00:00:00',
                }
                for tariff_ in tariffs
                if tariff_['home_zone'] == request.query['zone']
            ),
            None,
        )
        data = zone
        if data is None:
            data = {'code': 'NOT_FOUND', 'message': 'not found'}
        return mockserver.make_response(status=200 if zone else 404, json=data)

    await web_context.mongo.tariffs.insert(dict(tariff_data))

    context_manager: contextlib.AbstractContextManager
    if raised_exception:
        context_manager = pytest.raises(repository.NotFound)
    else:
        context_manager = contextlib.nullcontext()

    tariff = None
    with context_manager:
        # Act
        tariff = await repository.get_tariff(tariff_name, cache)

    assert tariff == expected_geoarea
