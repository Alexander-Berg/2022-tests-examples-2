# -*- coding: utf-8 -*-
# pylint: disable=too-many-lines
from __future__ import unicode_literals

import copy
import json

import pytest

from taxi_antifraud.clients import fssp
from taxi_antifraud.scoring import scoring_partner as sp
from taxi_antifraud.scoring.common import rules
from taxi_antifraud.scoring.common import scoring_config as sc


FAILED_SPARK_COMMENT = rules.FAILED_SPARK_COMMENT
FAILED_SPARK_RESPONSE_FOR_NEW_PARTNER = {
    'rating': 'Error',
    'reasons': [
        {'rule_id': 'registration_date', 'comment': FAILED_SPARK_COMMENT},
        {'rule_id': 'place_changing', 'comment': FAILED_SPARK_COMMENT},
        {'rule_id': 'reorganization', 'comment': FAILED_SPARK_COMMENT},
        {
            'rule_id': 'defendant_arbitration_cases',
            'comment': FAILED_SPARK_COMMENT,
        },
        {'rule_id': 'frozen_accounts', 'comment': FAILED_SPARK_COMMENT},
        {'rule_id': 'execution_proceedings', 'comment': FAILED_SPARK_COMMENT},
        {'rule_id': 'activeness', 'comment': FAILED_SPARK_COMMENT},
        {'rule_id': 'egrpo_activeness', 'comment': FAILED_SPARK_COMMENT},
        {'rule_id': 'liquidated', 'comment': FAILED_SPARK_COMMENT},
        {'rule_id': 'liquidation', 'comment': FAILED_SPARK_COMMENT},
        {'rule_id': 'liquidation_risk', 'comment': FAILED_SPARK_COMMENT},
        {'rule_id': 'to_liquidate', 'comment': FAILED_SPARK_COMMENT},
        {'rule_id': 'bankruptcy', 'comment': FAILED_SPARK_COMMENT},
        {'rule_id': 'spark_blacklist', 'comment': FAILED_SPARK_COMMENT},
    ],
}
FAILED_SPARK_RESPONSE_FOR_EXISTING_PARTNER = {
    'rating': 'Error',
    'reasons': [
        {'rule_id': 'registration_date', 'comment': FAILED_SPARK_COMMENT},
        {'rule_id': 'place_changing', 'comment': FAILED_SPARK_COMMENT},
        {'rule_id': 'reorganization', 'comment': FAILED_SPARK_COMMENT},
        {
            'rule_id': 'defendant_arbitration_cases',
            'comment': FAILED_SPARK_COMMENT,
        },
        {'rule_id': 'execution_proceedings', 'comment': FAILED_SPARK_COMMENT},
        {'rule_id': 'activeness', 'comment': FAILED_SPARK_COMMENT},
        {'rule_id': 'egrpo_activeness', 'comment': FAILED_SPARK_COMMENT},
        {'rule_id': 'liquidated', 'comment': FAILED_SPARK_COMMENT},
        {'rule_id': 'liquidation', 'comment': FAILED_SPARK_COMMENT},
        {'rule_id': 'liquidation_risk', 'comment': FAILED_SPARK_COMMENT},
        {'rule_id': 'to_liquidate', 'comment': FAILED_SPARK_COMMENT},
        {'rule_id': 'spark_blacklist', 'comment': FAILED_SPARK_COMMENT},
    ],
}
FAILED_FSSP_COMMENT = 'failed to obtain fssp report'
FAILED_FSSP_RESPONSE = {
    'rating': 'B',
    'reasons': [{'rule_id': 'fssp_check', 'comment': FAILED_FSSP_COMMENT}],
}
REQUEST_DATA_LOG_CHECKING = {'company_tin': 111111111}
SCORING_RATING_A = 'A'
SCORING_RATING_B = 'B'
SCORING_RATING_C = 'C'
SCORING_RESULTS_LOG_CHECKING = {
    'rating': 'C',
    'reasons': [
        {'rule_id': 'activeness', 'comment': '<IsActing>false</IsActing>'},
    ],
}
CATEGORIES = ('company', 'entrepreneur')
RELATIONSHIPS = ('partner', 'corp')
CONFIG_TYPES = {
    'partner': 'AFS_PARTNERS_SCORING_RULES',
    'corp': 'AFS_CORPS_SCORING_RULES',
}
API_METHODS = {
    'partner': {
        'company': '/scoring/score_company',
        'entrepreneur': '/scoring/score_entrepreneur',
    },
    'corp': {
        'company': '/scoring/corp/score_company',
        'entrepreneur': '/scoring/corp/score_entrepreneur',
    },
}


