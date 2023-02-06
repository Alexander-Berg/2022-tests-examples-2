# pylint: disable=import-only-modules
# pylint: disable=broad-except
# flake8: noqa

import pytest

from taxi.codegen.swaggen_serialization import ValidationError
from taxi_tariffs.api.common.cast_utils import overrided_schemas, schemas
from taxi_tariffs.generated.service.swagger import models


def _patch_categories(tariff):
    for category in tariff['categories']:
        category['category_name_key'] = 'category_name_key'


@pytest.mark.parametrize(
    'test_name',
    [
        'correct_schema',
        'with_new_field_in_root',
        'with_new_field_in_category',
        'with_many_new_fields',
        'not_correct_schema',
    ],
)
async def test_tariff_cast(load_json, test_name):
    dictionary = load_json('tariffs.json')[test_name]
    try:
        result = await schemas.Tariff.dump(dictionary)
        _patch_categories(result)
        categories = result['categories']
        models.api.GetTariffResponse(
            home_zone=result['home_zone'],
            activation_zone=result['activation_zone'],
            date_from=result['date_from'],
            date_to=result.get('date_to'),
            categories=[
                models.api.TariffCategory.deserialize(category)
                for category in categories
            ],
        )
    except (KeyError, ValidationError):
        assert test_name == 'not_correct_schema'


@pytest.mark.parametrize(
    'test_name',
    [
        'correct_schema',
        'with_new_field_in_root',
        'with_new_field_in_category',
        'with_many_new_fields',
        'not_correct_schema',
    ],
)
async def test_get_tariff_response_cast(load_json, test_name):
    dictionary = load_json('tariff_responses.json')[test_name]
    try:
        result = await overrided_schemas.OverridedTariff.dump(dictionary)
        _patch_categories(result)
        models.api.GetTariffResponse.deserialize(result)
    except (KeyError, ValidationError):
        assert test_name == 'not_correct_schema'
