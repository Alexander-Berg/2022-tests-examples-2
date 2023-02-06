import hashlib

import pytest

from tests_superapp_misc.test_availability import consts
from tests_superapp_misc.test_availability import helpers


@pytest.mark.config(
    SUPERAPP_MISC_CLIENT_YANDEX_DRIVE_PARAMETERS={
        'timeout_ms': 100,
        'server_timeout_us': 50000,
        'retries': 1,
    },
)
@pytest.mark.experiments3(filename='exp3_superapp_drive_availability.json')
@pytest.mark.parametrize(
    ['mocked_answer', 'expected_result'],
    [
        (
            helpers.get_drive_offer_answer(reason_code='no_cars'),
            helpers.drive_ok_response(),
        ),
        (
            helpers.get_drive_offer_answer(is_available=True),
            helpers.drive_ok_response(is_available=True),
        ),
        (
            helpers.get_drive_offer_answer(
                is_available=True, is_registered=False,
            ),
            helpers.drive_ok_response(is_available=True, is_registered=False),
        ),
        (
            helpers.get_drive_offer_answer(
                is_available=True, is_registered=True,
            ),
            helpers.drive_ok_response(is_available=True, is_registered=True),
        ),
        (
            helpers.get_drive_offer_answer(
                is_available=True, reason_code='no_cars',
            ),
            helpers.drive_ok_response(is_available=False, show_disabled=True),
        ),
        (
            helpers.get_drive_offer_answer(
                is_available=True, reason_code='random',
            ),
            helpers.drive_ok_response(is_available=True),
        ),
        (
            helpers.get_drive_offer_answer(
                is_available=False, reason_code=None,
            ),
            helpers.drive_ok_response(is_available=True),
        ),
        (
            helpers.get_drive_offer_answer(
                is_available=False, reason_code='bad_dst',
            ),
            helpers.drive_ok_response(is_available=True),
        ),
    ],
)
async def test_drive_availability(
        taxi_superapp_misc, mockserver, mocked_answer, expected_result,
):
    @mockserver.json_handler('/yandex-drive/offers/fixpoint')
    def _offers(request):
        assert 'IC-Taxi-App-Build' not in request.headers
        assert request.headers['AC-Taxi-App-Build'] == '1'
        assert request.headers['TC-Taxi-App-Build'] == '1'
        assert request.headers['X-Ya-User-Ticket'] == 'user_ticket'
        assert request.headers['DeviceId'] == 'device_id'
        assert (
            request.headers['X-Ya-UserSplit-Id']
            == hashlib.md5(b'device_id').hexdigest()
        )
        assert request.args['offer_count_limit'] == '1'
        assert request.args['src'] == '37.590533 55.733863'
        assert request.args['dst'] == '0.0 0.0'
        assert request.args['lang'] == 'ru'
        assert request.args['fast'] == 'true'
        assert request.args['timeout'] == '50000'
        return mocked_answer

    response = await taxi_superapp_misc.post(
        consts.URL,
        helpers.build_payload(),
        headers={
            'X-Ya-User-Ticket': 'user_ticket',
            'X-YaTaxi-Pass-Flags': 'portal',
            'X-AppMetrica-DeviceId': 'device_id',
            'X-Request-Language': 'ru',
            'X-Request-Application': 'app_name=android',
        },
    )
    assert response.status_code == 200
    assert response.json() == expected_result


@pytest.mark.experiments3(filename='exp3_superapp_drive_availability.json')
@pytest.mark.parametrize('err_class', ['TimeoutError', 'NetworkError'])
async def test_drive_availability_errors(
        taxi_superapp_misc, mockserver, err_class,
):
    @mockserver.json_handler('/yandex-drive/offers/fixpoint')
    def _offers(request):
        assert 'IC-Taxi-App-Build' not in request.headers
        assert request.headers['AC-Taxi-App-Build'] == '1'
        assert request.headers['TC-Taxi-App-Build'] == '1'
        raise getattr(mockserver, err_class)

    response = await taxi_superapp_misc.post(
        consts.URL,
        helpers.build_payload(),
        headers={
            'X-Ya-User-Ticket': 'user_ticket',
            'X-YaTaxi-Pass-Flags': 'portal',
            'X-Request-Language': 'ru',
            'X-Request-Application': 'app_name=android',
        },
    )
    assert response.status_code == 200
    assert response.json() == helpers.ok_response(True, True)


@pytest.mark.experiments3(filename='exp3_superapp_drive_availability.json')
@pytest.mark.experiments3(filename='exp3_drive_availability_fallback.json')
@pytest.mark.parametrize('err_class', ['TimeoutError', 'NetworkError'])
async def test_drive_availability_fallback(
        taxi_superapp_misc, mockserver, err_class,
):
    @mockserver.json_handler('/yandex-drive/offers/fixpoint')
    def _offers(request):
        assert 'IC-Taxi-App-Build' not in request.headers
        assert request.headers['AC-Taxi-App-Build'] == '1'
        assert request.headers['TC-Taxi-App-Build'] == '1'
        raise getattr(mockserver, err_class)

    response = await taxi_superapp_misc.post(
        consts.URL,
        helpers.build_payload(),
        headers={
            'X-Ya-User-Ticket': 'user_ticket',
            'X-YaTaxi-Pass-Flags': 'portal',
            'X-Request-Language': 'ru',
            'X-Request-Application': 'app_name=android',
        },
    )
    assert response.status_code == 200
    assert response.json() == helpers.drive_ok_response(is_available=True)


@pytest.mark.config(
    SUPERAPP_MISC_CLIENT_YANDEX_DRIVE_PARAMETERS={
        'timeout_ms': 100,
        'server_timeout_us': 50000,
        'retries': 1,
    },
)
@pytest.mark.experiments3(filename='exp3_superapp_drive_availability.json')
@pytest.mark.parametrize(
    'exp_multipoint, expected',
    [
        pytest.param(
            True,
            helpers.drive_ok_response(is_available=True),
            id='Merge availability position + waypoints, exp true',
        ),
        pytest.param(
            False,
            helpers.drive_ok_response(is_available=False),
            id='Merge availability position + waypoints, exp false',
        ),
    ],
)
async def test_drive_multipoint_availability(
        taxi_superapp_misc, mockserver, experiments3, exp_multipoint, expected,
):
    @mockserver.json_handler('/yandex-drive/offers/fixpoint')
    def _offers(request):
        assert 'IC-Taxi-App-Build' not in request.headers
        assert request.headers['AC-Taxi-App-Build'] == '1'
        assert request.headers['TC-Taxi-App-Build'] == '1'

        if request.args['src'] == '{0} {1}'.format(
                *consts.ADDITIONAL_POSITION,
        ):
            return helpers.get_drive_offer_answer(is_available=True)

        return helpers.get_drive_offer_answer(
            is_available=False, reason_code='no_cars',
        )

    helpers.add_exp_multipoint(experiments3, exp_multipoint)

    response = await taxi_superapp_misc.post(
        consts.URL,
        helpers.build_payload(state=helpers.build_state()),
        headers={
            'X-Ya-User-Ticket': 'user_ticket',
            'X-YaTaxi-Pass-Flags': 'portal',
            'X-AppMetrica-DeviceId': 'device_id',
            'X-Request-Language': 'ru',
            'X-Request-Application': 'app_name=yango_android',
        },
    )
    assert response.status_code == 200
    assert response.json() == expected