@pytest.mark.config(AFS_SCORE_DRIVER={'enabled': True})
def test_scoring_config_load_codegen_context(monkeypatch, web_context):
    assert web_context.config.AFS_SCORE_DRIVER['enabled']
    monkeypatch.setattr(
        sc.ScoringConfig, 'AFS_SCORE_DRIVER', {'enabled': False},
    )
    monkeypatch.setattr(sc.ScoringConfig, 'NEED_LOAD_CODEGEN_CONTEXT', True)
    scoring_config = sc.ScoringConfig(web_context)
    assert web_context.config.AFS_SCORE_DRIVER['enabled']
    assert scoring_config.AFS_SCORE_DRIVER['enabled']


def _in_blacklist_response(field_names):
    return {
        'rating': 'C',
        'reasons': [{'comment': field_names, 'rule_id': 'amocrm_blacklist'}],
    }


@pytest.mark.parametrize(
    'request_data,expected_code,expected_data',
    [
        (
            {'company_tin': 111111511},
            200,
            FAILED_SPARK_RESPONSE_FOR_NEW_PARTNER,
        ),
        (
            {'company_tin': 111111512},
            200,
            FAILED_SPARK_RESPONSE_FOR_NEW_PARTNER,
        ),
        (
            {'company_tin': 111111513},
            200,
            FAILED_SPARK_RESPONSE_FOR_NEW_PARTNER,
        ),
        (
            {'company_tin': 111111514},
            200,
            FAILED_SPARK_RESPONSE_FOR_NEW_PARTNER,
        ),
        (
            {'company_tin': 111111511, 'is_new_partner': True},
            200,
            FAILED_SPARK_RESPONSE_FOR_NEW_PARTNER,
        ),
        (
            {'company_tin': 111111512, 'is_new_partner': True},
            200,
            FAILED_SPARK_RESPONSE_FOR_NEW_PARTNER,
        ),
        (
            {'company_tin': 111111513, 'is_new_partner': True},
            200,
            FAILED_SPARK_RESPONSE_FOR_NEW_PARTNER,
        ),
        (
            {'company_tin': 111111514, 'is_new_partner': True},
            200,
            FAILED_SPARK_RESPONSE_FOR_NEW_PARTNER,
        ),
        (
            {'company_tin': 111111511, 'is_new_partner': False},
            200,
            FAILED_SPARK_RESPONSE_FOR_EXISTING_PARTNER,
        ),
        (
            {'company_tin': 111111512, 'is_new_partner': False},
            200,
            FAILED_SPARK_RESPONSE_FOR_EXISTING_PARTNER,
        ),
        (
            {'company_tin': 111111513, 'is_new_partner': False},
            200,
            FAILED_SPARK_RESPONSE_FOR_EXISTING_PARTNER,
        ),
        (
            {'company_tin': 111111514, 'is_new_partner': False},
            200,
            FAILED_SPARK_RESPONSE_FOR_EXISTING_PARTNER,
        ),
    ],
)
@pytest.mark.now('2018-07-20T14:00:00Z')
async def test_spark(
        monkeypatch,
        web_app_client,
        prepare_zeep_mock_spark,
        request_data,
        expected_code,
        expected_data,
):
    def as_dict(data):
        return {e['rule_id']: e['comment'] for e in data}

    response = await web_app_client.post(
        '/scoring/score_company', data=json.dumps(request_data),
    )
    assert response.status == expected_code
    if expected_data is not None:
        response_json = await response.json()
        assert response_json['rating'] == expected_data['rating']
        assert as_dict(response_json['reasons']) == as_dict(
            expected_data['reasons'],
        )


