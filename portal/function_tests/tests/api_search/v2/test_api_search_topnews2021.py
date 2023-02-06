import logging

import json
import allure
import pytest


from common import schema, env
from common.client import MordaClient
from common.schema import get_schema_validator, validate_schema
from common.geobase import Regions

logger = logging.getLogger(__name__)

#  use rc as env. There is no apphost on dev-inst

app_info = {
    'android': ['21060600'],
    'iphone': ['91000000']
}

#  Login and password for TT test.
TOKEN = "oauth_token@blackbox_thelostdesutestacc"
def gen_params(**kwargs):
    params = []
    for platform, versions in app_info.iteritems():
        params.extend([dict(app_version=version, app_platform=platform, geo='213', lang='ru-RU', processAssist='1',
                            uuid='0f730a00ff8a443ea2db355519bdd290', zen_extensions='true', informersCard='2',
                            bs_promo='1', **kwargs)
                       for version in versions])
    return params



def gen_params_for_schema_test(**kwargs):
    params = gen_params(ab_flags='topnews_extended', **kwargs)
    params.extend(gen_params(**kwargs))
    return params

schema_path = 'schema/api/search/2/searchapi-response-test.json'


@pytest.mark.yasm
@allure.feature('function_tests_stable')
@allure.testcase('https://testpalm.yandex-team.ru/testcase/home_all-1092')
@pytest.mark.parametrize('params', gen_params_for_schema_test())
def test_topnews_schema_div(params):
    client = MordaClient(env=env.morda_env())
    response = client.api_search_2(**params).send()
    assert response.is_ok(), 'Failed to get api-search response'
    data = response.json()
    validator = get_schema_validator(schema_path)
    validate_schema(data, validator)


#HOME-77182
#@pytest.mark.yasm
#@allure.feature('function_tests_stable')
#@allure.testcase('https://testpalm.yandex-team.ru/testcase/home_all-1092')
@pytest.mark.parametrize('params', gen_params(ab_flags='topnews_extended=1:topnews_summary:topnews_extended_from_avocado=0',
                                              topnews_extra_params='flags=yxnews_tops_export_test_official_comments=1',
                                              cleanvars='Topnews', httpmock="topnews@summary_on"))
def test_summary_feature(params):
    client = MordaClient(env=env.morda_env())
    response = client.api_search_2(**params).send()
    assert response.is_ok(), 'Failed to get api-search response'
    data = response.json()
    topnews = data['raw_data']['topnews_extended']['blockData']['blocks']['topnews']['rubrics']
    is_any_summary = False
    for i in range(len(topnews)):
        for story in topnews[i]['stories']:
            if 'summary' in story:
                for summary in story['summary']:
                    assert 'agency_name' in summary, "summary agency_name is empty"
                    assert 'agency_url' in summary, "summary agency_url is empty"
                    assert 'text' in summary, "summary text is empty"
                    is_any_summary = True
    assert is_any_summary


@pytest.mark.yasm
@allure.feature('function_tests_stable')
@allure.testcase('https://testpalm.yandex-team.ru/testcase/home_all-1092')
@pytest.mark.parametrize('params', gen_params(ab_flags='topnews_extended=1:topnews_official_comments:topnews_extended_from_avocado=0',
                                              topnews_extra_params='flags=yxnews_tops_export_test_official_comments=1',
                                              cleanvars='Topnews'))
def test_official_comments_feature(params):
    client = MordaClient(env=env.morda_env())
    response = client.api_search_2(**params).send()
    assert response.is_ok(), 'Failed to get api-search response'
    data = response.json()
    is_any_off_comment = False
    topnews = data['raw_data']['topnews_extended']['blockData']['blocks']['topnews']['rubrics']
    for rubric in topnews:
        for story in rubric['stories']:
            if 'official_comments' in story:
                is_any_off_comment = True
                message = story['official_comments'][0]['message']
                assert 'company_url' in message
                assert 'company_logo' in message
                assert 'url' in message
                assert 'company_title' in message
                assert 'text' in message
                assert 'agency_name' in message
    assert is_any_off_comment


@pytest.mark.yasm
@allure.feature('function_tests_stable')
@allure.testcase('https://testpalm.yandex-team.ru/testcase/home_all-1092')
@pytest.mark.parametrize('params', gen_params(ab_flags='topnews_extended=1:topnews_extended_from_avocado=0',
                                              httpmock='topnews@news_with_disclaimer_allowed',
                                              cleanvars='Topnews'))
