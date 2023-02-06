from unittest import mock

import pytest

from taxi_antifraud.qc import avtocod
from taxi_antifraud.qc import changes_sts
from taxi_antifraud.qc import yavtocod

QC_PASS_DEFAULT: dict = {
    'registration_cert': 'somestsnumber',
    'vin': 'somevinnumber',
    'body_number': 'somebodynumber',
}

AVTOCOD_INFO_DEFAULT = avtocod.AvtocodInfo(
    sts_number='somestsnumber',
    vin='somevinnumber',
    year=None,
    color=None,
    brand=None,
    model=None,
)

YAVTOCOD_INFO_DEFAULT = yavtocod.YavtocodInfo(
    vin='somevinnumber', year=None, color=None, model=None,
)

OCR_RESPONSE_DEFAULT = {
    'back_sts_full_model_text': 'somestsnumbersomevinnumbersomebodynumber',
    'front_sts_full_model_text': 'somestsnumbersomevinnumbersomebodynumber',
}


@pytest.mark.parametrize(
    'comment,qc_pass_dict,avtocod_info,yavtocod_info,ocr_response,changes,'
    'config_values,expected_changes_result',
    [
        (
            'change sts number',
            {**QC_PASS_DEFAULT, 'registration_cert': 'anotherstsnumber'},
            AVTOCOD_INFO_DEFAULT,
            YAVTOCOD_INFO_DEFAULT,
            OCR_RESPONSE_DEFAULT,
            [],
            {},
            [
                {
                    'field_name': 'registration_cert',
                    'old_value': 'anotherstsnumber',
                    'new_value': 'somestsnumber',
                },
            ],
        ),
        (
            'change vin number',
            {**QC_PASS_DEFAULT, 'vin': 'anothervinnumber'},
            AVTOCOD_INFO_DEFAULT,
            YAVTOCOD_INFO_DEFAULT,
            OCR_RESPONSE_DEFAULT,
            [
                {
                    'field_name': 'some_field_name',
                    'old_value': 'some_old_value',
                    'new_value': 'some_new_value',
                },
            ],
            {},
            [
                {
                    'field_name': 'some_field_name',
                    'old_value': 'some_old_value',
                    'new_value': 'some_new_value',
                },
                {
                    'field_name': 'vin',
                    'old_value': 'anothervinnumber',
                    'new_value': 'somevinnumber',
                },
            ],
        ),
        (
            'change sts number and vin',
            {
                **QC_PASS_DEFAULT,
                'registration_cert': 'anotherstsnumber',
                'vin': 'anothervinnumber',
                'body_number': None,
            },
            AVTOCOD_INFO_DEFAULT,
            YAVTOCOD_INFO_DEFAULT,
            OCR_RESPONSE_DEFAULT,
            [],
            {},
            [
                {
                    'field_name': 'registration_cert',
                    'old_value': 'anotherstsnumber',
                    'new_value': 'somestsnumber',
                },
                {
                    'field_name': 'vin',
                    'old_value': 'anothervinnumber',
                    'new_value': 'somevinnumber',
                },
            ],
        ),
        (
            'change sts number: ocr sts number with bad symbols',
            {**QC_PASS_DEFAULT, 'registration_cert': 'anotherstsnumber'},
            AVTOCOD_INFO_DEFAULT,
            YAVTOCOD_INFO_DEFAULT,
            {
                'back_sts_full_model_text': 'some sts   number',
                'front_sts_full_model_text': '   some   sts   number',
            },
            [],
            {},
            [
                {
                    'field_name': 'registration_cert',
                    'old_value': 'anotherstsnumber',
                    'new_value': 'somestsnumber',
                },
            ],
        ),
        (
            'change sts number found in special ocr',
            {**QC_PASS_DEFAULT, 'registration_cert': 'anotherstsnumber'},
            AVTOCOD_INFO_DEFAULT,
            YAVTOCOD_INFO_DEFAULT,
            {
                'front_sts_front_strategy': [
                    {
                        'confidence': 0.9,
                        'text': 'somestsnumber',
                        'type': 'stsfront_sts_number',
                    },
                ],
                'back_sts_back_strategy': [
                    {
                        'confidence': 0.9,
                        'text': 'somestsnumber',
                        'type': 'stsback_sts_number',
                    },
                ],
            },
            [],
            {},
            [
                {
                    'field_name': 'registration_cert',
                    'old_value': 'anotherstsnumber',
                    'new_value': 'somestsnumber',
                },
            ],
        ),
        (
            'change sts number found in special ocr reversed case',
            {**QC_PASS_DEFAULT, 'registration_cert': 'anotherstsnumber'},
            AVTOCOD_INFO_DEFAULT,
            YAVTOCOD_INFO_DEFAULT,
            {
                'back_sts_front_strategy': [
                    {
                        'confidence': 0.9,
                        'text': 'somestsnumber',
                        'type': 'stsfront_sts_number',
                    },
                ],
                'front_sts_back_strategy': [
                    {
                        'confidence': 0.9,
                        'text': 'somestsnumber',
                        'type': 'stsback_sts_number',
                    },
                ],
            },
            [],
            {},
            [
                {
                    'field_name': 'registration_cert',
                    'old_value': 'anotherstsnumber',
                    'new_value': 'somestsnumber',
                },
            ],
        ),
        (
            'change vin found in front photo with front strategy',
            {**QC_PASS_DEFAULT, 'vin': 'anothervinnumber'},
            AVTOCOD_INFO_DEFAULT,
            YAVTOCOD_INFO_DEFAULT,
            {
                'front_sts_front_strategy': [
                    {
                        'confidence': 0.9,
                        'text': 'somevinnumber',
                        'type': 'stsfront_vin_number',
                    },
                ],
            },
            [],
            {},
            [
                {
                    'field_name': 'vin',
                    'old_value': 'anothervinnumber',
                    'new_value': 'somevinnumber',
                },
            ],
        ),
        (
            'change vin found in back photo with front strategy',
            {**QC_PASS_DEFAULT, 'vin': 'anothervinnumber'},
            AVTOCOD_INFO_DEFAULT,
            YAVTOCOD_INFO_DEFAULT,
            {
                'back_sts_front_strategy': [
                    {
                        'confidence': 0.9,
                        'text': 'somevinnumber',
                        'type': 'stsfront_vin_number',
                    },
                ],
            },
            [],
            {},
            [
                {
                    'field_name': 'vin',
                    'old_value': 'anothervinnumber',
                    'new_value': 'somevinnumber',
                },
            ],
        ),
        (
            'change sts number to russian',
            {**QC_PASS_DEFAULT, 'registration_cert': '99YY999999'},
            avtocod.AvtocodInfo(
                sts_number='99УУ999999',
                vin='somevinnumber',
                year=None,
                color=None,
                brand=None,
                model=None,
            ),
            YAVTOCOD_INFO_DEFAULT,
            {
                'back_sts_full_model_text': '99YY999999somevinnumber',
                'front_sts_full_model_text': '99YY999999somevinnumber',
            },
            [],
            {},
            [
                {
                    'field_name': 'registration_cert',
                    'new_value': '99УУ999999',
                    'old_value': '99YY999999',
                },
            ],
        ),
        (
            'sts number recognized on one side',
            {**QC_PASS_DEFAULT, 'registration_cert': 'anotherstsnumber'},
            AVTOCOD_INFO_DEFAULT,
            YAVTOCOD_INFO_DEFAULT,
            {
                'back_sts_full_model_text': 'somevinnumbersomebodynumber',
                'front_sts_full_model_text': (
                    'somestsnumbersomevinnumbersomebodynumber'
                ),
            },
            [],
            {},
            [],
        ),
        (
            'change vin by Yavtocod',
            {**QC_PASS_DEFAULT, 'vin': 'anothervinnumber'},
            avtocod.AvtocodInfo(
                sts_number=None,
                vin=None,
                year=None,
                color=None,
                brand=None,
                model=None,
            ),
            yavtocod.YavtocodInfo(
                vin='somevinnumber', year=None, color=None, model=None,
            ),
            OCR_RESPONSE_DEFAULT,
            [
                {
                    'field_name': 'some_field_name',
                    'old_value': 'some_old_value',
                    'new_value': 'some_new_value',
                },
            ],
            {
                'AFS_CRON_RESOLVE_STS_QC_PASSES_YAVTOCOD_CHANGE_DATA_ENABLED': (  # noqa: E501 pylint: disable=line-too-long
                    True
                ),
            },
            [
                {
                    'field_name': 'some_field_name',
                    'old_value': 'some_old_value',
                    'new_value': 'some_new_value',
                },
                {
                    'field_name': 'vin',
                    'old_value': 'anothervinnumber',
                    'new_value': 'somevinnumber',
                },
            ],
        ),
        (
            'change empty vin by Yavtocod',
            {**QC_PASS_DEFAULT, 'vin': None},
            avtocod.AvtocodInfo(
                sts_number=None,
                vin=None,
                year=None,
                color=None,
                brand=None,
                model=None,
            ),
            yavtocod.YavtocodInfo(
                vin='somevinnumber', year=None, color=None, model=None,
            ),
            OCR_RESPONSE_DEFAULT,
            [
                {
                    'field_name': 'some_field_name',
                    'old_value': 'some_old_value',
                    'new_value': 'some_new_value',
                },
            ],
            {
                'AFS_CRON_RESOLVE_STS_QC_PASSES_YAVTOCOD_CHANGE_DATA_ENABLED': (  # noqa: E501 pylint: disable=line-too-long
                    True
                ),
            },
            [
                {
                    'field_name': 'some_field_name',
                    'old_value': 'some_old_value',
                    'new_value': 'some_new_value',
                },
                {
                    'field_name': 'vin',
                    'old_value': None,
                    'new_value': 'somevinnumber',
                },
            ],
        ),
    ],
)
def test_apply_changes_from_avtocod(
        comment,
        qc_pass_dict,
        avtocod_info,
        yavtocod_info,
        ocr_response,
        changes,
        config_values,
        expected_changes_result,
):
    qc_pass = mock.Mock(**qc_pass_dict)
    config = mock.Mock(**config_values)

    changes_result = changes_sts.apply_changes_from_avtocod(
        qc_pass, avtocod_info, yavtocod_info, ocr_response, changes, config,
    )

    assert changes_result == expected_changes_result
