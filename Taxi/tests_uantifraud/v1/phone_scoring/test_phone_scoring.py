import base64
import json

import pytest


TEST_PHONE_NUMBER = '5555551212'
TEST_PHONE_NUMBER_WITH_COUNTRY = '1' + TEST_PHONE_NUMBER


@pytest.mark.nofilldb
async def test_async(
        taxi_uantifraud,
        taxi_uantifraud_monitor,
        load,
        mockserver,
        mongodb,
        testpoint,
):
    await base_test_impl(
        taxi_uantifraud,
        taxi_uantifraud_monitor,
        load,
        mockserver,
        mongodb,
        testpoint,
        'async',
        '5cebb3f8629526419e4dddb4',
    )


@pytest.mark.nofilldb
async def test_sync(
        taxi_uantifraud,
        taxi_uantifraud_monitor,
        load,
        mockserver,
        mongodb,
        testpoint,
):
    await base_test_impl(
        taxi_uantifraud,
        taxi_uantifraud_monitor,
        load,
        mockserver,
        mongodb,
        testpoint,
        'sync',
        '5cebb3f8629526419e4dddb5',
    )


def setup_mock_user_api(
        mockserver,
        test_user_phone_id,
        test_personal_phone_id,
        test_phone_number_with_country,
):
    @mockserver.handler('/user-api/user_phones/get', prefix=True)
    def _mock_user_api(request):
        req = request.json
        assert req['id'] == test_user_phone_id
        return mockserver.make_response(
            json.dumps(
                {
                    'id': test_user_phone_id,
                    'phone': test_phone_number_with_country,
                    'is_loyal': False,
                    'is_yandex_staff': False,
                    'is_taxi_staff': False,
                    'type': 'yandex',
                    'stat': {
                        'big_first_discounts': 1,
                        'complete': 2,
                        'complete_card': 3,
                        'complete_apple': 4,
                        'complete_google': 5,
                        'fake': 6,
                        'total': 7,
                    },
                    'personal_phone_id': test_personal_phone_id,
                },
            ),
            200,
        )


def setup_mock_personal_api(
        mockserver, test_personal_phone_id, test_phone_number_with_country,
):
    @mockserver.handler('/personal/v1/phones/store', prefix=True)
    def _mock_personal_api(request):
        req = request.json
        assert req['value'] == test_phone_number_with_country
        return mockserver.make_response(
            json.dumps(
                {
                    'id': test_personal_phone_id,
                    'value': test_phone_number_with_country,
                },
            ),
            200,
        )


class ApiCallsCounter:
    def __init__(self):
        self.counter = 0

    def get(self):
        return self.counter

    def inc(self):
        self.counter += 1


def setup_mock_telesign_api(
        mockserver, load, test_phone_number_with_country, api_calls,
):
    telesign_response200 = load('telesign_response200.json')
    assert (
        json.loads(telesign_response200)['numbering']['original'][
            'complete_phone_number'
        ]
        == test_phone_number_with_country
    )

    @mockserver.handler('/score', prefix=True)
    def _mock_telesign_api(request):
        if api_calls is not None:
            api_calls.inc()
        assert request.method == 'POST'
        assert request.path == '/score/%s' % test_phone_number_with_country
        authorization_prefix = 'Basic '
        authorization_header_value = request.headers['Authorization']
        assert authorization_header_value.startswith(authorization_prefix)
        authorization_decoded = base64.b64decode(
            authorization_header_value[len(authorization_prefix) :],
        )
        assert authorization_decoded == b'login:password'
        return mockserver.make_response(telesign_response200, 200)


