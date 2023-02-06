# flake8: noqa
# pylint: disable=import-error,wildcard-import
from cargo_tariffs_plugins.generated_tests import *
import pytest


def get_default_service_scheme():
    return {
        'name': 'express',
        'text': 'Экспресс Доставка',
        'tariff_schema': {
            'title': 'boarding_price',
            'description': 'Цена подачи на точке А',
            'type': 'number',
        },
    }


@pytest.mark.geoareas(tg_filename='typed_geoareas_base.json')
@pytest.mark.experiments3(filename='experiment3.json')
async def test_simple(v1_services_scheme):
    service = 'ndd_client'
    response = await v1_services_scheme.get_service_scheme(service)
    assert response.status_code == 200

    body = response.json()
    assert body['name'] == service
    assert body['text'] == get_default_service_scheme()['text']
    assert (
        body['tariff_schema'] == get_default_service_scheme()['tariff_schema']
    )
    assert body['conditions'] == {
        'groups': [
            {
                'fields': [
                    {
                        'name': 'employer_id',
                        'text': 'employer_id',
                        'type': 'string',
                    },
                ],
                'name': 'client',
                'text': 'client',
            },
            {
                'fields': [
                    {
                        'name': 'source_zone',
                        'text': 'source_zone',
                        'type': 'string',
                    },
                ],
                'name': 'source_geo',
                'text': 'source_geo',
            },
            {
                'fields': [
                    {
                        'name': 'destination_zone',
                        'text': 'destination_zone',
                        'type': 'string',
                    },
                ],
                'name': 'destination_geo',
                'text': 'destination_geo',
            },
            {
                'fields': [
                    {
                        'name': 'tariff_category',
                        'text': 'tariff_category',
                        'type': 'string',
                    },
                ],
                'name': 'tariff',
                'text': 'tariff',
            },
        ],
    }
