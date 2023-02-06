import base64
import json

import pytest


TEST_PHONE_NUMBER = '5555551212'
TEST_PHONE_ID = '5555551212_phone_id'
TEST_PERSONAL_PHONE_ID = '5555551212_personal_id'
TEST_WRONG_ID = 'wrong_id'

USER_API_RESPONSE = {
    'id': TEST_PHONE_ID,
    'phone': TEST_PHONE_NUMBER,
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
    'personal_phone_id': TEST_PERSONAL_PHONE_ID,
}


def setup_mock_user_api(mockserver):
    @mockserver.handler('/user-api/user_phones')
    def _mock_user_api_post(request):
        if request.json['personal_phone_id'] == TEST_PERSONAL_PHONE_ID:
            return mockserver.make_response(json.dumps(USER_API_RESPONSE), 200)
        return mockserver.make_response(
            json.dumps({'code': '400', 'message': 'test_error'}), 400,
        )


def setup_mock_personal_api(mockserver):
    @mockserver.handler('/personal/v1/phones/retrieve', prefix=True)
    def _mock_personal_api_retrieve(request):
        req = request.json
        if req['id'] == TEST_PERSONAL_PHONE_ID:
            return mockserver.make_response(
                json.dumps(
                    {'id': TEST_PERSONAL_PHONE_ID, 'value': TEST_PHONE_NUMBER},
                ),
                200,
            )
        return mockserver.make_response(
            json.dumps({'code': '404', 'message': 'test_error'}), 404,
        )


class ApiCallsCounter:
    def __init__(self):
        self.counter = 0

    def get(self):
        return self.counter

    def inc(self):
        self.counter += 1


def setup_mock_telesign_api(mockserver, load, api_calls):
    telesign_response200 = load('telesign_response200.json')

    @mockserver.handler('/score', prefix=True)
    def _mock_telesign_api(request):
        api_calls.inc()
        assert request.method == 'POST'
        assert request.path == f'/score/{TEST_PHONE_NUMBER}'
        authorization_prefix = 'Basic '
        authorization_header_value = request.headers['Authorization']
        assert authorization_header_value.startswith(authorization_prefix)
        authorization_decoded = base64.b64decode(
            authorization_header_value[len(authorization_prefix) :],
        )
        assert authorization_decoded == b'login:password'
        return mockserver.make_response(telesign_response200, 200)


def setup_api(mockserver, load, api_calls):
    setup_mock_user_api(mockserver)
    setup_mock_personal_api(mockserver)
    setup_mock_telesign_api(mockserver, load, api_calls)


def clean(mongodb):
    mongodb.antifraud_telesign_phone_scoring.drop()


FULL_REPORT = {
    'full_report': '{"carrier":{"name":"Telefonica UK Limited"},"location":{"city":"Countrywide","coordinates":{"latitude":null,"longitude":null},"country":{"iso2":"GB","iso3":"GBR","name":"United Kingdom"},"county":null,"metro_code":null,"state":null,"time_zone":{"name":null,"utc_offset_max":"0","utc_offset_min":"0"},"zip":null},"numbering":{"cleansing":{"call":{"cleansed_code":105,"country_code":"1","max_length":10,"min_length":10,"phone_number":"**********"},"sms":{"cleansed_code":105,"country_code":"1","max_length":10,"min_length":10,"phone_number":"**********"}},"original":{"complete_phone_number":"***********","country_code":"1","phone_number":"**********"}},"phone_type":{"code":"8","description":"INVALID"},"reference_id":"B567DC5D1180011C8952823CF6B40773","risk":{"level":"high","recommendation":"block","score":959},"status":{"code":300,"description":"Transaction successfully completed","updated_on":"2017-02-01T00:33:34.860418Z"}}',  # noqa E501
    'recommendation': 'block',
    'score': 959,
}


