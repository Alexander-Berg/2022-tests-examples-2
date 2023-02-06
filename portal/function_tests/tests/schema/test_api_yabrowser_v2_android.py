# -*- coding: utf-8 -*-
import allure
import pytest

from common.schema import get_schema_validator
from common.utils  import delete

from tests.schema.crutches import *
from tests.schema.utils    import *


@pytest.mark.yasm
@allure.feature('api_yabrowser_v2_android', 'schema_tests_simple')
@allure.story('api_yabrowser_v2_android_schema')
@pytest.mark.parametrize('params', get_params('tests/schema/api_yabrowser_android'))
def test_schema_api_yabrowser_v2_android(params, yasm):
    check_params(params)
    prepare_params(params)

    response = get_response(params)
    prepare_for_validation(response)

    schema_version = delete(params, 'schema_version')
    dot_pos = schema_version.rfind('.')
    if dot_pos not in [-1, schema_version.find('.')]:
        schema_version = schema_version[:dot_pos] + schema_version[dot_pos + 1:]

    schema_path = 'schema/android/{}/api/search/2/yabrowserapi-response.json'.format(schema_version)
    validator = get_schema_validator(schema_path)
    validate_and_send_signal(response, validator, yasm, 'api_yabrowser_v2_android_{}'.format(schema_version))


# если хотите добавить сюда костыль, заведите тикет с описанием
# и добавьте функцию в crutches.py с именем, содержащим очередь и номер тикета
def prepare_for_validation(response):
    if not isinstance(response, dict):
        return

    crutch_HOME_71234(response)

    if 'block' in response and isinstance(response['block'], list):
        for block in response['block']:
            if not isinstance(block, dict):
                continue

            if block.get('id', '') in ['weather', 'weather_vertical']:
                crutch_HOME_70251(block)
                crutch_HOME_71272(block)
