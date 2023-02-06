from unittest import mock

import pytest

from taxi_antifraud.qc import changes_identity


QC_PASS_DEFAULT = {
    'last_name': 'Иванов',
    'first_name': 'Петр',
    'patronymic': 'Олегович',
    'date_of_birth': '2000-01-01',
    'issue_date': '2020-01-01',
    'issuer': 'РОВД города Москвы',
    'number': '1112223334',
    'type': 'rus',
}

OCR_DEFAULT = {
    'title_recognized_text': [
        {'confidence': 0.9, 'text': 'Иванов', 'type': 'surname'},
        {'confidence': 0.9, 'text': 'Петр', 'type': 'name'},
        {'confidence': 0.9, 'text': 'Олегович', 'type': 'middle_name'},
        {'confidence': 0.9, 'text': '01.01.2000', 'type': 'birth_date'},
        {'confidence': 0.9, 'text': '1112223334', 'type': 'number'},
        {'confidence': 0.9, 'text': '01.01.2020', 'type': 'issue_date'},
        {
            'confidence': 0.9,
            'text': 'РОВД города Москвы',
            'type': 'subdivision',
        },
    ],
}

CONFIG_DEFAULT = {
    'AFS_CRON_RESOLVE_IDENTITY_QC_PASSES_OCR_CONFIDENCE_THRESHOLD': 0.8,
    'AFS_CRON_RESOLVE_IDENTITY_QC_PASSES_OCR_STRATEGY': [],
}