@pytest.mark.nofilldb
@pytest.mark.parametrize('response_expected', [{'report': FULL_REPORT}])
async def test_sync_score(
        taxi_uantifraud,
        taxi_uantifraud_monitor,
        load,
        mockserver,
        mongodb,
        testpoint,
        response_expected,
):
    await taxi_uantifraud.tests_control(reset_metrics=True)
    api_calls = ApiCallsCounter()
    setup_api(mockserver, load, api_calls)

    def check_post():
        body = {'personal_phone_id': TEST_PERSONAL_PHONE_ID}
        return taxi_uantifraud.post('v2/phone_scoring/sync/score', body)

    assert api_calls.get() == 0
    response = await check_post()
    assert response.json() == response_expected

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

    assert api_calls.get() == 1
    await check_post()
    assert api_calls.get() == 2

    stats = await taxi_uantifraud_monitor.get_metric('telesign')
    assert stats == {
        'already_checked_by_phone_id': 0,
        'already_checked_by_personal_phone_id': 0,
        'foreign_request_start': 2,
        'foreign_request_success': 2,
        'foreign_request_failed': 0,
        'personal_phone_id_empty': 0,
        'personal_api_error': 0,
        'user_api_error': 0,
        'known_eda_user': 0,
        'known_taxi_user': 0,
        'stored_to_db': 2,
        'wrong_args': 0,
    }
    clean(mongodb)


@pytest.mark.nofilldb
async def test_async_score(
        taxi_uantifraud,
        taxi_uantifraud_monitor,
        load,
        mockserver,
        mongodb,
        testpoint,
):
    @testpoint('telesign-report-saved')
    def telesign_report_saved(data):
        pass

    await taxi_uantifraud.tests_control(reset_metrics=True)
    api_calls = ApiCallsCounter()
    setup_api(mockserver, load, api_calls)

    def check_post():
        body = {'personal_phone_id': TEST_PERSONAL_PHONE_ID}
        return taxi_uantifraud.post('v2/phone_scoring/async/score', body)

    assert api_calls.get() == 0
    response = await check_post()
    assert response.json() == {}
    await telesign_report_saved.wait_call()

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

    assert api_calls.get() == 1
    await check_post()
    assert api_calls.get() == 1

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
    clean(mongodb)


@pytest.mark.nofilldb
async def test_async_score_newbie(
        taxi_uantifraud,
        taxi_uantifraud_monitor,
        load,
        mockserver,
        mongodb,
        testpoint,
):
    @testpoint('telesign-report-saved')
    def telesign_report_saved(data):
        pass

    await taxi_uantifraud.tests_control(reset_metrics=True)
    api_calls = ApiCallsCounter()
    setup_api(mockserver, load, api_calls)

    def check_post():
        body = {'personal_phone_id': TEST_PERSONAL_PHONE_ID}
        return taxi_uantifraud.post(
            'v2/phone_scoring/async/score_newbie', body,
        )

    assert api_calls.get() == 0

    # newbie
    response = await check_post()
    assert response.status_code == 200
    assert response.json() == {}
    await telesign_report_saved.wait_call()

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

    assert api_calls.get() == 1

    # not newbie
    response = await check_post()
    assert response.status_code == 200
    assert api_calls.get() == 1
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
    clean(mongodb)


@pytest.mark.nofilldb
async def test_info(
        taxi_uantifraud,
        taxi_uantifraud_monitor,
        load,
        mockserver,
        mongodb,
        testpoint,
):
    await taxi_uantifraud.tests_control(reset_metrics=True)
    api_calls = ApiCallsCounter()
    setup_api(mockserver, load, api_calls)

    def check_get():
        url = 'v2/phone_scoring/info'
        return taxi_uantifraud.get(
            f'{url}?personal_phone_id={TEST_PERSONAL_PHONE_ID}',
        )

    def post_update_newbies():
        body = {
            'changed_values': [
                {
                    'personal_phone_id': TEST_PERSONAL_PHONE_ID,
                    'order_count': 0,
                },
            ],
        }
        return taxi_uantifraud.post('v2/phone_scoring/update_newbies', body)

    response = await check_get()
    assert response.json() == {
        'info': {
            'newbie_status': {'found_in_cache': False, 'is_newbie': True},
        },
    }

    response = await check_get()
    assert response.json() == {
        'info': {
            'newbie_status': {'found_in_cache': False, 'is_newbie': True},
        },
    }

    mongodb.antifraud_order_count.insert_one(
        {'personal_phone_id': TEST_PERSONAL_PHONE_ID, 'order_count': 4},
    )
    response = await check_get()
    assert response.json() == {
        'info': {
            'newbie_status': {'found_in_cache': False, 'is_newbie': False},
        },
    }

    await post_update_newbies()
    response = await check_get()
    assert response.json() == {
        'info': {
            'newbie_status': {'found_in_cache': False, 'is_newbie': True},
        },
    }


