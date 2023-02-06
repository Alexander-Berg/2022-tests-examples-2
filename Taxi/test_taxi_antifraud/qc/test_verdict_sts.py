# pylint: disable=too-many-lines

import dataclasses
from unittest import mock

import pytest

from taxi_antifraud.qc import avtocod
from taxi_antifraud.qc import verdict_sts
from taxi_antifraud.qc import yavtocod


DEFAULT_CONFIG: dict = dict(
    AFS_CRON_RESOLVE_STS_QC_PASSES_COLOR_MAPPING=[],
    AFS_CRON_RESOLVE_STS_QC_PASSES_YAVTOCOD_BRAND_MAPPING=[],
    AFS_CRON_RESOLVE_STS_QC_PASSES_YAVTOCOD_COLOR_MAPPING=[],
    AFS_CRON_RESOLVE_STS_QC_PASSES_YAVTOCOD_MODEL_MAPPING=[],
    AFS_CRON_RESOLVE_STS_QC_PASSES_YAVTOCOD_RESOLVE_ENABLED=False,
)

SUCCESSFUL_INPUT: dict = {
    'qc_pass': {
        'color': 'желтый',
        'brand': 'Audi',
        'model': 'Q4',
        'year': '2014',
        'body_number': 'some_body_number',
        'number': 'А777АА777',
        'registration_cert': 'somestsnumber',
        'vin': 'some_vin_number',
    },
    'ocr_response': {
        'back_car_recognized_text': [
            {'confidence': 0.9, 'text': 'А777АА777\n', 'type': 'text'},
        ],
        'front_car_recognized_text': [
            {'confidence': 0.9, 'text': 'А777АА777\n', 'type': 'text'},
        ],
        'back_sts_full_model_text': (
            'владелецsome_vin_numbersome_vin_numbersomestsnumber'
        ),
        'front_sts_full_model_text': 'российская2014somestsnumber',
    },
    'avtocod_verdict': 'YES_AVTOCOD',
    'avtocod_report': {
        'data': [
            {
                'content': {
                    'identifiers': {
                        'vehicle': {
                            'sts': 'somestsnumber',
                            'vin': 'some_vin_number',
                        },
                    },
                    'tech_data': {
                        'body': {
                            'color': {'name': 'желтый'},
                            'number': 'somebodynumber',
                        },
                        'brand': {'name': {'normalized': 'Audi'}},
                        'model': {'name': {'normalized': 'Q4'}},
                        'year': 2014,
                    },
                },
            },
        ],
    },
    'catboost_scores': {
        'front_photo_has_correct_color': 0.9,
        'back_photo_has_correct_color': 0.9,
        'left_photo_has_correct_color': 0.9,
        'right_photo_has_correct_color': 0.9,
        'front_photo_has_correct_brand': 0.9,
        'back_photo_has_correct_brand': 0.9,
        'left_photo_has_correct_brand': 0.9,
        'right_photo_has_correct_brand': 0.9,
        'front_photo_has_bad_format': 0.1,
        'back_photo_has_bad_format': 0.1,
        'left_photo_has_bad_format': 0.1,
        'right_photo_has_bad_format': 0.1,
        'sts_photo_has_bad_format': 0.1,
        'front_car_photo_from_screen': 0.1,
        'back_car_photo_from_screen': 0.1,
        'left_car_photo_from_screen': 0.1,
        'right_car_photo_from_screen': 0.1,
        'front_sts_photo_from_screen': 0.1,
        'back_sts_photo_from_screen': 0.1,
        'front_sts_is_russian': 0.9,
        'back_sts_is_russian': 0.9,
    },
    'yavtocod_info': yavtocod.YavtocodInfo(
        vin='some_vin_number', year=2014, color='желтый', model='Audi Q4',
    ),
}

AVTOVCOD_REPORT_WITHOUT_BODY_NUMBER: dict = {
    'data': [
        {
            'content': {
                'identifiers': {
                    'vehicle': {
                        'sts': 'somestsnumber',
                        'vin': 'some_vin_number',
                    },
                },
                'tech_data': {
                    'body': {'color': {'name': 'желтый'}},
                    'brand': {'name': {'normalized': 'Audi'}},
                    'model': {'name': {'normalized': 'Q4'}},
                    'year': 2014,
                },
            },
        },
    ],
}


