import pytest

from taxi.core import async
from taxi.external import passenger_profile


class _Response(object):
    def __init__(self, json):
        self._json = json

    def json(self):
        return self._json


def _patch_perform_request(
        patch,
        expected_location,
        expected_params,
        response,
        expected_exception_cls=None,
):
    @patch('taxi.external.passenger_profile._perform_request')
    @async.inline_callbacks
    def _perform_request(method, location, params, log_extra):
        assert method == 'GET'
        assert location == expected_location
        assert params == expected_params
        if expected_exception_cls:
            raise expected_exception_cls()
        async.return_value(_Response(response))
        yield

    return _perform_request


@pytest.mark.parametrize(
    ['response', 'expected_exception_cls', 'expected_result'],
    [
        (
            # Normal response
            {'rating': '5.0', 'first_name': 'Michael Popov'},
            None,
            'Michael Popov',
        ),
        (
            # Optional field 'first_name' is missing
            {'rating': '5.0'},
            None,
            None,
        ),
        (None, passenger_profile.InvalidRequest, None),
        (None, passenger_profile.Forbidden, None),
    ]
)
@pytest.inline_callbacks
def test_get_first_name(
        patch,
        response,
        expected_exception_cls,
        expected_result,
):
    application = 'android'
    yandex_uid = '933975681'
    mocked_func = _patch_perform_request(
        patch,
        expected_location='passenger-profile/v1/profile',
        expected_params={'application': application, 'yandex_uid': yandex_uid},
        response=response,
        expected_exception_cls=expected_exception_cls,
    )
    try:
        result = yield passenger_profile.get_first_name(
            application, yandex_uid,
        )
        assert result == expected_result
    except Exception as exc:
        assert expected_exception_cls is not None
        assert isinstance(exc, expected_exception_cls)
    assert len(mocked_func.calls) == 1