@pytest.mark.nofilldb
async def test_error(
        taxi_uantifraud,
        taxi_uantifraud_monitor,
        load,
        mockserver,
        mongodb,
        testpoint,
):
    await taxi_uantifraud.tests_control(reset_metrics=True)
    api_calls = ApiCallsCounter()
    setup_api(mockserver, load, api_calls)

    def info():
        url = 'v2/phone_scoring/info'
        return taxi_uantifraud.get(f'{url}?personal_phone_id={TEST_WRONG_ID}')

    def sync_score():
        body = {'personal_phone_id': TEST_WRONG_ID}
        return taxi_uantifraud.post('v2/phone_scoring/sync/score', body)

    def async_score():
        body = {'personal_phone_id': TEST_WRONG_ID}
        return taxi_uantifraud.post('v2/phone_scoring/async/score', body)

    def async_score_newbie():
        body = {'personal_phone_id': TEST_WRONG_ID}
        return taxi_uantifraud.post(
            'v2/phone_scoring/async/score_newbie', body,
        )

    for request in (info, sync_score):
        response = await request()
        assert response.status_code == 400

    for request in (async_score, async_score_newbie):
        response = await request()
        assert response.status_code == 200


@pytest.mark.nofilldb
@pytest.mark.config(UAFS_PHONESCORING_TELESIGN_ENABLED=False)
async def test_telesign_disabled(
        taxi_uantifraud,
        taxi_uantifraud_monitor,
        load,
        mockserver,
        mongodb,
        testpoint,
):
    await taxi_uantifraud.tests_control(reset_metrics=True)
    api_calls = ApiCallsCounter()
    setup_api(mockserver, load, api_calls)

    zero_stats = {
        'already_checked_by_phone_id': 0,
        'already_checked_by_personal_phone_id': 0,
        'foreign_request_start': 0,
        'foreign_request_success': 0,
        'foreign_request_failed': 0,
        'personal_phone_id_empty': 0,
        'personal_api_error': 0,
        'user_api_error': 0,
        'known_eda_user': 0,
        'known_taxi_user': 0,
        'stored_to_db': 0,
        'wrong_args': 0,
    }

    def check_post_sync():
        body = {'personal_phone_id': TEST_PERSONAL_PHONE_ID}
        return taxi_uantifraud.post('v2/phone_scoring/sync/score', body)

    def check_post_async(newbie=False):
        body = {'personal_phone_id': TEST_PERSONAL_PHONE_ID}
        if not newbie:
            return taxi_uantifraud.post('v2/phone_scoring/async/score', body)
        return taxi_uantifraud.post(
            'v2/phone_scoring/async/score_newbie', body,
        )

    response = await check_post_sync()
    assert response.status_code == 204
    stats = await taxi_uantifraud_monitor.get_metric('telesign')
    assert stats == zero_stats

    response = await check_post_async()
    assert response.status_code == 200
    stats = await taxi_uantifraud_monitor.get_metric('telesign')
    assert stats == zero_stats

    response = await check_post_async(newbie=True)
    assert response.status_code == 200
    stats = await taxi_uantifraud_monitor.get_metric('telesign')
    assert stats == zero_stats

    clean(mongodb)
