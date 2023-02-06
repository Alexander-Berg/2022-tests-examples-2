# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import copy
import json

import pytest

from taxi_antifraud.scoring import scoring_driver as sd
from taxi_antifraud.scoring.common import scoring_config as sc
from test_taxi_antifraud import conftest

_SERVICE_CONFIGS = {
    'scoring_studio': {'url': conftest.SCORING_STUDIO_URL_TEST},
    'sum_and_substance': {
        'url': conftest.SUM_AND_SUBSTANCE_URL_TEST,
        'test_key': conftest.SCORING_STUDIO_API_KEY_TEST,
    },
}


@pytest.mark.parametrize(
    'request_data,expected_code,expected_body',
    [
        (
            # ok driver (cached)
            {
                'last_name': 'фамилия',
                'first_name': 'имя',
                'middle_name': 'отчество',
                'birth_date': '1987-01-26',
                'driver_license_country': 'RUS',
                'driver_license_series': '5006',
                'driver_license_number': '363067',
                'driver_license_issue_date': '2010-03-13',
                'park_zone': 'геозона',
            },
            503,
            {'error': 'Handler is off (AFS_SCORE_DRIVER.enabled is false)'},
        ),
    ],
)
@pytest.mark.parametrize(
    'service_type', ['sum_and_substance', 'scoring_studio'],
)
@pytest.mark.now('2018-07-20T14:00:00Z')
async def test_disabled(
        monkeypatch,
        web_app_client,
        prepare_scoring_services_mock,
        request_data,
        expected_code,
        expected_body,
        service_type,
):
    _set_config(monkeypatch, service_type=service_type, enabled=False)

    response = await web_app_client.post(
        '/scoring/score_driver', data=json.dumps(request_data),
    )
    assert response.status == expected_code

    assert await response.json() == expected_body