@pytest.mark.parametrize('rules_enabled', [True, False])
@pytest.mark.parametrize('relationship', ['partner', 'corp'])
@pytest.mark.parametrize(
    'request_data,expected_code,expected_data',
    [
        ({'company_tin': 111111111}, 200, {'rating': 'A', 'reasons': []}),
        (
            {'company_tin': 111111211},
            200,
            {
                'rating': 'A',
                'reasons': [
                    {
                        'comment': '<DateFirstReg>2018-05-01</DateFirstReg>',
                        'rule_id': 'registration_date',
                    },
                ],
            },
        ),
        (
            {'company_tin': 111111212},
            200,
            {
                'rating': 'A',
                'reasons': [
                    {
                        'comment': 'no <DateFirstReg/>',
                        'rule_id': 'registration_date',
                    },
                ],
            },
        ),
        ({'company_tin': 111111222}, 200, {'rating': 'A', 'reasons': []}),
        (
            {'company_tin': 111111231},
            200,
            {
                'rating': 'A',
                'reasons': [
                    {
                        'comment': (
                            '<Year Year="2017">'
                            '<Defendant CasesNumber="0" Sum="1"/>'
                            '</Year>'
                            '<Year Year="2018">'
                            '<Defendant CasesNumber="1" Sum="0"/>'
                            '</Year>'
                        ),
                        'rule_id': 'defendant_arbitration_cases',
                    },
                ],
            },
        ),
        ({'company_tin': 111111232}, 200, {'rating': 'A', 'reasons': []}),
        ({'company_tin': 111111233}, 200, {'rating': 'A', 'reasons': []}),
        ({'company_tin': 111111251}, 200, {'rating': 'A', 'reasons': []}),
        (
            {'company_tin': 111111312},
            200,
            {
                'rating': 'A',
                'reasons': [
                    {
                        'comment': '<DateFirstReg>2018-06-01</DateFirstReg>',
                        'rule_id': 'registration_date',
                    },
                ],
            },
        ),
        (
            {'company_tin': 111111411},
            200,
            {
                'rating': 'C',
                'reasons': [
                    {
                        'comment': '<IsActing>false</IsActing>',
                        'rule_id': 'activeness',
                    },
                ],
            },
        ),
        ({'company_tin': 111111414}, 200, {'rating': 'A', 'reasons': []}),
        ({'company_tin': 111111415}, 200, {'rating': 'A', 'reasons': []}),
        ({'company_tin': 111111416}, 200, {'rating': 'A', 'reasons': []}),
        (
            {'company_tin': 111111421},
            200,
            {
                'rating': 'C',
                'reasons': [
                    {
                        'comment': (
                            '<BankruptcyMessage>'
                            'Azaza'
                            '</BankruptcyMessage>'
                        ),
                        'rule_id': 'bankruptcy',
                    },
                ],
            },
        ),
        (
            {'company_tin': 111111431},
            200,
            {
                'rating': 'C',
                'reasons': [
                    {
                        'comment': '<ListName Id="26" IsNegative="1"/>',
                        'rule_id': 'spark_blacklist',
                    },
                ],
            },
        ),
        ({'company_tin': 111111432}, 200, {'rating': 'A', 'reasons': []}),
        ({'company_tin': 111111451}, 200, _in_blacklist_response('tin')),
        ({'company_tin': 111111452}, 200, _in_blacklist_response('tin')),
        ({'company_name': 'Azaza'}, 200, _in_blacklist_response('name')),
        ({'company_name': 'Az'}, 200, _in_blacklist_response('name')),
        (
            {'contact_email': '79161111451@mail_server.ru'},
            200,
            _in_blacklist_response('email'),
        ),
        ({'contact_phone': 79161111451}, 200, _in_blacklist_response('phone')),
        (
            {
                'company_tin': 111111111,
                'company_name': 'Azaza',
                'contact_email': '79161111451@mail_server.ru',
                'contact_phone': 79161111452,
            },
            200,
            _in_blacklist_response('email, name, phone'),
        ),
        (
            {'company_name': 'Infernia Overkill'},
            200,
            {'rating': 'B', 'reasons': []},
        ),
        (
            {'company_tin': 111111422},
            200,
            {
                'rating': 'C',
                'reasons': [
                    {
                        'comment': (
                            '<EGRULLikvidation>'
                            'EGRULLikvidationTestMessage'
                            '</EGRULLikvidation>'
                        ),
                        'rule_id': 'to_liquidate',
                    },
                ],
            },
        ),
    ],
)
@pytest.mark.now('2018-07-20T14:00:00Z')
async def test_score_all_company_spark(
        monkeypatch,
        web_app_client,
        prepare_zeep_mock_spark,
        rules_enabled,
        relationship,
        request_data,
        expected_code,
        expected_data,
):
    if not rules_enabled:
        expected_data = {'rating': 'B', 'reasons': []}

    await _check_scoring(
        relationship,
        'company',
        monkeypatch,
        web_app_client,
        False,
        rules_enabled,
        request_data,
        expected_code,
        expected_data,
    )