def test_favorite_feature(params):
    client = MordaClient(env=env.morda_env())
    response = client.api_search_2(**params).send()
    assert response.is_ok(), 'Failed to get api-search response'
    data = response.json()
    topnews = data['raw_data']['topnews_extended']['blockData']['blocks']['topnews']['rubrics']
    for story in topnews[0]['stories']:
        assert 'is_favorite' in story
        assert story['is_favorite'] == 1


@pytest.mark.yasm
@allure.feature('function_tests_stable')
@allure.testcase('https://testpalm.yandex-team.ru/testcase/home_all-1092')
@pytest.mark.parametrize('params', gen_params(ab_flags='topnews_extended=1:geohelper_extra_stories=1:topnews_extended_from_avocado=0',
                                              httpmock='topnews@news_with_disclaimer_allowed',
                                              cleanvars='Topnews'))
def test_extra_stories_feature(params):
    client = MordaClient(env=env.morda_env())
    response = client.api_search_2(**params).send()
    assert response.is_ok(), 'Failed to get api-search response'
    data = response.json()
    topnews = data['raw_data']['topnews_extended']['blockData']['blocks']['topnews']['rubrics']
    for rubric in topnews:
        for story in rubric['stories']:
            if 'extra_stories' in story:
                for ex_story in story['extra_stories']:
                    assert 'agency' in ex_story
                    assert 'name' in ex_story['agency']
                    assert 'logo' in ex_story['agency']
                    assert 'id' in ex_story['agency']
                    assert 'url' in ex_story
                    assert 'title' in ex_story

@pytest.mark.yasm
@allure.feature('function_tests_stable')
@allure.testcase('https://testpalm.yandex-team.ru/testcase/home_all-1092')
@pytest.mark.parametrize('params', gen_params(ab_flags='news_degradation=1:topnews_extended=1:topnews_extended_from_avocado=0',
                                              cleanvars='Topnews'))
def test_degradation(params):
    client = MordaClient(env=env.morda_env())
    response = client.api_search_2(**params).send()
    assert response.is_ok(), 'Failed to get api-search response'
    data = response.json()
    topnews = data['raw_data']['topnews_extended']['blockData']['blocks']['topnews']['rubrics']
    for rubric in topnews:
        for story in rubric['stories']:
            assert 'extra_stories' not in story

@pytest.mark.yasm
@allure.feature('function_tests_stable')
@allure.testcase('https://testpalm.yandex-team.ru/testcase/home_all-1092')
@pytest.mark.parametrize('params', gen_params(ab_flags='news_degradation=0:topnews_extended=1:tourist_blocks=1:news_tourist_tab=1:topnews_extended_from_avocado=0',
                                              cleanvars='Topnews', geo_by_settings=2, test_auth=TOKEN, madm_mocks='tourist_blocks=tourist_blocks.default',
                                              madm_options='enable_new_tourist_morda=0:new_tourist_morda_testids=0'))
def test_tourist(params):
    client = MordaClient(env=env.morda_env())
    response = client.api_search_2(**params).send()
    data = response.json()
    topnews = data['raw_data']['topnews_extended']['blockData']['blocks']['topnews']['rubrics']
    is_spb = False
    is_moscow = False
    for rubric in topnews:
        if rubric["alias"] == "Saint_Petersburg":
            is_spb = True
        if rubric["alias"] == "Moscow":
            is_moscow = True
    assert is_spb, "My city is not in response"
    assert is_moscow, "Touristic Tab is not in response"

@pytest.mark.yasm
@allure.feature('function_tests_stable')
@allure.testcase('https://testpalm.yandex-team.ru/testcase/home_all-1092')
@pytest.mark.parametrize('params', gen_params(ab_flags="topnews_extended=1:news_degradation=0:geohelper_extra_stories=1:topnews_extended_from_avocado=0",
                                              httpmock='topnews@news_with_disclaimer_allowed_hot',
                                              cleanvars='Topnews', geo_by_settings=2, test_auth=TOKEN))
def test_hot(params):
    client = MordaClient(env=env.morda_env())
    response = client.api_search_2(**params).send()
    data = response.json()
    topnews = data['raw_data']['topnews_extended']['blockData']['blocks']['topnews']['rubrics']
    is_any_hot = False
    for rubric in topnews:
        for story in rubric["stories"]:
            if "is_hot" in story and story["is_hot"] == 1:
                is_any_hot = True
            if "extra_stories" in story:
                for ex_story in story["extra_stories"]:
                    if "is_hot" in ex_story and ex_story["is_hot"] == 1:
                        is_any_hot = True
    assert is_any_hot, "No hot news"
