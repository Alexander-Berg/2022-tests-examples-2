import pytest

from taxi.conf import settings
from taxi.core import async
from taxi.internal import personal
from taxi.internal import personal_manager


@pytest.mark.config(PERSONAL_SERVICE_ENABLED=False,
                    LOG_PERSONAL_DATA_SERVISE_ERRORS={'__default__': True})
@pytest.inline_callbacks
def test_service_enabled_default_config(patch):
    license_id = yield personal.store_safe(
        personal.PERSONAL_TYPE_DRIVER_LICENSES, '223322', 'unique_drivers')
    assert license_id is None


@pytest.mark.config(PERSONAL_SERVICE_ENABLED=False,
                    LOG_PERSONAL_DATA_SERVISE_ERRORS={'__default__': True,
                                                      'unique_drivers': False})
@pytest.inline_callbacks
def test_service_disabled_config(patch):
    license_id = yield personal.store_safe(
        personal.PERSONAL_TYPE_DRIVER_LICENSES, '223322', 'unique_drivers')
    assert license_id is None


@pytest.mark.config(PERSONAL_SERVICE_ENABLED=True,
                    LOG_PERSONAL_DATA_SERVISE_ERRORS={'__default__': True,
                                                      'unique_drivers': False})
@pytest.inline_callbacks
def test_store_license_safe_success(patch):
    @patch('taxi.external.personal.store')
    @async.inline_callbacks
    def mock_licenses_store(data_type, value, validate=True, log_extra=None):
        assert data_type == 'driver_licenses'
        assert value == '223322'
        yield
        async.return_value({'id': 'personal_id', 'license': '+223322'})

    license_id = yield personal.store_safe(
        personal.PERSONAL_TYPE_DRIVER_LICENSES, '223322', 'unique_drivers')
    assert license_id == 'personal_id'


@pytest.inline_callbacks
@pytest.mark.config(PERSONAL_SERVICE_ENABLED=True,
                    PERSONAL_BASE_URL='http://personal.taxi.yandex.net',
                    PERSONAL_PYTHON_CLIENT_TIMEOUT_MS=3000)
def test_store_license_safe_service_error(areq_request):
    @areq_request
    def aresponse(method, url, **kwargs):
        return areq_request.response(500)

    settings.PERSONAL_APIKEY = 'qwerty'
    license_id = yield personal.store_safe(
        personal.PERSONAL_TYPE_DRIVER_LICENSES, '223322', 'unique_drivers')
    assert license_id is None


@pytest.inline_callbacks
def test_store_license_safe_returns_none(patch):
    @patch('taxi.external.personal.store')
    @async.inline_callbacks
    def mock_licenses_store(data_type, value, validate=True, log_extra=None):
        assert data_type == 'driver_licenses'
        assert value == '223322'
        yield
        async.return_value({'id': None, 'license': '+223322'})

    license_id = yield personal.store_safe(
        personal.PERSONAL_TYPE_DRIVER_LICENSES, '223322', 'unique_drivers')
    assert license_id is None


@pytest.mark.parametrize('billing_response, expected_response', [
    (
        {
            'qwerty': 123,
            'user_phone': 'phone',
            'user_email': 'email',
        },
        {
            'qwerty': 123,
            'user_phone': 'phone',
            'user_phone_pd_id': 'personal_id',
            'user_email': 'email',
            'user_email_pd_id': 'personal_id',
        },
    ),
    (
        {
            'qwerty': 123,
            'user_phone': 'phone',
        },
        {
            'qwerty': 123,
            'user_phone': 'phone',
            'user_phone_pd_id': 'personal_id',
        },
    ),
    (
        {
            'qwerty': 123,
            'user_email': 'email',
        },
        {
            'qwerty': 123,
            'user_email': 'email',
            'user_email_pd_id': 'personal_id',
        },
    ),
    (
        {
            'qwerty': 123,
        },
        {
            'qwerty': 123,
        },
    ),
    (
        12345,
        12345,
    ),
    (
        '12345',
        '12345',
    ),
])
@pytest.mark.config(PERSONAL_HIDE_BILLING_ENABLED=True)
@pytest.inline_callbacks
def test_process_billing_response(patch, billing_response, expected_response):
    @patch('taxi.internal.personal.store')
    @async.inline_callbacks
    def mock_store(*args, **kwargs):
        yield
        async.return_value({'id': 'personal_id'})

    patched_response = yield personal_manager.process_billing_response(
        billing_response,
    )
    assert patched_response == expected_response