@pytest.mark.parametrize('rules_enabled', [True, False])
@pytest.mark.parametrize(
    'request_data,expected_code,expected_data',
    [
        (
            {'company_tin': 111111421, 'is_new_partner': True},
            200,
            {
                'rating': 'C',
                'reasons': [
                    {
                        'comment': (
                            '<BankruptcyMessage>'
                            'Azaza'
                            '</BankruptcyMessage>'
                        ),
                        'rule_id': 'bankruptcy',
                    },
                ],
            },
        ),
        (
            {'company_tin': 111111421, 'is_new_partner': False},
            200,
            {'rating': 'A', 'reasons': []},
        ),
        (
            {'company_tin': 111111451, 'is_new_partner': True},
            200,
            _in_blacklist_response('tin'),
        ),
        (
            {'company_tin': 111111451, 'is_new_partner': False},
            200,
            {'rating': 'A', 'reasons': []},
        ),
        (
            {'company_tin': 111111452, 'is_new_partner': True},
            200,
            _in_blacklist_response('tin'),
        ),
        (
            {'company_tin': 111111452, 'is_new_partner': False},
            200,
            {'rating': 'A', 'reasons': []},
        ),
        (
            {'company_name': 'Azaza', 'is_new_partner': True},
            200,
            _in_blacklist_response('name'),
        ),
        (
            {'company_name': 'Azaza', 'is_new_partner': False},
            200,
            {'rating': 'B', 'reasons': []},
        ),
        (
            {'company_name': 'Az', 'is_new_partner': True},
            200,
            _in_blacklist_response('name'),
        ),
        (
            {'company_name': 'Az', 'is_new_partner': False},
            200,
            {'rating': 'B', 'reasons': []},
        ),
        (
            {
                'contact_email': '79161111451@mail_server.ru',
                'is_new_partner': True,
            },
            200,
            _in_blacklist_response('email'),
        ),
        (
            {
                'contact_email': '79161111451@mail_server.ru',
                'is_new_partner': False,
            },
            200,
            {'rating': 'B', 'reasons': []},
        ),
        (
            {'contact_phone': 79161111451, 'is_new_partner': True},
            200,
            _in_blacklist_response('phone'),
        ),
        (
            {'contact_phone': 79161111451, 'is_new_partner': False},
            200,
            {'rating': 'B', 'reasons': []},
        ),
        (
            {
                'company_tin': 111111111,
                'company_name': 'Azaza',
                'contact_email': '79161111451@mail_server.ru',
                'contact_phone': 79161111452,
                'is_new_partner': True,
            },
            200,
            _in_blacklist_response('email, name, phone'),
        ),
        (
            {
                'company_tin': 111111111,
                'company_name': 'Azaza',
                'contact_email': '79161111451@mail_server.ru',
                'contact_phone': 79161111452,
                'is_new_partner': False,
            },
            200,
            {'rating': 'A', 'reasons': []},
        ),
    ],
)
@pytest.mark.now('2018-07-20T14:00:00Z')
async def test_score_all_company_spark_as_partner(
        monkeypatch,
        web_app_client,
        prepare_zeep_mock_spark,
        rules_enabled,
        request_data,
        expected_code,
        expected_data,
):
    if not rules_enabled:
        expected_data = {'rating': 'B', 'reasons': []}

    await _check_scoring(
        'partner',
        'company',
        monkeypatch,
        web_app_client,
        False,
        rules_enabled,
        request_data,
        expected_code,
        expected_data,
    )


