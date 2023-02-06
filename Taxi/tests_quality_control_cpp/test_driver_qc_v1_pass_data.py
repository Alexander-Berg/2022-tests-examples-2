import datetime

import pytest


# pylint: disable=too-many-arguments
@pytest.mark.parametrize(
    'exam_code, pass_id, selectors, switchers, confirmations, '
    'pass_data_request, pass_data_response, pass_response, '
    'mock_parks, db_confirmation, expected_code, expected_response,'
    'park_id',
    [
        (
            'dkvu',
            '5d485be9e0eda8c4aafc4e96',
            {},
            {},
            {'dkvu_confirmation': 'http://dl_offer'},
            {'data': {'dkvu_confirmation': '<confirmation_id>'}},
            {},
            'api_v1_pass_empty.json',
            'driver_profile_list_rus.json',
            {
                'park_id': 'park_id',
                'driver_profile_id': 'driver_uuid',
                'pass_id': '5d485be9e0eda8c4aafc4e96',
                'offer_id': 'dkvu_confirmation',
                'offer_link': 'http://dl_offer',
                'created': datetime.datetime(2019, 9, 9, 8, 30),
            },
            200,
            {'exam_data': {}, 'ui': {'pages': []}},
            'park_id',
        ),
        (
            'identity',
            '5d485be9e0eda8c4aafc4e91',
            {'identity_id': 'passport_rus'},
            {},
            {'identity_confirmation': 'http://offer/ru/v1'},
            {
                'data': {
                    'identity_id': 'passport_rus',
                    'identity_confirmation': '<confirmation_id>',
                },
            },
            {},
            'api_v1_pass_identity_confirmation.json',
            'driver_profile_list_rus.json',
            {
                'park_id': 'park_id',
                'driver_profile_id': 'driver_uuid',
                'pass_id': '5d485be9e0eda8c4aafc4e91',
                'offer_id': 'identity_confirmation',
                'offer_link': 'http://offer/ru/v1',
                'created': datetime.datetime(2019, 9, 9, 8, 30),
            },
            200,
            {'exam_data': {}, 'ui': {'pages': []}},
            'park_id',
        ),
        (
            'identity',
            '5d485be9e0eda8c4aafc4e91',
            {'identity_id': 'passport_rus'},
            {},
            {'identity_confirmation': 'http://offer/ru/v1'},
            {
                'data': {
                    'identity_id': 'passport_rus',
                    'identity_confirmation': '<confirmation_id>',
                },
            },
            {'modified': '2017-04-25T07:00:00+00:00'},
            'api_v1_pass_identity_confirmation.json',
            'driver_profile_list_rus.json',
            {
                'park_id': 'park_id',
                'driver_profile_id': 'driver_uuid',
                'pass_id': '5d485be9e0eda8c4aafc4e91',
                'offer_id': 'identity_confirmation',
                'offer_link': 'http://offer/ru/v1',
                'created': datetime.datetime(2019, 9, 9, 8, 30),
            },
            200,
            {
                'exam_data': {
                    'modified': '2017-04-25T07:00:00+00:00',
                    'text': 'Информация отправлена.',
                },
                'ui': {'pages': []},
            },
            'park_id',
        ),
        (
            'identity',
            '5d485be9e0eda8c4aafc4e92',
            {'identity_id': 'passport_rus'},
            {},
            {'identity_confirmation': 'http://offer/ru/v1'},
            {
                'data': {
                    'identity_id': 'passport_rus',
                    'identity_confirmation': '<confirmation_id>',
                },
            },
            {},
            'api_v1_pass_identity_confirmation.json',
            'driver_profile_list_rus.json',
            {
                'park_id': 'park_id1',
                'driver_profile_id': 'driver_uuid1',
                'pass_id': '5d485be9e0eda8c4aafc4e92',
                'offer_id': 'identity_confirmation',
                'offer_link': 'http://offer',
                'created': datetime.datetime(2019, 8, 8, 11, 30),
            },
            200,
            {'exam_data': {}, 'ui': {'pages': []}},
            'park_id',
        ),
        (
            'identity',
            '5d485be9e0eda8c4aafc4e91',
            {'identity_id': 'passport_rus'},
            {},
            {'identity_confirmation': 'http://offer/ru/v2'},
            {
                'data': {
                    'identity_id': 'passport_rus',
                    'identity_confirmation': '<confirmation_id>',
                },
            },
            {},
            'api_v1_pass_identity_confirmation.json',
            'driver_profile_list_rus.json',
            None,
            200,
            {
                'exam_data': {},
                'ui': {
                    'pages': [
                        {
                            'type': 'default_page',
                            'confirmations': [
                                {
                                    'id': 'identity_confirmation',
                                    'title': (
                                        'Принимаю [условия]'
                                        '(http://offer/ru/v1)'
                                    ),
                                    'subtitle': '',
                                    'value': 'http://offer/ru/v1',
                                    'value_required': True,
                                    'markdown': True,
                                    'horizontal_divider_type': 'none',
                                    'tooltip_params': {
                                        'type': 'error',
                                        'text': 'Обязательное поле',
                                    },
                                    'default_confirmation_value': False,
                                },
                            ],
                        },
                        {'type': 'default_page'},
                    ],
                },
            },
            'park_id',
        ),
        (
            'identity',
            '5d485be9e0eda8c4aafc4e91',
            {'identity_id': 'passport_blr'},
            {},
            {},
            {'data': {'identity_id': 'passport_blr'}},
            {},
            'api_v1_pass_identity.json',
            'driver_profile_list_blr.json',
            None,
            200,
            {'exam_data': {}, 'ui': {'pages': []}},
            'park_id',
        ),
        (
            'identity',
            '5d485be9e0eda8c4aafc4e91',
            {'identity_id': 'passport_blr'},
            {},
            {'identity_confirmation': 'http://offer/ru/v1'},
            {
                'data': {
                    'identity_id': 'passport_blr',
                    'identity_confirmation': '<confirmation_id>',
                },
            },
            {},
            'api_v1_pass_identity_confirmation.json',
            'driver_profile_list_blr.json',
            None,
            400,
            None,
            'park_id',
        ),
        (
            'identity',
            '5d485be9e0eda8c4aafc4e91',
            {},
            {},
            {},
            {
                'data': {
                    'identity_id': 'passport_blr',
                    'identity_confirmation': '<confirmation_id>',
                },
            },
            {},
            'api_v1_pass_identity.json',
            'driver_profile_list_blr.json',
            None,
            400,
            None,
            'park_id',
        ),
        (
            'identity',
            '5d485be9e0eda8c4aafc4e91',
            {},
            {},
            {},
            None,
            None,
            'api_v1_pass_empty.json',
            'driver_profile_list_blr.json',
            None,
            200,
            {'exam_data': {}, 'ui': {'pages': []}},
            'park_id',
        ),
        (
            'vaccination',
            '5d485be9e0eda8c4aafc4e91',
            {},
            {'scan_result_id': 'http://covid'},
            {'vaccination_confirmation': 'http://offer/ru/v1'},
            {
                'data': {
                    'scan_result_id': 'http://covid',
                    'vaccination_confirmation': '<confirmation_id>',
                },
            },
            {'modified': '2017-04-25T07:00:00+00:00'},
            'api_v1_pass_vaccination.json',
            'driver_profile_list_rus.json',
            None,
            200,
            {
                'exam_data': {
                    'modified': '2017-04-25T07:00:00+00:00',
                    'text': 'Информация отправлена.',
                },
                'ui': {'pages': []},
            },
            'park_id',
        ),
        pytest.param(
            'vaccination',
            '5d485be9e0eda8c4aafc4e91',
            {},
            {'scan_result_id': 'http://covid'},
            {},
            {'data': {'scan_result_id': 'http://covid'}},
            {'modified': '2017-04-25T07:00:00+00:00'},
            'api_v1_pass_vaccination.json',
            'driver_profile_list_rus.json',
            None,
            200,
            {
                'exam_data': {
                    'modified': '2017-04-25T07:00:00+00:00',
                    'text': 'Информация отправлена.',
                },
                'ui': {'pages': []},
            },
            'park_id_confirmation_one_time_required',
            marks=pytest.mark.filldb(confirmations='vaccination'),
        ),
    ],
)
@pytest.mark.experiments3('qc_cpp_exp3_confirmation_configs.json')
@pytest.mark.now('2019-09-09T11:30:00+0300')
async def test_driver_qc_v1_pass_data(
        taxi_quality_control_cpp,
        mongodb,
        driver_authorizer,
        quality_control,
        parks,
        tags_mocks,
        exam_code,
        pass_id,
        selectors,
        switchers,
        confirmations,
        pass_data_request,
        pass_data_response,
        pass_response,
        mock_parks,
        db_confirmation,
        expected_code,
        expected_response,
        park_id,
):
    driver_authorizer.set_session(park_id, 'driver_session', 'driver_uuid')
    if pass_data_request is not None:
        quality_control.set_pass_data(
            pass_id, pass_data_request, pass_data_response,
        )
    parks.set_driver_profiles_list(
        park_id, 'driver_uuid', 'mock_responses/' + mock_parks,
    )

    quality_control.set_pass(pass_id, 'mock_responses/' + pass_response)

    response = await taxi_quality_control_cpp.post(
        '/driver/qc/v1/pass/data',
        params={'park_id': park_id},
        json={
            'exam_code': exam_code,
            'pass_id': pass_id,
            'selectors': selectors,
            'switchers': switchers,
            'data': {},
            'confirmations': confirmations,
        },
        headers={
            'Accept-Language': 'ru',
            'User-Agent': 'Taximeter 8.80 (562)',
            'X-Driver-Session': 'driver_session',
        },
    )

    assert response.status_code == expected_code
    if response.status_code == 200:
        if db_confirmation:
            doc = mongodb.confirmations.find_one({'pass_id': pass_id})
            doc.pop('_id')
            assert doc == db_confirmation

        assert response.json() == expected_response
