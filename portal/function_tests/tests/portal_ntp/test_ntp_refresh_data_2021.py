import logging

import json
import allure
import pytest


from common import schema
from common.client import MordaClient
from common.schema import get_schema_validator, validate_schema
from common.geobase import Regions
from common.morda import DesktopMain
logger = logging.getLogger(__name__)

@pytest.mark.yasm
@allure.feature('portal_ntp')
@allure.feature('function_tests_stable')
@allure.story('ntp/refresh_data')
def test_refresh_data_old():
    # Old test
    client = MordaClient(DesktopMain(Regions.MOSCOW))
    validator = get_schema_validator('schema/ntp/refresh/refresh_data.json')
    url = client.make_url('{}/portal/ntp/refresh_data/?madm_mocks=ntp_morda_blocks=ntp_topnews_enabled_mock')
    response = client.request(url=url).send()
    if response.is_ok():
        data = response.json()
        validate_schema(data, validator)


@pytest.mark.yasm
@allure.feature('portal_ntp')
@allure.feature('function_tests_stable')
@allure.story('ntp/refresh_data')
def test_refresh_data():
    validator = get_schema_validator('schema/ntp/refresh/refresh_data2021.json')
    client = MordaClient(DesktopMain(Regions.MOSCOW))
    url = client.make_url("{}/portal/ntp/refresh_data/?tablo2021=1&madm_mocks=ntp_morda_blocks=ntp_topnews_enabled_mock")
    response = client.request(url=url).send()
    if response.is_ok():
        data = response.json()
        validate_schema(data, validator)


@pytest.mark.yasm
@allure.feature('portal_ntp')
@allure.feature('function_tests_stable')
@allure.story('ntp/refresh_data')
def test_topnews_off():
    client = MordaClient(DesktopMain(Regions.MOSCOW))
    url = client.make_url('{}/portal/ntp/refresh_data/?tablo2021=1&madm_mocks=ntp_morda_blocks=ntp_topnews_disabled_mock')
    response = client.request(url=url).send()
    if response.is_ok():
        response = response.json()
        assert "madm_mock_error" not in response, response["madm_mock_error"]
        assert ("Topnews" not in response) or (response["Topnews"]["show"] == 0)


@pytest.mark.yasm
@allure.feature('portal_ntp')
@allure.feature('function_tests_stable')
@allure.story('ntp/refresh_data')
def test_topnews_off_old():
    client = MordaClient(DesktopMain(Regions.MOSCOW))
    url = client.make_url('{}/portal/ntp/refresh_data/?madm_mocks=ntp_morda_blocks=ntp_topnews_disabled_mock')
    response = client.request(url=url).send()
    if response.is_ok():
        response = response.json()
        assert "madm_mock_error" not in response, response["madm_mock_error"]
        assert ("Topnews" not in response) or (response["Topnews"]["show"] == 0)


@pytest.mark.yasm
@allure.feature('portal_ntp')
@allure.feature('function_tests_stable')
@allure.story('ntp/refresh_data')
def test_topnews_on():
    client = MordaClient(DesktopMain(Regions.MOSCOW))
    url = client.make_url('{}/portal/ntp/refresh_data/?tablo2021=1&madm_mocks=ntp_morda_blocks=ntp_topnews_enabled_mock:topnews_special_v2=special_on')
    response = client.request(url=url).send()
    if response.is_ok():
        response = response.json()
        assert "madm_mock_error" not in response, response["madm_mock_error"]
        assert "Topnews" in response
        data = response["Topnews"]
        fields_list = ["href", "id", "save_tab", "show", "special", "tabs", "topnews_stocks", "url_setup_favorite"]
        for field in fields_list:
            assert field in data


@pytest.mark.yasm
@allure.feature('portal_ntp')
@allure.feature('function_tests_stable')
@allure.story('ntp/refresh_data')
def test_topnews_on_old():
    client = MordaClient(DesktopMain(Regions.MOSCOW))
    url = client.make_url('{}/portal/ntp/refresh_data/?madm_mocks=ntp_morda_blocks=ntp_topnews_enabled_mock:topnews_special_v2=special_on')
    response = client.request(url=url).send()
    if response.is_ok():
        response = response.json()
        assert "madm_mock_error" not in response, response["madm_mock_error"]
        assert "Topnews" in response
        data = response["Topnews"]
        fields_list = ["href", "id", "save_tab", "show", "special", "tabs", "topnews_stocks"]
        for field in fields_list:
            assert field in data