@pytest.mark.parametrize('rules_enabled', [True, False])
@pytest.mark.parametrize(
    'request_data,expected_code,expected_data',
    [({'company_tin': 111111221}, 200, {'rating': 'A', 'reasons': []})],
)
@pytest.mark.now('2018-07-20T14:00:00Z')
async def test_score_corp_company_spark(
        monkeypatch,
        web_app_client,
        prepare_zeep_mock_spark,
        rules_enabled,
        request_data,
        expected_code,
        expected_data,
):
    if not rules_enabled:
        expected_data = {'rating': 'B', 'reasons': []}

    await _check_scoring(
        'corp',
        'company',
        monkeypatch,
        web_app_client,
        False,
        rules_enabled,
        request_data,
        expected_code,
        expected_data,
    )


@pytest.mark.parametrize('rules_enabled', [True, False])
@pytest.mark.parametrize(
    'request_data,expected_code,expected_data',
    [
        (
            {'company_tin': 111111221, 'is_new_partner': True},
            400,
            {
                'error': (
                    'Parameter \'is_new_partner\' is not supported '
                    'for \'scoring/corp/...\' API methods'
                ),
            },
        ),
        (
            {'company_tin': 111111221, 'is_new_partner': False},
            400,
            {
                'error': (
                    'Parameter \'is_new_partner\' is not supported '
                    'for \'scoring/corp/...\' API methods'
                ),
            },
        ),
    ],
)
@pytest.mark.now('2018-07-20T14:00:00Z')
async def test_score_corp_company_spark_unsupported(
        monkeypatch,
        web_app_client,
        prepare_zeep_mock_spark,
        rules_enabled,
        request_data,
        expected_code,
        expected_data,
):
    await _check_scoring(
        'corp',
        'company',
        monkeypatch,
        web_app_client,
        False,
        rules_enabled,
        request_data,
        expected_code,
        expected_data,
    )


@pytest.mark.parametrize('rules_enabled', [True, False])
@pytest.mark.parametrize(
    'request_data,expected_code,expected_data',
    [
        (
            {'entrepreneur_tin': 22111111111},
            200,
            {'rating': 'A', 'reasons': []},
        ),
        (
            {'entrepreneur_tin': 22111111112},
            200,
            {
                'rating': 'C',
                'reasons': [
                    {
                        'comment': (
                            '<Status IsActing="0" '
                            'Text="Не действующее" Code="24" '
                            'Date="2018-03-30"/>'
                        ),
                        'rule_id': 'activeness',
                    },
                ],
            },
        ),
        (
            {'entrepreneur_tin': 22111111113},
            200,
            {
                'rating': 'C',
                'reasons': [
                    {
                        'comment': (
                            '<BankruptcyMessage>Oops</BankruptcyMessage>'
                        ),
                        'rule_id': 'bankruptcy',
                    },
                ],
            },
        ),
        (
            {'entrepreneur_tin': 22111111113, 'is_new_partner': True},
            200,
            {
                'rating': 'C',
                'reasons': [
                    {
                        'comment': (
                            '<BankruptcyMessage>Oops</BankruptcyMessage>'
                        ),
                        'rule_id': 'bankruptcy',
                    },
                ],
            },
        ),
        (
            {'entrepreneur_tin': 22111111113, 'is_new_partner': False},
            200,
            {'rating': 'A', 'reasons': []},
        ),
        (
            {'entrepreneur_name': 'Infernia Overkill'},
            200,
            {'rating': 'B', 'reasons': []},
        ),
    ],
)
@pytest.mark.now('2018-07-20T14:00:00Z')
async def test_score_entrepreneur_spark(
        monkeypatch,
        web_app_client,
        prepare_zeep_mock_spark,
        rules_enabled,
        request_data,
        expected_code,
        expected_data,
):
    if not rules_enabled:
        expected_data = {'rating': 'B', 'reasons': []}

    await _check_scoring(
        'partner',
        'entrepreneur',
        monkeypatch,
        web_app_client,
        False,
        rules_enabled,
        request_data,
        expected_code,
        expected_data,
    )