@pytest.mark.now('2021-01-01T00:00:00Z')
@pytest.mark.parametrize(
    'comment,qc_pass_dict,ocr_response,config_dict,expected_changes',
    [
        ('no changes', QC_PASS_DEFAULT, OCR_DEFAULT, CONFIG_DEFAULT, []),
        (
            'changes_number',
            {**QC_PASS_DEFAULT, 'number': '7777777777'},
            OCR_DEFAULT,
            CONFIG_DEFAULT,
            [
                {
                    'field_name': 'number_pd_id',
                    'new_value': '1112223334_pd_id',
                    'old_value': '7777777777_pd_id',
                },
            ],
        ),
        (
            'changes name',
            {
                **QC_PASS_DEFAULT,
                'first_name': 'Семёнов',
                'last_name': 'Семён',
                'patronymic': 'Семёнович',
            },
            OCR_DEFAULT,
            CONFIG_DEFAULT,
            [
                {
                    'field_name': 'firstname',
                    'new_value': 'Петр',
                    'old_value': 'Семёнов',
                },
                {
                    'field_name': 'middlename',
                    'new_value': 'Олегович',
                    'old_value': 'Семёнович',
                },
                {
                    'field_name': 'lastname',
                    'new_value': 'Иванов',
                    'old_value': 'Семён',
                },
            ],
        ),
        (
            'changes name with strip',
            QC_PASS_DEFAULT,
            {
                'title_recognized_text': [
                    {
                        'confidence': 0.9,
                        'text': '  Семёнов  ',
                        'type': 'surname',
                    },
                    {'confidence': 0.9, 'text': '  Семён ', 'type': 'name'},
                    {
                        'confidence': 0.9,
                        'text': 'Семёнович      ',
                        'type': 'middle_name',
                    },
                    {
                        'confidence': 0.9,
                        'text': '01.01.2000',
                        'type': 'birth_date',
                    },
                    {
                        'confidence': 0.9,
                        'text': '1112223334',
                        'type': 'number',
                    },
                    {
                        'confidence': 0.9,
                        'text': '01.01.2020',
                        'type': 'issue_date',
                    },
                    {
                        'confidence': 0.9,
                        'text': 'РОВД города Москвы',
                        'type': 'subdivision',
                    },
                ],
            },
            CONFIG_DEFAULT,
            [
                {
                    'field_name': 'firstname',
                    'new_value': '  Семён ',
                    'old_value': 'Петр',
                },
                {
                    'field_name': 'middlename',
                    'new_value': 'Семёнович      ',
                    'old_value': 'Олегович',
                },
                {
                    'field_name': 'lastname',
                    'new_value': '  Семёнов  ',
                    'old_value': 'Иванов',
                },
                {
                    'field_name': 'lastname',
                    'new_value': 'Семёнов',
                    'old_value': '  Семёнов  ',
                },
                {
                    'field_name': 'firstname',
                    'new_value': 'Семён',
                    'old_value': '  Семён ',
                },
                {
                    'field_name': 'middlename',
                    'new_value': 'Семёнович',
                    'old_value': 'Семёнович      ',
                },
            ],
        ),
        (
            'do not change birthday in kaz documents',
            {
                **QC_PASS_DEFAULT,
                'type': 'id_kaz',
                'date_of_birth': '2002-01-01',
            },
            OCR_DEFAULT,
            CONFIG_DEFAULT,
            [],
        ),
        (
            'fill birthday from ocr in kaz documents',
            {**QC_PASS_DEFAULT, 'type': 'id_kaz', 'date_of_birth': None},
            OCR_DEFAULT,
            CONFIG_DEFAULT,
            [
                {
                    'field_name': 'date_of_birth',
                    'old_value': None,
                    'new_value': '2000-01-01',
                },
            ],
        ),
        (
            'fill birthday from ocr issue_date in kaz documents',
            {**QC_PASS_DEFAULT, 'type': 'id_kaz', 'date_of_birth': None},
            {
                'title_recognized_text': [
                    {'confidence': 0.9, 'text': 'Иванов', 'type': 'surname'},
                    {'confidence': 0.9, 'text': 'Петр', 'type': 'name'},
                    {
                        'confidence': 0.9,
                        'text': 'Олегович',
                        'type': 'middle_name',
                    },
                    {
                        'confidence': 0.9,
                        'text': '1112223334',
                        'type': 'number',
                    },
                    {
                        'confidence': 0.9,
                        'text': '01.01.2010',
                        'type': 'issue_date',
                    },
                    {
                        'confidence': 0.9,
                        'text': 'РОВД города Москвы',
                        'type': 'subdivision',
                    },
                ],
            },
            CONFIG_DEFAULT,
            [
                {
                    'field_name': 'date_of_birth',
                    'old_value': None,
                    'new_value': '2010-01-01',
                },
            ],
        ),
        (
            'fill issue_date from expiration_date in kaz documents',
            {**QC_PASS_DEFAULT, 'type': 'id_kaz'},
            {
                'back_recognized_text_by_dkvu_front_model': [
                    {
                        'confidence': 0.9,
                        'text': '01.01.2021',
                        'type': 'expiration_date',
                    },
                    {
                        'confidence': 0.9,
                        'text': '01.02.2015',
                        'type': 'issue_date',
                    },
                ],
                'title_recognized_text': [],
            },
            CONFIG_DEFAULT,
            [
                {
                    'field_name': 'issue_date',
                    'old_value': '2020-01-01',
                    'new_value': '2011-02-01',
                },
            ],
        ),
        (
            'fill issue_date from issue_date in kaz documents',
            {**QC_PASS_DEFAULT, 'type': 'id_kaz'},
            {
                'back_recognized_text_by_dkvu_front_model': [
                    {
                        'confidence': 0.9,
                        'text': '01.01.2019',
                        'type': 'expiration_date',
                    },
                    {
                        'confidence': 0.9,
                        'text': '01.01.2015',
                        'type': 'issue_date',
                    },
                ],
                'title_recognized_text': [],
            },
            CONFIG_DEFAULT,
            [
                {
                    'field_name': 'issue_date',
                    'old_value': '2020-01-01',
                    'new_value': '2015-01-01',
                },
            ],
        ),
        (
            'do not change issue_date in kaz documents',
            {**QC_PASS_DEFAULT, 'type': 'id_kaz'},
            {
                'title_recognized_text': [],
                'back_recognized_text_by_dkvu_front_model': [],
            },
            CONFIG_DEFAULT,
            [],
        ),
        (
            'fill data from kaz ocr',
            {
                'last_name': None,
                'first_name': None,
                'patronymic': None,
                'date_of_birth': None,
                'issue_date': None,
                'issuer': None,
                'number': None,
                'type': 'id_kaz_stripped',
            },
            {
                'title_recognized_text': [
                    {'type': 'name', 'text': 'атабек ', 'confidence': 0.7},
                    {
                        'type': 'surname',
                        'text': 'атабеков ',
                        'confidence': 0.7,
                    },
                    {
                        'type': 'middle_name',
                        'text': 'атабекулы ',
                        'confidence': 0.7,
                    },
                    {
                        'type': 'number',
                        'text': '111222333444',
                        'confidence': 0.7,
                    },
                    {
                        'type': 'birth_date',
                        'text': '01-02-1993',
                        'confidence': 0.7,
                    },
                ],
                'back_recognized_text_by_dkvu_front_model': [],
            },
            {
                'AFS_CRON_RESOLVE_IDENTITY_QC_PASSES_OCR_STRATEGY': [
                    {
                        'identity_type': 'id_kaz_stripped',
                        'ocr_strategy': 'PassportKaz',
                        'confidence_threshold': 0.6,
                    },
                ],
                'AFS_CRON_RESOLVE_IDENTITY_QC_PASSES_OCR_CONFIDENCE_THRESHOLD': (  # noqa: E501 pylint: disable=line-too-long
                    0.8
                ),
            },
            [
                {
                    'field_name': 'number_pd_id',
                    'new_value': '111222333444_pd_id',
                    'old_value': None,
                },
                {
                    'field_name': 'firstname',
                    'new_value': 'атабек ',
                    'old_value': None,
                },
                {
                    'field_name': 'middlename',
                    'new_value': 'атабекулы ',
                    'old_value': None,
                },
                {
                    'field_name': 'lastname',
                    'new_value': 'атабеков ',
                    'old_value': None,
                },
                {
                    'field_name': 'date_of_birth',
                    'new_value': '1993-02-01',
                    'old_value': None,
                },
                {
                    'field_name': 'lastname',
                    'new_value': 'атабеков',
                    'old_value': 'атабеков ',
                },
                {
                    'field_name': 'firstname',
                    'new_value': 'атабек',
                    'old_value': 'атабек ',
                },
                {
                    'field_name': 'middlename',
                    'new_value': 'атабекулы',
                    'old_value': 'атабекулы ',
                },
            ],
        ),
    ],
)
async def test_changes_identity(
        comment,
        qc_pass_dict,
        ocr_response,
        config_dict,
        expected_changes,
        patch,
):
    @patch('taxi_antifraud.qc.personal.store_passport')
    async def _store_passport(
            passport_number, personal_client, *args, **kwargs,
    ):
        if passport_number is None:
            return None
        return passport_number + '_pd_id'

    qc_pass = mock.Mock(**qc_pass_dict)
    config = mock.Mock(**config_dict)
    personal_client = mock.Mock()

    changes = await changes_identity.apply_identity_changes(
        qc_pass, ocr_response, config, personal_client,
    )

    assert changes == expected_changes