@pytest.mark.parametrize(
    'comment,qc_pass_dict,ocr_response,avtocod_verdict,'
    'avtocod_report,yavtocod_info,catboost_scores_dict,config_values,'
    'expected_verdict,expected_errors',
    [
        (
            'successful pass',
            SUCCESSFUL_INPUT['qc_pass'],
            SUCCESSFUL_INPUT['ocr_response'],
            SUCCESSFUL_INPUT['avtocod_verdict'],
            SUCCESSFUL_INPUT['avtocod_report'],
            SUCCESSFUL_INPUT['yavtocod_info'],
            SUCCESSFUL_INPUT['catboost_scores'],
            DEFAULT_CONFIG,
            'success',
            [],
        ),
        (
            'successfull pass with color config',
            {**SUCCESSFUL_INPUT['qc_pass'], 'color': 'пурпурный'},
            SUCCESSFUL_INPUT['ocr_response'],
            SUCCESSFUL_INPUT['avtocod_verdict'],
            SUCCESSFUL_INPUT['avtocod_report'],
            SUCCESSFUL_INPUT['yavtocod_info'],
            SUCCESSFUL_INPUT['catboost_scores'],
            {
                **DEFAULT_CONFIG,
                'AFS_CRON_RESOLVE_STS_QC_PASSES_COLOR_MAPPING': [
                    {'assessor_color': 'пурпурный', 'avtocod_color': 'желтый'},
                ],
            },
            'success',
            [],
        ),
        (
            'unknown with several errors',
            {
                **SUCCESSFUL_INPUT['qc_pass'],
                'color': 'серый',
                'brand': 'Toyota',
                'year': '2021',
                'number': '12345678',
            },
            SUCCESSFUL_INPUT['ocr_response'],
            SUCCESSFUL_INPUT['avtocod_verdict'],
            SUCCESSFUL_INPUT['avtocod_report'],
            SUCCESSFUL_INPUT['yavtocod_info'],
            {
                **SUCCESSFUL_INPUT['catboost_scores'],
                'front_sts_is_russian': 0.1,
            },
            DEFAULT_CONFIG,
            'unknown',
            [
                'qc pass year is not equal to avtocod or yavtocod year',
                'car color for assessors is None',
                'qc_pass brand is not equal to avtocod or yavtocod brand',
                'qc_pass number is not recognized in back car photo',
                'qc_pass number is not recognized in front car photo',
                'catboost front_sts_is_russian reached threshold',
            ],
        ),
        (
            'car number error',
            SUCCESSFUL_INPUT['qc_pass'],
            {
                **SUCCESSFUL_INPUT['ocr_response'],
                'front_car_recognized_text': [
                    {'confidence': 0.9, 'text': 'А777АА778\n', 'type': 'text'},
                ],
            },
            SUCCESSFUL_INPUT['avtocod_verdict'],
            SUCCESSFUL_INPUT['avtocod_report'],
            SUCCESSFUL_INPUT['yavtocod_info'],
            SUCCESSFUL_INPUT['catboost_scores'],
            DEFAULT_CONFIG,
            'unknown',
            ['qc_pass number is not recognized in front car photo'],
        ),
        (
            'sts number error',
            SUCCESSFUL_INPUT['qc_pass'],
            {
                **SUCCESSFUL_INPUT['ocr_response'],
                'front_sts_full_model_text': 'российская2014',
            },
            SUCCESSFUL_INPUT['avtocod_verdict'],
            SUCCESSFUL_INPUT['avtocod_report'],
            SUCCESSFUL_INPUT['yavtocod_info'],
            SUCCESSFUL_INPUT['catboost_scores'],
            DEFAULT_CONFIG,
            'unknown',
            [
                'there is no avtocod sts number in full and specific ocr '
                'response',
            ],
        ),
        (
            'vin and body number error',
            SUCCESSFUL_INPUT['qc_pass'],
            {
                **SUCCESSFUL_INPUT['ocr_response'],
                'back_sts_full_model_text': 'владелецsomestsnumber',
            },
            SUCCESSFUL_INPUT['avtocod_verdict'],
            SUCCESSFUL_INPUT['avtocod_report'],
            SUCCESSFUL_INPUT['yavtocod_info'],
            SUCCESSFUL_INPUT['catboost_scores'],
            DEFAULT_CONFIG,
            'unknown',
            ['there is no qc pass vin in full and specific ocr'],
        ),
        (
            'color error',
            {**SUCCESSFUL_INPUT['qc_pass'], 'color': 'красный'},
            SUCCESSFUL_INPUT['ocr_response'],
            SUCCESSFUL_INPUT['avtocod_verdict'],
            SUCCESSFUL_INPUT['avtocod_report'],
            SUCCESSFUL_INPUT['yavtocod_info'],
            SUCCESSFUL_INPUT['catboost_scores'],
            DEFAULT_CONFIG,
            'unknown',
            ['car color for assessors is None'],
        ),
        (
            'brand and model errors',
            {**SUCCESSFUL_INPUT['qc_pass'], 'brand': 'Another', 'model': 'Q5'},
            SUCCESSFUL_INPUT['ocr_response'],
            SUCCESSFUL_INPUT['avtocod_verdict'],
            SUCCESSFUL_INPUT['avtocod_report'],
            SUCCESSFUL_INPUT['yavtocod_info'],
            SUCCESSFUL_INPUT['catboost_scores'],
            DEFAULT_CONFIG,
            'unknown',
            [
                'qc_pass brand is not equal to avtocod or yavtocod brand',
                'qc_pass model is not equal to avtocod or yavtocod model',
            ],
        ),
        (
            'car year error',
            SUCCESSFUL_INPUT['qc_pass'],
            {
                **SUCCESSFUL_INPUT['ocr_response'],
                'front_sts_full_model_text': 'российскаяsomestsnumber',
            },
            SUCCESSFUL_INPUT['avtocod_verdict'],
            SUCCESSFUL_INPUT['avtocod_report'],
            SUCCESSFUL_INPUT['yavtocod_info'],
            SUCCESSFUL_INPUT['catboost_scores'],
            DEFAULT_CONFIG,
            'unknown',
            ['qc pass year is not found in full ocr response'],
        ),
        (
            'catboost error',
            SUCCESSFUL_INPUT['qc_pass'],
            SUCCESSFUL_INPUT['ocr_response'],
            SUCCESSFUL_INPUT['avtocod_verdict'],
            SUCCESSFUL_INPUT['avtocod_report'],
            SUCCESSFUL_INPUT['yavtocod_info'],
            {
                **SUCCESSFUL_INPUT['catboost_scores'],
                'back_car_photo_from_screen': 0.9,
            },
            DEFAULT_CONFIG,
            'unknown',
            ['catboost back_car_photo_from_screen reached threshold'],
        ),
        (
            'sts error',
            SUCCESSFUL_INPUT['qc_pass'],
            {
                **SUCCESSFUL_INPUT['ocr_response'],
                'front_sts_full_model_text': '2014somestsnumber',
            },
            SUCCESSFUL_INPUT['avtocod_verdict'],
            SUCCESSFUL_INPUT['avtocod_report'],
            SUCCESSFUL_INPUT['yavtocod_info'],
            SUCCESSFUL_INPUT['catboost_scores'],
            DEFAULT_CONFIG,
            'unknown',
            [
                'keywords российская or владелец is not found in full '
                'ocr response',
            ],
        ),
        (
            'ocr response is empty',
            SUCCESSFUL_INPUT['qc_pass'],
            {},
            SUCCESSFUL_INPUT['avtocod_verdict'],
            SUCCESSFUL_INPUT['avtocod_report'],
            SUCCESSFUL_INPUT['yavtocod_info'],
            SUCCESSFUL_INPUT['catboost_scores'],
            DEFAULT_CONFIG,
            'unknown',
            [
                'there is no avtocod sts number in full and specific '
                'ocr response',
                'there is no qc pass vin in full and specific ocr',
                'qc pass year is not found in full ocr response',
                'back car text does not recognized',
                'front car text does not recognized',
                'full ocr response has not recognized back photo',
                'full ocr response has not recognized front photo',
            ],
        ),
        (
            'car number is None in ocr',
            SUCCESSFUL_INPUT['qc_pass'],
            {
                **SUCCESSFUL_INPUT['ocr_response'],
                'back_car_recognized_text': [],
                'front_car_recognized_text': [],
            },
            SUCCESSFUL_INPUT['avtocod_verdict'],
            SUCCESSFUL_INPUT['avtocod_report'],
            SUCCESSFUL_INPUT['yavtocod_info'],
            SUCCESSFUL_INPUT['catboost_scores'],
            DEFAULT_CONFIG,
            'unknown',
            [
                'back car number is not found in ocr response',
                'front car number is not found in ocr response',
            ],
        ),
        (
            'avtocod_data is None',
            SUCCESSFUL_INPUT['qc_pass'],
            SUCCESSFUL_INPUT['ocr_response'],
            SUCCESSFUL_INPUT['avtocod_verdict'],
            {**SUCCESSFUL_INPUT['avtocod_report'], 'data': []},
            yavtocod.YavtocodInfo(vin=None, year=None, color=None, model=None),
            SUCCESSFUL_INPUT['catboost_scores'],
            DEFAULT_CONFIG,
            'unknown',
            [
                'avtocod and yavtocod reports do not have vin',
                'avtocod and yavtocod reports do not have year',
                'avtocod and yavtocod reports do not have color',
                'avtocod and yavtocod reports do not have brand',
                'avtocod and yavtocod reports do not have model',
            ],
        ),
        (
            'qc_pass and avtocod sts numbers are different',
            {
                **SUCCESSFUL_INPUT['qc_pass'],
                'registration_cert': 'anotherstsnumber',
            },
            SUCCESSFUL_INPUT['ocr_response'],
            SUCCESSFUL_INPUT['avtocod_verdict'],
            SUCCESSFUL_INPUT['avtocod_report'],
            SUCCESSFUL_INPUT['yavtocod_info'],
            SUCCESSFUL_INPUT['catboost_scores'],
            DEFAULT_CONFIG,
            'unknown',
            ['qc_pass sts number is not equal to avtocod sts number'],
        ),
        (
            'qc_pass and avtocod vin are different',
            {**SUCCESSFUL_INPUT['qc_pass'], 'vin': 'another_vin'},
            SUCCESSFUL_INPUT['ocr_response'],
            SUCCESSFUL_INPUT['avtocod_verdict'],
            SUCCESSFUL_INPUT['avtocod_report'],
            SUCCESSFUL_INPUT['yavtocod_info'],
            SUCCESSFUL_INPUT['catboost_scores'],
            DEFAULT_CONFIG,
            'unknown',
            ['qc pass vin is not equal to avtocod or yavtocod vin'],
        ),
        (
            'qc_pass color is None',
            {**SUCCESSFUL_INPUT['qc_pass'], 'color': None},
            SUCCESSFUL_INPUT['ocr_response'],
            SUCCESSFUL_INPUT['avtocod_verdict'],
            SUCCESSFUL_INPUT['avtocod_report'],
            SUCCESSFUL_INPUT['yavtocod_info'],
            SUCCESSFUL_INPUT['catboost_scores'],
            DEFAULT_CONFIG,
            'unknown',
            ['qc pass color is None'],
        ),
        (
            'qc_pass and avtocod colors are different',
            {**SUCCESSFUL_INPUT['qc_pass'], 'color': 'бордовый'},
            SUCCESSFUL_INPUT['ocr_response'],
            SUCCESSFUL_INPUT['avtocod_verdict'],
            SUCCESSFUL_INPUT['avtocod_report'],
            SUCCESSFUL_INPUT['yavtocod_info'],
            SUCCESSFUL_INPUT['catboost_scores'],
            {
                **DEFAULT_CONFIG,
                'AFS_CRON_RESOLVE_STS_QC_PASSES_COLOR_MAPPING': [
                    {'assessor_color': 'жёлтый', 'avtocod_color': 'желтый'},
                ],
            },
            'unknown',
            ['qc pass color is not matched with avtocod or yavtocod color'],
        ),
        (
            'catboost scores are None',
            SUCCESSFUL_INPUT['qc_pass'],
            SUCCESSFUL_INPUT['ocr_response'],
            SUCCESSFUL_INPUT['avtocod_verdict'],
            SUCCESSFUL_INPUT['avtocod_report'],
            SUCCESSFUL_INPUT['yavtocod_info'],
            None,
            DEFAULT_CONFIG,
            'unknown',
            ['catboost_scores are None'],
        ),
        (
            'successful pass with reversed sts photo',
            SUCCESSFUL_INPUT['qc_pass'],
            {
                **SUCCESSFUL_INPUT['ocr_response'],
                'back_sts_full_model_text': 'российская2014somestsnumber',
                'front_sts_full_model_text': (
                    'владелецsome_vin_numbersome_vin_numbersomestsnumber'
                ),
            },
            SUCCESSFUL_INPUT['avtocod_verdict'],
            SUCCESSFUL_INPUT['avtocod_report'],
            SUCCESSFUL_INPUT['yavtocod_info'],
            SUCCESSFUL_INPUT['catboost_scores'],
            DEFAULT_CONFIG,
            'success',
            [],
        ),
        (
            'mistakes verdict',
            SUCCESSFUL_INPUT['qc_pass'],
            SUCCESSFUL_INPUT['ocr_response'],
            'NO_EXCEPTION_VIN',
            SUCCESSFUL_INPUT['avtocod_report'],
            SUCCESSFUL_INPUT['yavtocod_info'],
            SUCCESSFUL_INPUT['catboost_scores'],
            DEFAULT_CONFIG,
            'mistakes',
            [],
        ),
        (
            'avtocod is None',
            SUCCESSFUL_INPUT['qc_pass'],
            SUCCESSFUL_INPUT['ocr_response'],
            SUCCESSFUL_INPUT['avtocod_verdict'],
            None,
            yavtocod.YavtocodInfo(vin=None, year=None, color=None, model=None),
            SUCCESSFUL_INPUT['catboost_scores'],
            DEFAULT_CONFIG,
            'unknown',
            [
                'avtocod and yavtocod reports do not have vin',
                'avtocod and yavtocod reports do not have year',
                'avtocod and yavtocod reports do not have color',
                'avtocod and yavtocod reports do not have brand',
                'avtocod and yavtocod reports do not have model',
            ],
        ),
        (
            'ocr response is None',
            SUCCESSFUL_INPUT['qc_pass'],
            None,
            SUCCESSFUL_INPUT['avtocod_verdict'],
            SUCCESSFUL_INPUT['avtocod_report'],
            SUCCESSFUL_INPUT['yavtocod_info'],
            SUCCESSFUL_INPUT['catboost_scores'],
            DEFAULT_CONFIG,
            'unknown',
            ['ocr_response is None'],
        ),
        (
            'successful pass qc_pass body number is substring',
            {**SUCCESSFUL_INPUT['qc_pass'], 'body_number': 'number'},
            {
                **SUCCESSFUL_INPUT['ocr_response'],
                'back_sts_full_model_text': (
                    'владелецsome_vin_numbersomestsnumbersomebodynumber'
                ),
            },
            SUCCESSFUL_INPUT['avtocod_verdict'],
            SUCCESSFUL_INPUT['avtocod_report'],
            SUCCESSFUL_INPUT['yavtocod_info'],
            SUCCESSFUL_INPUT['catboost_scores'],
            DEFAULT_CONFIG,
            'success',
            [],
        ),
        (
            'successful pass qc_pass body number is substring',
            {**SUCCESSFUL_INPUT['qc_pass'], 'body_number': 'number'},
            {
                **SUCCESSFUL_INPUT['ocr_response'],
                'back_sts_full_model_text': (
                    'владелецsome_vin_numbersomestsnumber'
                ),
            },
            SUCCESSFUL_INPUT['avtocod_verdict'],
            SUCCESSFUL_INPUT['avtocod_report'],
            SUCCESSFUL_INPUT['yavtocod_info'],
            SUCCESSFUL_INPUT['catboost_scores'],
            DEFAULT_CONFIG,
            'success',
            [],
        ),
        (
            'successful pass avtocod body number is substring',
            {
                **SUCCESSFUL_INPUT['qc_pass'],
                'body_number': 'somebodynumberandmore',
            },
            {
                **SUCCESSFUL_INPUT['ocr_response'],
                'back_sts_full_model_text': (
                    'владелецsome_vin_numbersomestsnumbersomebodynumber'
                    'andmore'
                ),
            },
            SUCCESSFUL_INPUT['avtocod_verdict'],
            SUCCESSFUL_INPUT['avtocod_report'],
            SUCCESSFUL_INPUT['yavtocod_info'],
            SUCCESSFUL_INPUT['catboost_scores'],
            DEFAULT_CONFIG,
            'success',
            [],
        ),
        (
            'successful pass qc pass body number equal to avtocod vin',
            {**SUCCESSFUL_INPUT['qc_pass'], 'body_number': 'some_vin_number'},
            {
                **SUCCESSFUL_INPUT['ocr_response'],
                'back_sts_full_model_text': (
                    'владелецsome_vin_numbersomestsnumber'
                ),
            },
            SUCCESSFUL_INPUT['avtocod_verdict'],
            AVTOVCOD_REPORT_WITHOUT_BODY_NUMBER,
            SUCCESSFUL_INPUT['yavtocod_info'],
            SUCCESSFUL_INPUT['catboost_scores'],
            DEFAULT_CONFIG,
            'success',
            [],
        ),
        (
            'successfull pass body number does not exist',
            {**SUCCESSFUL_INPUT['qc_pass'], 'body_number': None},
            {
                **SUCCESSFUL_INPUT['ocr_response'],
                'back_sts_full_model_text': (
                    'владелецsome_vin_numbersomestsnumber'
                ),
            },
            SUCCESSFUL_INPUT['avtocod_verdict'],
            AVTOVCOD_REPORT_WITHOUT_BODY_NUMBER,
            SUCCESSFUL_INPUT['yavtocod_info'],
            SUCCESSFUL_INPUT['catboost_scores'],
            DEFAULT_CONFIG,
            'success',
            [],
        ),
        (
            'successful pass avtocod body number is in ocr',
            {**SUCCESSFUL_INPUT['qc_pass'], 'body_number': None},
            {
                **SUCCESSFUL_INPUT['ocr_response'],
                'back_sts_full_model_text': (
                    'владелецsome_vin_numbersomestsnumbersomebodynumber'
                ),
            },
            SUCCESSFUL_INPUT['avtocod_verdict'],
            SUCCESSFUL_INPUT['avtocod_report'],
            SUCCESSFUL_INPUT['yavtocod_info'],
            SUCCESSFUL_INPUT['catboost_scores'],
            DEFAULT_CONFIG,
            'success',
            [],
        ),
        (
            'successful pass avtocod body number is not found',
            {**SUCCESSFUL_INPUT['qc_pass'], 'body_number': None},
            {
                **SUCCESSFUL_INPUT['ocr_response'],
                'back_sts_full_model_text': (
                    'владелецsome_vin_numbersomestsnumber'
                ),
            },
            SUCCESSFUL_INPUT['avtocod_verdict'],
            SUCCESSFUL_INPUT['avtocod_report'],
            SUCCESSFUL_INPUT['yavtocod_info'],
            SUCCESSFUL_INPUT['catboost_scores'],
            DEFAULT_CONFIG,
            'success',
            [],
        ),
        (
            'successful pass: back car photo recognized two cars',
            SUCCESSFUL_INPUT['qc_pass'],
            {
                **SUCCESSFUL_INPUT['ocr_response'],
                'back_car_recognized_text': [
                    {'confidence': 0.9, 'text': 'А888АА888\n', 'type': 'text'},
                    {'confidence': 0.9, 'text': 'А777АА777\n', 'type': 'text'},
                ],
            },
            SUCCESSFUL_INPUT['avtocod_verdict'],
            SUCCESSFUL_INPUT['avtocod_report'],
            SUCCESSFUL_INPUT['yavtocod_info'],
            SUCCESSFUL_INPUT['catboost_scores'],
            DEFAULT_CONFIG,
            'success',
            [],
        ),
        (
            'successful pass sts number recognized in specific model',
            SUCCESSFUL_INPUT['qc_pass'],
            {
                **SUCCESSFUL_INPUT['ocr_response'],
                'back_sts_full_model_text': (
                    'владелецsome_vin_numbersome_vin_number'
                ),
                'front_sts_full_model_text': 'российская2014',
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
            SUCCESSFUL_INPUT['avtocod_verdict'],
            SUCCESSFUL_INPUT['avtocod_report'],
            SUCCESSFUL_INPUT['yavtocod_info'],
            SUCCESSFUL_INPUT['catboost_scores'],
            DEFAULT_CONFIG,
            'success',
            [],
        ),
        (
            'successful pass vin number recognized in specific model',
            SUCCESSFUL_INPUT['qc_pass'],
            {
                **SUCCESSFUL_INPUT['ocr_response'],
                'back_sts_full_model_text': 'владелецsomestsnumber',
                'front_sts_full_model_text': 'российская2014somestsnumber',
                'back_sts_front_strategy': [
                    {
                        'confidence': 0.9,
                        'text': 'some_vin_number',
                        'type': 'stsfront_vin_number',
                    },
                ],
            },
            SUCCESSFUL_INPUT['avtocod_verdict'],
            SUCCESSFUL_INPUT['avtocod_report'],
            SUCCESSFUL_INPUT['yavtocod_info'],
            SUCCESSFUL_INPUT['catboost_scores'],
            DEFAULT_CONFIG,
            'success',
            [],
        ),
        (
            'successful pass car year recognized in specific model',
            SUCCESSFUL_INPUT['qc_pass'],
            {
                **SUCCESSFUL_INPUT['ocr_response'],
                'back_sts_full_model_text': (
                    'владелецsome_vin_numbersome_vin_numbersomestsnumber'
                ),
                'front_sts_full_model_text': 'российскаяsomestsnumber',
                'front_sts_front_strategy': [
                    {
                        'confidence': 0.9,
                        'text': '2014',
                        'type': 'stsfront_car_year',
                    },
                ],
            },
            SUCCESSFUL_INPUT['avtocod_verdict'],
            SUCCESSFUL_INPUT['avtocod_report'],
            SUCCESSFUL_INPUT['yavtocod_info'],
            SUCCESSFUL_INPUT['catboost_scores'],
            DEFAULT_CONFIG,
            'success',
            [],
        ),
        (
            'successful pass letters in sts car number',
            {**SUCCESSFUL_INPUT['qc_pass'], 'registration_cert': '99УУ999999'},
            {
                **SUCCESSFUL_INPUT['ocr_response'],
                'back_sts_full_model_text': (
                    'владелецsome_vin_numbersome_vin_number99YY999999'
                ),
                'front_sts_full_model_text': 'российская201499YY999999',
            },
            SUCCESSFUL_INPUT['avtocod_verdict'],
            {
                'data': [
                    {
                        'content': {
                            'identifiers': {
                                'vehicle': {
                                    'sts': '99УУ999999',
                                    'vin': 'some_vin_number',
                                },
                            },
                            'tech_data': {
                                'body': {
                                    'color': {'name': 'желтый'},
                                    'number': 'somebodynumber',
                                },
                                'brand': {'name': {'normalized': 'Audi'}},
                                'model': {'name': {'normalized': 'Q4'}},
                                'year': 2014,
                            },
                        },
                    },
                ],
            },
            SUCCESSFUL_INPUT['yavtocod_info'],
            SUCCESSFUL_INPUT['catboost_scores'],
            DEFAULT_CONFIG,
            'success',
            [],
        ),
        (
            'avtocod has no sts number',
            SUCCESSFUL_INPUT['qc_pass'],
            SUCCESSFUL_INPUT['ocr_response'],
            SUCCESSFUL_INPUT['avtocod_verdict'],
            {
                'data': [
                    {
                        'content': {
                            'identifiers': {
                                'vehicle': {'vin': 'some_vin_number'},
                            },
                            'tech_data': {
                                'body': {
                                    'color': {'name': 'желтый'},
                                    'number': 'somebodynumber',
                                },
                                'brand': {'name': {'normalized': 'Audi'}},
                                'model': {'name': {'normalized': 'Q4'}},
                                'year': 2014,
                            },
                        },
                    },
                ],
            },
            SUCCESSFUL_INPUT['yavtocod_info'],
            SUCCESSFUL_INPUT['catboost_scores'],
            DEFAULT_CONFIG,
            'success',
            [],
        ),
        (
            'success by Yavtocod vin',
            {**SUCCESSFUL_INPUT['qc_pass'], 'vin': 'yavtocod_vin'},
            {
                **SUCCESSFUL_INPUT['ocr_response'],
                'back_sts_full_model_text': (
                    SUCCESSFUL_INPUT['ocr_response'][
                        'back_sts_full_model_text'
                    ]
                    + '\nyavtocod_vin'
                ),
            },
            SUCCESSFUL_INPUT['avtocod_verdict'],
            SUCCESSFUL_INPUT['avtocod_report'],
            dataclasses.replace(
                SUCCESSFUL_INPUT['yavtocod_info'], vin='yavtocod_vin',
            ),
            SUCCESSFUL_INPUT['catboost_scores'],
            {
                **DEFAULT_CONFIG,
                'AFS_CRON_RESOLVE_STS_QC_PASSES_YAVTOCOD_RESOLVE_ENABLED': (
                    True
                ),
            },
            'success',
            [],
        ),
        (
            'success by Yavtocod year',
            {**SUCCESSFUL_INPUT['qc_pass'], 'year': '7777'},
            {
                **SUCCESSFUL_INPUT['ocr_response'],
                'back_sts_full_model_text': (
                    SUCCESSFUL_INPUT['ocr_response'][
                        'back_sts_full_model_text'
                    ]
                    + '\n7777'
                ),
            },
            SUCCESSFUL_INPUT['avtocod_verdict'],
            SUCCESSFUL_INPUT['avtocod_report'],
            dataclasses.replace(SUCCESSFUL_INPUT['yavtocod_info'], year=7777),
            SUCCESSFUL_INPUT['catboost_scores'],
            {
                **DEFAULT_CONFIG,
                'AFS_CRON_RESOLVE_STS_QC_PASSES_YAVTOCOD_RESOLVE_ENABLED': (
                    True
                ),
            },
            'success',
            [],
        ),
        (
            'success by Yavtocod color',
            {**SUCCESSFUL_INPUT['qc_pass'], 'color': 'цветной'},
            SUCCESSFUL_INPUT['ocr_response'],
            SUCCESSFUL_INPUT['avtocod_verdict'],
            SUCCESSFUL_INPUT['avtocod_report'],
            dataclasses.replace(
                SUCCESSFUL_INPUT['yavtocod_info'], color='цветной',
            ),
            SUCCESSFUL_INPUT['catboost_scores'],
            {
                **DEFAULT_CONFIG,
                'AFS_CRON_RESOLVE_STS_QC_PASSES_YAVTOCOD_RESOLVE_ENABLED': (
                    True
                ),
            },
            'success',
            [],
        ),
        (
            'success by Yavtocod color with mapping',
            {**SUCCESSFUL_INPUT['qc_pass'], 'color': 'yavtocod_color'},
            SUCCESSFUL_INPUT['ocr_response'],
            SUCCESSFUL_INPUT['avtocod_verdict'],
            SUCCESSFUL_INPUT['avtocod_report'],
            dataclasses.replace(
                SUCCESSFUL_INPUT['yavtocod_info'], color=' серобуромалиновый ',
            ),
            SUCCESSFUL_INPUT['catboost_scores'],
            {
                **DEFAULT_CONFIG,
                'AFS_CRON_RESOLVE_STS_QC_PASSES_YAVTOCOD_RESOLVE_ENABLED': (
                    True
                ),
                'AFS_CRON_RESOLVE_STS_QC_PASSES_YAVTOCOD_COLOR_MAPPING': [
                    {
                        'qc_pass_name': 'yavtocod_color',
                        'yavtocod_name': 'СероБуроМалиновый',
                    },
                ],
            },
            'success',
            [],
        ),
        (
            'success by Yavtocod brand',
            {**SUCCESSFUL_INPUT['qc_pass'], 'brand': 'yavtocod_brand'},
            SUCCESSFUL_INPUT['ocr_response'],
            SUCCESSFUL_INPUT['avtocod_verdict'],
            SUCCESSFUL_INPUT['avtocod_report'],
            dataclasses.replace(
                SUCCESSFUL_INPUT['yavtocod_info'],
                model='yavtocod_brand yavtocod_model',
            ),
            SUCCESSFUL_INPUT['catboost_scores'],
            {
                **DEFAULT_CONFIG,
                'AFS_CRON_RESOLVE_STS_QC_PASSES_YAVTOCOD_RESOLVE_ENABLED': (
                    True
                ),
            },
            'success',
            [],
        ),
        (
            'success by Yavtocod brand with mapping',
            {**SUCCESSFUL_INPUT['qc_pass'], 'brand': 'yavtocod_brand'},
            SUCCESSFUL_INPUT['ocr_response'],
            SUCCESSFUL_INPUT['avtocod_verdict'],
            SUCCESSFUL_INPUT['avtocod_report'],
            dataclasses.replace(
                SUCCESSFUL_INPUT['yavtocod_info'],
                model=' явтокодмарка явтокодмодель ',
            ),
            SUCCESSFUL_INPUT['catboost_scores'],
            {
                **DEFAULT_CONFIG,
                'AFS_CRON_RESOLVE_STS_QC_PASSES_YAVTOCOD_RESOLVE_ENABLED': (
                    True
                ),
                'AFS_CRON_RESOLVE_STS_QC_PASSES_YAVTOCOD_BRAND_MAPPING': [
                    {
                        'qc_pass_name': 'yavtocod_brand',
                        'yavtocod_name': 'ЯвтокодМарка',
                    },
                ],
            },
            'success',
            [],
        ),
        (
            'success by Yavtocod model',
            {**SUCCESSFUL_INPUT['qc_pass'], 'model': 'yavtocod_model'},
            SUCCESSFUL_INPUT['ocr_response'],
            SUCCESSFUL_INPUT['avtocod_verdict'],
            SUCCESSFUL_INPUT['avtocod_report'],
            dataclasses.replace(
                SUCCESSFUL_INPUT['yavtocod_info'],
                model='yavtocod_brand yavtocod_model',
            ),
            SUCCESSFUL_INPUT['catboost_scores'],
            {
                **DEFAULT_CONFIG,
                'AFS_CRON_RESOLVE_STS_QC_PASSES_YAVTOCOD_RESOLVE_ENABLED': (
                    True
                ),
            },
            'success',
            [],
        ),
        (
            'success by Yavtocod model with mapping',
            {**SUCCESSFUL_INPUT['qc_pass'], 'model': 'yavtocod_model'},
            SUCCESSFUL_INPUT['ocr_response'],
            SUCCESSFUL_INPUT['avtocod_verdict'],
            SUCCESSFUL_INPUT['avtocod_report'],
            dataclasses.replace(
                SUCCESSFUL_INPUT['yavtocod_info'],
                model=' явтокодмарка явтокодмодель ',
            ),
            SUCCESSFUL_INPUT['catboost_scores'],
            {
                **DEFAULT_CONFIG,
                'AFS_CRON_RESOLVE_STS_QC_PASSES_YAVTOCOD_RESOLVE_ENABLED': (
                    True
                ),
                'AFS_CRON_RESOLVE_STS_QC_PASSES_YAVTOCOD_MODEL_MAPPING': [
                    {
                        'qc_pass_name': 'yavtocod_model',
                        'yavtocod_name': 'ЯвтокодМодель',
                    },
                ],
            },
            'success',
            [],
        ),
    ],
)
def test_calculate_verdict_sts(
        comment,
        qc_pass_dict,
        ocr_response,
        avtocod_verdict,
        avtocod_report,
        yavtocod_info,
        catboost_scores_dict,
        config_values,
        expected_verdict,
        expected_errors,
):
    config = mock.Mock(**config_values)
    qc_pass = mock.Mock(**qc_pass_dict)
    catboost_scores = (
        mock.Mock(**catboost_scores_dict)
        if catboost_scores_dict is not None
        else None
    )

    catboost_models = mock.Mock(
        front_car_color_threshold=0.2,
        back_car_color_threshold=0.2,
        left_car_color_threshold=0.2,
        right_car_color_threshold=0.2,
        front_car_brand_threshold=0.02,
        back_car_brand_threshold=0.02,
        left_car_brand_threshold=0.02,
        right_car_brand_threshold=0.02,
        front_photo_bad_format_threshold=0.4,
        back_photo_bad_format_threshold=0.4,
        left_photo_bad_format_threshold=0.4,
        right_photo_bad_format_threshold=0.4,
        sts_photo_bad_format_threshold=0.4,
        car_photo_from_screen_threshold=0.2,
        sts_photo_from_screen_threshold=0.2,
        sts_front_is_russian_threshold=0.5,
        sts_back_is_russian_threshold=0.5,
    )

    verdict = verdict_sts.calculate_verdict(
        qc_pass,
        ocr_response,
        avtocod_verdict,
        avtocod.get_info(avtocod_report),
        yavtocod_info,
        catboost_models,
        catboost_scores,
        config,
    )

    assert str(verdict.verdict) == expected_verdict
    assert verdict.errors == expected_errors