@pytest.mark.parametrize('rules_enabled', [True, False])
@pytest.mark.parametrize(
    'request_data,expected_code,expected_data',
    [
        (
            {'entrepreneur_tin': 22111111111, 'is_new_partner': True},
            400,
            {
                'error': (
                    'Parameter \'is_new_partner\' is not supported '
                    'for \'scoring/corp/...\' API methods'
                ),
            },
        ),
        (
            {'entrepreneur_tin': 22111111111, 'is_new_partner': False},
            400,
            {
                'error': (
                    'Parameter \'is_new_partner\' is not supported '
                    'for \'scoring/corp/...\' API methods'
                ),
            },
        ),
    ],
)
@pytest.mark.now('2018-07-20T14:00:00Z')
async def test_score_corp_entrepreneur_spark_unsupported(
        monkeypatch,
        web_app_client,
        prepare_zeep_mock_spark,
        rules_enabled,
        request_data,
        expected_code,
        expected_data,
):
    await _check_scoring(
        'corp',
        'entrepreneur',
        monkeypatch,
        web_app_client,
        False,
        rules_enabled,
        request_data,
        expected_code,
        expected_data,
    )


@pytest.mark.parametrize(
    'region_name, company_name, expected_scoring',
    [
        ('Саратовская область', '"ОАО Маск"', FAILED_FSSP_RESPONSE),
        ('Волгоградская область', 'ООО Полис', FAILED_FSSP_RESPONSE),
        ('Волгоградская область', 'Зэ Бэст Компани', FAILED_FSSP_RESPONSE),
        ('Москва', 'Another One', FAILED_FSSP_RESPONSE),
        ('Москва', 'Фирма что надо', FAILED_FSSP_RESPONSE),
        ('Волгоградская область', 'Pineapple', FAILED_FSSP_RESPONSE),
        ('Волгоградская область', 'Maple', FAILED_FSSP_RESPONSE),
    ],
)
@pytest.mark.now('2018-07-20T14:00:00Z')
async def test_fssp_failures(
        monkeypatch,
        web_app_client,
        prepare_zeep_mock_for_fssp,
        prepare_mock_aiohttp_for_fssp,
        region_name,
        company_name,
        expected_scoring,
):
    _add_rule_config(monkeypatch, 'partner', 'company', 'fssp_check')

    # pylint: disable=protected-access
    scoring = await sp._FSSPRulesEngineForCompany.apply_rules(
        fssp.Client('test_api_key'),
        region_name=region_name,
        company_name=company_name,
        rules_config=sc.ScoringConfig.AFS_PARTNERS_SCORING_RULES,
    )

    assert scoring == expected_scoring


