# -*- coding: utf-8 -*-
import allure
import pytest

from common.schema import get_schema_validator

from tests.schema.crutches import *
from tests.schema.utils    import *


@pytest.mark.yasm
@allure.feature('api_yabrowser_v2_ios', 'schema_tests_simple')
@allure.story('api_yabrowser_v2_ios_schema')
@pytest.mark.parametrize('params', get_params('tests/schema/api_yabrowser_ios'))
def test_schema_api_yabrowser_v2_ios(params, yasm):
    check_params(params)
    prepare_params(params)

    response = get_response(params)

    schema_path = 'schema/browser_ios/{}/api/search/2/yabrowserapi-response.json'.format(params['schema_version'])
    validator = get_schema_validator(schema_path)
    validate_and_send_signal(response, validator, yasm, 'api_yabrowser_v2_ios_{}'.format(params['schema_version']))