async def base_test_impl(
        taxi_uantifraud,
        taxi_uantifraud_monitor,
        load,
        mockserver,
        mongodb,
        testpoint,
        mode,
        test_user_phone_id,
):
    @testpoint('telesign-report-saved')
    def telesign_report_saved(data):
        pass

    test_src_service = 'taxi'

    await taxi_uantifraud.tests_control(reset_metrics=True)

    test_personal_phone_id = test_user_phone_id
    api_calls = ApiCallsCounter()

    setup_mock_user_api(
        mockserver,
        test_user_phone_id,
        test_personal_phone_id,
        TEST_PHONE_NUMBER_WITH_COUNTRY,
    )
    setup_mock_personal_api(
        mockserver, test_personal_phone_id, TEST_PHONE_NUMBER_WITH_COUNTRY,
    )
    setup_mock_telesign_api(
        mockserver, load, TEST_PHONE_NUMBER_WITH_COUNTRY, api_calls,
    )

    assert (
        mongodb.antifraud_telesign_phone_scoring.find_one(
            {'phone_id': test_user_phone_id},
        )
        is None
    )

    def check_post():
        return taxi_uantifraud.post(
            'v1/phone_scoring',
            {'user_phone_id': test_user_phone_id},
            params={'mode': mode, 'src_service': test_src_service},
        )

    assert api_calls.get() == 0
    response = await check_post()
    await telesign_report_saved.wait_call()
    assert api_calls.get() == 1
    assert response.status_code == 200
    report = mongodb.antifraud_telesign_phone_scoring.find_one(
        {'phone_id': test_user_phone_id},
    )
    assert report['risk_recommendation'] == 'block'
    assert report['risk_score'] > 500
    assert (
        report['telesign_full_report'].find(TEST_PHONE_NUMBER) == -1
    )  # check for masking private data
    assert report['src_service'] == test_src_service

    # single check for each phone.
    await check_post()
    assert api_calls.get() == 1

    # check stop for equal personal_phone_id
    another_phone_id = test_user_phone_id + '_some_suffix'
    setup_mock_user_api(
        mockserver,
        another_phone_id,
        test_personal_phone_id,
        TEST_PHONE_NUMBER_WITH_COUNTRY,
    )
    await taxi_uantifraud.post(
        'v1/phone_scoring',
        {'user_phone_id': another_phone_id},
        params={'mode': 'sync'},
    )
    assert api_calls.get() == 1

    stats = await taxi_uantifraud_monitor.get_metric('telesign')
    assert stats == {
        'already_checked_by_phone_id': 1,
        'already_checked_by_personal_phone_id': 1,
        'foreign_request_start': 1,
        'foreign_request_success': 1,
        'foreign_request_failed': 0,
        'personal_phone_id_empty': 0,
        'personal_api_error': 0,
        'user_api_error': 0,
        'known_eda_user': 0,
        'known_taxi_user': 0,
        'stored_to_db': 1,
        'wrong_args': 0,
    }


@pytest.mark.nofilldb
async def test_eda(
        taxi_uantifraud, taxi_uantifraud_monitor, load, mockserver, mongodb,
):
    test_src_service = 'eda'

    test_user_phone_id = '5cebb3f8629526419e4dddb6'
    test_personal_phone_id = test_user_phone_id

    await taxi_uantifraud.tests_control(reset_metrics=True)

    setup_mock_user_api(
        mockserver,
        test_user_phone_id,
        test_personal_phone_id,
        TEST_PHONE_NUMBER_WITH_COUNTRY,
    )
    setup_mock_personal_api(
        mockserver, test_personal_phone_id, TEST_PHONE_NUMBER_WITH_COUNTRY,
    )
    setup_mock_telesign_api(
        mockserver, load, TEST_PHONE_NUMBER_WITH_COUNTRY, api_calls=None,
    )

    assert (
        mongodb.antifraud_telesign_phone_scoring.find_one(
            {'phone_id': test_user_phone_id},
        )
        is None
    )

    def check_post():
        return taxi_uantifraud.post(
            'v1/phone_scoring',
            {'user_phone': TEST_PHONE_NUMBER_WITH_COUNTRY},
            params={'mode': 'sync', 'src_service': test_src_service},
        )

    response = await check_post()
    assert response.status_code == 200
    assert (
        mongodb.antifraud_telesign_phone_scoring.find_one(
            {'personal_phone_id': test_personal_phone_id},
        )
        is not None
    )

    stats = await taxi_uantifraud_monitor.get_metric('telesign')
    assert stats == {
        'already_checked_by_phone_id': 0,
        'already_checked_by_personal_phone_id': 0,
        'foreign_request_start': 1,
        'foreign_request_success': 1,
        'foreign_request_failed': 0,
        'personal_phone_id_empty': 0,
        'personal_api_error': 0,
        'user_api_error': 0,
        'known_eda_user': 0,
        'known_taxi_user': 0,
        'stored_to_db': 1,
        'wrong_args': 0,
    }