@pytest.mark.parametrize('rules_enabled', [True, False])
@pytest.mark.parametrize(
    'request_data,expected_code,expected_data',
    [
        # test when SPARK scoring is C and FSSP has no effect on common result
        (
            {'company_tin': 2222222241},
            200,
            {
                'rating': 'C',
                'reasons': [
                    {
                        'comment': '<IsActing>false</IsActing>',
                        'rule_id': 'activeness',
                    },
                    {
                        'comment': '<EGRPOIncluded>false</EGRPOIncluded>',
                        'rule_id': 'egrpo_activeness',
                    },
                    {'comment': FAILED_FSSP_COMMENT, 'rule_id': 'fssp_check'},
                    {
                        'comment': '<DateFirstReg>2018-01-25</DateFirstReg>',
                        'rule_id': 'registration_date',
                    },
                ],
            },
        ),
        # test when SPARK scoring is A and FSSP scoring is B
        (
            {'company_tin': 2222222223},
            200,
            {
                'rating': 'B',
                'reasons': [
                    {
                        'rule_id': 'defendant_arbitration_cases',
                        'comment': (
                            '<Year Year="2017"><Defendant '
                            'CasesNumber="2" Sum="51948"/></Year>'
                            '<Year Year="2018"><Defendant '
                            'CasesNumber="3" Sum="48890"/></Year>'
                        ),
                    },
                    {
                        'rule_id': 'fssp_check',
                        'comment': (
                            '[{\'exe_production\': \'27122/12/20/74 '
                            'от 24.04.2012\', \'name\': '
                            '"ООО \'КОМПАНИЯ\', РОССИЯ,454108,'
                            'ЧЕЛЯБИНСКАЯ ОБЛ, ,ЧЕЛЯБИНСК Г"}]'
                        ),
                    },
                ],
            },
        ),
    ],
)
@pytest.mark.now('2018-07-20T14:00:00Z')
async def test_score_company_fssp(
        monkeypatch,
        web_app_client,
        prepare_zeep_mock_for_fssp,
        prepare_mock_aiohttp_for_fssp,
        rules_enabled,
        request_data,
        expected_code,
        expected_data,
):
    if not rules_enabled:
        expected_data = {'rating': 'B', 'reasons': []}

    await _check_scoring(
        'partner',
        'company',
        monkeypatch,
        web_app_client,
        True,
        rules_enabled,
        request_data,
        expected_code,
        expected_data,
    )


@pytest.mark.parametrize('rules_enabled', [True, False])
@pytest.mark.parametrize(
    'request_data,expected_code,expected_data',
    [
        # test when SPARK scoring is A and FSSP scoring is A
        (
            {'entrepreneur_tin': 222222222222},
            200,
            {
                'rating': 'B',
                'reasons': [
                    {'comment': FAILED_FSSP_COMMENT, 'rule_id': 'fssp_check'},
                    {
                        'rule_id': 'main_activity_type',
                        'comment': (
                            '<OKVED Code="74.11" '
                            'Name="Деятельность в области права" '
                            'IsMain="true"/><OKVED Code="69.10" '
                            'Name="Деятельность в области права" '
                            'IsMain="true"/>'
                        ),
                    },
                ],
            },
        ),
        # test when SPARK scoring is B and FSSP scoring is B
        (
            {'entrepreneur_tin': 222222222233},
            200,
            {
                'rating': 'B',
                'reasons': [
                    {
                        'rule_id': 'fssp_check',
                        'comment': (
                            '[{\'exe_production\': \'721/13/19/01\', '
                            '\'name\': \'ИП Налча\', \'subject\': '
                            '\'Задолженность\'}]'
                        ),
                    },
                    {
                        'rule_id': 'main_activity_type',
                        'comment': 'no <OKVED IsMain="true"/>',
                    },
                    {
                        'rule_id': 'registration_date',
                        'comment': 'no <DateReg/>',
                    },
                ],
            },
        ),
        # test when SPARK scoring is B and FSSP scoring is A
        (
            {'entrepreneur_tin': 222222222232},
            200,
            {
                'rating': 'B',
                'reasons': [
                    {'rule_id': 'fssp_check', 'comment': '[]'},
                    {
                        'rule_id': 'main_activity_type',
                        'comment': 'no <OKVED IsMain="true"/>',
                    },
                    {
                        'rule_id': 'registration_date',
                        'comment': 'no <DateReg/>',
                    },
                ],
            },
        ),
    ],
)
@pytest.mark.now('2018-07-20T14:00:00Z')
async def test_score_entrepreneur_fssp(
        monkeypatch,
        web_app_client,
        prepare_zeep_mock_for_fssp,
        prepare_mock_aiohttp_for_fssp,
        rules_enabled,
        request_data,
        expected_code,
        expected_data,
):
    if not rules_enabled:
        expected_data = {'rating': 'B', 'reasons': []}

    await _check_scoring(
        'partner',
        'entrepreneur',
        monkeypatch,
        web_app_client,
        True,
        rules_enabled,
        request_data,
        expected_code,
        expected_data,
    )


