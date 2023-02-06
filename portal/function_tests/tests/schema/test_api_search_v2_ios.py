# -*- coding: utf-8 -*-
import allure
import pytest

from common.schema import get_schema_validator

from tests.schema.crutches import *
from tests.schema.utils    import *


@pytest.mark.yasm
@allure.feature('api_search_v2_ios', 'schema_tests_simple')
@allure.story('api_search_v2_ios_schema')
@pytest.mark.parametrize('params', get_params('tests/schema/api_search_v2_ios'))
def test_schema_api_search_v2_ios(params, yasm):
    check_params(params)
    prepare_params(params)

    response = get_response(params)
    prepare_for_validation(response)

    schema_path = 'schema/search_app_ios/{}/api/search/2/searchapi-response.json'.format(params['schema_version'])
    validator = get_schema_validator(schema_path)
    validate_and_send_signal(response, validator, yasm, 'api_search_v2_ios_{}'.format(params['schema_version']))


# если хотите добавить сюда костыль, заведите тикет с описанием
# и добавьте функцию в crutches.py с именем, содержащим очередь и номер тикета
def prepare_for_validation(response):
    if not isinstance(response, dict):
        return

    crutch_HOME_68803(response)

    if 'block' in response and isinstance(response['block'], list):
        for block in response['block']:
            if not isinstance(block, dict):
                continue
            if block.get('id', '') == 'etrains' and block.get('type', '') == 'tv':
                crutch_HOME_68712_1(block)
            if block.get('id', '') == 'tv':
                crutch_HOME_68712_1(block)
            if block.get('id', '') == 'weather':
                crutch_HOME_71272(block)