@pytest.mark.parametrize(
    'request_data,' 'expected_data,' 'expected_data_2,' 'expected_data_3',
    [
        (
            # ok driver (cached)
            {
                'last_name': 'фамилия',
                'first_name': 'имя',
                'middle_name': 'отчество',
                'birth_date': '1987-01-26',
                'driver_license_series': '5006',
                'driver_license_number': '363067',
                'driver_license_issue_date': '2010-03-13',
                'park_zone': 'геозона',
            },
            {'scoring_id': '78b446cf66814e3c5b065e583409725ccf03e82a@геозона'},
            {
                # 'details': None,
                'result': 'positive',
            },
            None,
        ),
        (
            # not cached
            {
                'last_name': 'ф',
                'first_name': 'и',
                'middle_name': 'о',
                'birth_date': '1987-01-26',
                'driver_license_series': '1111',
                'driver_license_number': '222222',
                'driver_license_issue_date': '2010-03-13',
                'park_zone': 'геозона',
            },
            {'scoring_id': '353f3b6ea671dc583f36efead5bca4ac445566e2@геозона'},
            {'result': 'pending'},
            {
                # 'details': None,
                'result': 'positive',
            },
        ),
        (
            # bad driver (cached)
            {
                'last_name': 'ГОЛОВКО',
                'first_name': 'МАКСИМ',
                'middle_name': 'ГРИГОРЬЕВИЧ',
                'birth_date': '1987-01-26',
                'driver_license_series': '55BA',
                'driver_license_number': '401919',
                'driver_license_issue_date': '2010-03-09',
                'park_zone': 'newvasyuki',
            },
            {
                'scoring_id': (
                    'bb673af29383c518705e51eaee6d204945fb411f@newvasyuki'
                ),
            },
            {
                'details': {'factors': ['inconsistent birth date']},
                'result': 'negative',
            },
            None,
        ),
        (
            # very bad driver (initial request cached)
            {
                'last_name': 'дёминов',
                'first_name': 'лев',
                'middle_name': 'владимирович',
                'birth_date': '1990-05-28',
                'driver_license_country': 'RUS',
                'driver_license_series': '4632',
                'driver_license_number': '038294',
                'driver_license_issue_date': '2017-09-23',
                'park_zone': 'uryupinsk',
            },
            {
                'scoring_id': (
                    '3fb3ead0e0307b4e1eed96fd433050f1920e0559@uryupinsk'
                ),
            },
            [
                {
                    'details': {
                        'factors': [
                            'criminal',
                            'license ban count: 1',
                            'administrative',
                            'credit blacklist',
                        ],
                    },
                    'result': 'negative',
                },
                {
                    'details': {'factors': ['DOCUMENT_TEMPLATE', 'FORGERY']},
                    'result': 'negative',
                },
            ],
            None,
        ),
        (
            # ok driver (not cached)
            {
                'last_name': 'Незнакомка',
                'first_name': 'Красавица',
                'middle_name': 'Таинственная',
                'birth_date': '1995-01-23',
                'driver_license_series': 'L0V3',
                'driver_license_number': 'LT3LT3',
                'driver_license_issue_date': '2018-04-01',
                'park_zone': 'moscow',
            },
            {'scoring_id': '9f77d34b0d76aba701fed4e8f8d5a78390632d80@moscow'},
            {
                # 'details': None,
                'result': 'positive',
            },
            None,
        ),
        (
            # race condition test (record in db, no request_id yet)
            {
                'last_name': 'race',
                'first_name': 'condition',
                'middle_name': 'example',
                'birth_date': '2000-01-01',
                'driver_license_series': 'XXX0',
                'driver_license_number': '777777',
                'driver_license_issue_date': '2011-11-11',
                'park_zone': 'montecarlo',
            },
            {
                'scoring_id': (
                    '7756a0bcc50d1081714a399a5bf2e1f33debbcab@montecarlo'
                ),
            },
            {'result': 'pending'},
            [
                {
                    'details': {'factors': ['license ban count: 1']},
                    'result': 'negative',
                },
                {'details': {'factors': ['FORGERY']}, 'result': 'negative'},
            ],
        ),
    ],
)
@pytest.mark.parametrize(
    'service_type', ['sum_and_substance', 'scoring_studio'],
)
@pytest.mark.now('2018-07-20T14:00:00Z')
@pytest.mark.skip(reason='it is broken and unused')
async def test_score_driver(
        stq3_context,
        monkeypatch,
        web_app_client,
        prepare_scoring_services_mock,
        prepare_scoring_callback_mock,
        request_data,
        expected_data,
        expected_data_2,
        expected_data_3,
        service_type,
):
    _set_config(monkeypatch, service_type=service_type, enabled=True)
    _set_test_scoring_zones(monkeypatch)

    # 1) send driver data
    response = await web_app_client.post(
        '/scoring/score_driver', data=json.dumps(request_data),
    )
    assert response.status == 200

    # 2) get scoring_id from response
    scoring_id_json = await response.json()
    _assert_one_of(scoring_id_json, expected_data)

    # 3) poll for scoring result
    result_response = await web_app_client.post(
        '/scoring/score_driver_result', data=json.dumps(scoring_id_json),
    )
    assert result_response.status == 200
    result = await result_response.json()
    _assert_one_of(result, expected_data_2)

    # if result pending ...
    if result['result'] == 'pending' and expected_data_3:
        assert conftest.ScoringCallbackMock.get_call_count() == 0

        # 4) call stq task
        await sd.score_driver_poll(
            stq3_context, scoring_id_json['scoring_id'], log_extra=None,
        )
        # verify callback invoked
        assert conftest.ScoringCallbackMock.get_call_count() == 1

        # 5) poll for final result
        final_result_response = await web_app_client.post(
            '/scoring/score_driver_result', data=json.dumps(scoring_id_json),
        )
        # verify final result
        assert final_result_response.status == 200
        final_result = await final_result_response.json()
        _assert_one_of(final_result, expected_data_3)


def _assert_one_of(actual, expected):
    if isinstance(expected, list):
        assert actual in expected
    else:
        assert actual == expected


def _set_test_scoring_zones(monkeypatch):
    zone_config = {
        'default': -15,
        'moscow': -10,
        'uryupinsk': -90,
        'newvasyuki': 0,
        'геозона': -29,
    }
    monkeypatch.setattr(
        sc.ScoringConfig,
        'AFS_SCORE_DRIVER_PASSING_SCORE_BY_ZONE',
        zone_config,
    )


def _set_config(monkeypatch, service_type, enabled):
    # actual config looks like this:
    # {
    #     "active_service": "sum_and_substance",
    #     "enabled": false,
    #     "callback_url": "",
    #     "services": {
    #         "scoring_studio": {
    #             "url":
    #                 "https://api.scoringstudio.cloud/api/v1/scoring/request"
    #         },
    #         "sum_and_substance": {
    #             "url": "https://test-api.sumsub.com/resources/applicants",
    #             "test_key": "NJPFQPPUMERBRM"
    #         }
    #     }
    # }

    new_config = copy.deepcopy(sc.ScoringConfig.AFS_SCORE_DRIVER)
    new_config['enabled'] = enabled
    new_config['active_service'] = service_type
    new_config['services'] = _SERVICE_CONFIGS
    monkeypatch.setattr(sc.ScoringConfig, 'AFS_SCORE_DRIVER', new_config)