@pytest.mark.parametrize('billing_response, expected_response', [
    (
            [],
            []
    ),
    (
            [
                {
                    'EMAIL': 'some1@somwhere.com',
                    'INN': '1234567890',
                },
                {
                    'EMAIL': 'some2@somwhere.com',
                    'INN': '0123456789',
                }
            ],
            [
                {
                    'EMAIL': 'some1@somwhere.com',
                    'INN': '1234567890',
                    'INN_PD_ID': 'inn_pd_id_1'
                },
                {
                    'EMAIL': 'some2@somwhere.com',
                    'INN': '0123456789',
                    'INN_PD_ID': 'inn_pd_id_2'
                }
            ]
    ),
])
@pytest.mark.config(
    TAXI_PARKS_PERSONAL_DATA_WRITE_MODE={'__default__': 'both_fallback'})
@pytest.inline_callbacks
def test_process_get_client_persons(
        patch, billing_response, expected_response):
    @patch('taxi.internal.personal.bulk_store')
    @async.inline_callbacks
    def mock_bulk_store(data_type, raw_data, validate=True, log_extra=None):
        assert data_type == personal.PERSONAL_TYPE_TINS
        raw_to_pd_id = {
            '1234567890': 'inn_pd_id_1',
            '0123456789': 'inn_pd_id_2'
        }
        result = [{'id': raw_to_pd_id[raw], 'tin': raw} for raw in raw_data]
        yield
        async.return_value(result)

    patched_response = yield personal.process_get_client_persons(
        billing_response, 'billing',
    )
    assert patched_response == expected_response


@pytest.mark.parametrize('billing_response, expected_response', [
    (
            [],
            []
    ),
    (
            [
                {
                    'EMAIL': 'some1@somwhere.com',
                    'INN': '1234567890',
                },
                {
                    'EMAIL': 'some2@somwhere.com',
                    'INN': '0123456789',
                }
            ],
            [
                {
                    'EMAIL': 'some1@somwhere.com',
                    'INN': '1234567890',
                },
                {
                    'EMAIL': 'some2@somwhere.com',
                    'INN': '0123456789',
                }
            ]
    ),
])
@pytest.mark.config(
    TAXI_PARKS_PERSONAL_DATA_WRITE_MODE={'__default__': 'old_way'})
@pytest.inline_callbacks
def test_process_get_client_persons_old_way(
        patch, billing_response, expected_response):
    @patch('taxi.internal.personal.bulk_store')
    @async.inline_callbacks
    def mock_bulk_store(data_type, raw_data, validate=True, log_extra=None):
        assert False
        yield

    patched_response = yield personal.process_get_client_persons(
        billing_response, 'billing',
    )
    assert patched_response == expected_response


@pytest.mark.parametrize('billing_response, expected_response', [
    (
            [],
            []
    ),
    (
            [
                {
                    'EMAIL': 'some1@somwhere.com',
                    'INN': '1234567890',
                },
                {
                    'EMAIL': 'some2@somwhere.com',
                    'INN': '0123456789',
                }
            ],
            [
                {
                    'EMAIL': 'some1@somwhere.com',
                    'INN': '1234567890',
                },
                {
                    'EMAIL': 'some2@somwhere.com',
                    'INN': '0123456789',
                }
            ]
    ),
])
@pytest.mark.config(
    TAXI_PARKS_PERSONAL_DATA_WRITE_MODE={'__default__': 'both_fallback'})
@pytest.inline_callbacks
def test_process_get_client_persons_error_in_both_fallback(
        patch, billing_response, expected_response):
    @patch('taxi.internal.personal.bulk_store')
    @async.inline_callbacks
    def mock_bulk_store(data_type, raw_data, validate=True, log_extra=None):
        assert data_type == personal.PERSONAL_TYPE_TINS
        raise personal.BaseError
        yield
        async.return_value(None)

    patched_response = yield personal.process_get_client_persons(
        billing_response, 'billing',
    )
    assert patched_response == expected_response


@pytest.mark.config(
    TAXI_PARKS_PERSONAL_DATA_WRITE_MODE={'__default__': 'both_no_fallback'})
@pytest.inline_callbacks
def test_process_get_client_persons_error_in_both_no_fallback(
        patch):
    @patch('taxi.internal.personal.bulk_store')
    @async.inline_callbacks
    def mock_bulk_store(data_type, raw_data, validate=True, log_extra=None):
        assert data_type == personal.PERSONAL_TYPE_TINS
        raise personal.BaseError
        yield
        async.return_value(None)
    billing_response = [
                {
                    'EMAIL': 'some1@somwhere.com',
                    'INN': '1234567890',
                },
                {
                    'EMAIL': 'some2@somwhere.com',
                    'INN': '0123456789',
                }
            ]
    expected_exc = ('api-over-data : can not retrieve personal data for '
                    'consumer billing can not get INN_PD_ID for INN 1234567890 '
                    'can not get INN_PD_ID for INN 0123456789 ')
    try:
        yield personal.process_get_client_persons(
            billing_response, 'billing',
        )
    except personal.NoPersonalIdInNoFallback as exc:
        assert str(exc) == expected_exc