@pytest.mark.parametrize(
    'first_report_rating,second_report_rating,expected_report_rating',
    [
        (SCORING_RATING_A, SCORING_RATING_A, SCORING_RATING_A),
        (SCORING_RATING_A, SCORING_RATING_B, SCORING_RATING_B),
        (SCORING_RATING_B, SCORING_RATING_B, SCORING_RATING_B),
        (SCORING_RATING_A, SCORING_RATING_C, SCORING_RATING_C),
        (SCORING_RATING_B, SCORING_RATING_A, SCORING_RATING_B),
        (SCORING_RATING_B, SCORING_RATING_C, SCORING_RATING_C),
        (SCORING_RATING_C, SCORING_RATING_A, SCORING_RATING_C),
        (SCORING_RATING_C, SCORING_RATING_B, SCORING_RATING_C),
        (SCORING_RATING_C, SCORING_RATING_C, SCORING_RATING_C),
    ],
)
@pytest.mark.parametrize(
    'first_report,second_report,expected_report',
    [
        (
            {
                'reasons': [
                    {
                        'rule_id': 'first_rule_first_report',
                        'comment': (
                            '{applying first_rule_first_report ' 'results}'
                        ),
                    },
                    {
                        'rule_id': 'second_rule_first_report',
                        'comment': (
                            '{applying second_rule_first_report ' 'results}'
                        ),
                    },
                ],
            },
            {
                'reasons': [
                    {
                        'rule_id': 'first_rule_second_report',
                        'comment': (
                            '{applying first_rule_second_report ' 'results}'
                        ),
                    },
                ],
            },
            {
                'reasons': [
                    {
                        'rule_id': 'first_rule_first_report',
                        'comment': (
                            '{applying first_rule_first_report ' 'results}'
                        ),
                    },
                    {
                        'rule_id': 'second_rule_first_report',
                        'comment': (
                            '{applying second_rule_first_report ' 'results}'
                        ),
                    },
                    {
                        'rule_id': 'first_rule_second_report',
                        'comment': (
                            '{applying first_rule_second_report ' 'results}'
                        ),
                    },
                ],
            },
        ),
    ],
)
def test_join_reports(
        first_report_rating,
        first_report,
        second_report_rating,
        second_report,
        expected_report_rating,
        expected_report,
):
    first_report['rating'] = first_report_rating
    second_report['rating'] = second_report_rating
    expected_report['rating'] = expected_report_rating

    # pylint: disable=protected-access
    joined_report = sp._join_scoring_reports(first_report, second_report)
    assert joined_report == expected_report


async def _check_scoring(
        relationship,
        category,
        monkeypatch,
        web_app_client,
        fssp_enabled,
        rules_enabled,
        request_data,
        expected_code,
        expected_data,
):
    api_method = API_METHODS[relationship][category]

    if not rules_enabled:
        _disable_rules(monkeypatch, relationship, category)
    elif fssp_enabled:
        _add_rule_config(monkeypatch, relationship, category, 'fssp_check')

    response = await web_app_client.post(
        api_method, data=json.dumps(request_data),
    )

    assert response.status == expected_code
    assert await response.json() == expected_data


def _add_rule_config(monkeypatch, relationship, category, rule_name):
    adder = _RulesConfigAdder(rule_name)
    _update_rules_config(monkeypatch, relationship, category, adder.add)


def _disable_rules(monkeypatch, relationship, category):
    _update_rules_config(
        monkeypatch, relationship, category, _make_enable_false,
    )


def _update_rules_config(monkeypatch, relationship, category, change_config):
    config_name = CONFIG_TYPES[relationship]
    new_config = copy.deepcopy(vars(sc.ScoringConfig)[config_name])
    change_config(new_config, category)
    monkeypatch.setattr(sc.ScoringConfig, config_name, new_config)


class _RulesConfigAdder:
    def __init__(self, rule_name):
        self._rule_name = rule_name

    def add(self, config_dict, category):
        config_dict[self._rule_name] = {
            'company': {'enabled': category == 'company'},
            'entrepreneur': {'enabled': category == 'entrepreneur'},
        }


def _make_enable_false(config_dict, category):
    for key, value in config_dict.items():
        if key == 'enabled':
            config_dict[key] = False
        elif isinstance(value, dict) and (
            key not in CATEGORIES or key == category
        ):
            _make_enable_false(value, category)
