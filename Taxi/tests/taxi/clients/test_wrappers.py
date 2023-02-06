import pytest

from taxi.clients.helpers import errors
from taxi.clients.helpers import wrappers


@pytest.mark.parametrize(
    ('request_status', 'bad_codes', 'expected_status', 'expected_error'),
    [
        (200, None, 200, None),
        (400, None, 400, None),
        (400, [400], None, errors.BaseError),
        (429, None, None, errors.BaseError),
        (500, None, None, errors.BaseError),
    ],
)
async def test_check_status(
        response_mock,
        request_status,
        bad_codes,
        expected_status,
        expected_error,
):
    @wrappers.check_status(bad_codes)
    async def request():
        return response_mock(status=request_status)

    if expected_error:
        with pytest.raises(expected_error):
            await request()
    else:
        response = await request()
        assert response.status == expected_status


@pytest.mark.parametrize(
    ('errors_before_response', 'retries_count', 'expected_error'),
    [
        (0, 2, None),
        (1, 2, None),
        (2, 2, errors.BaseError),
        (3, 2, errors.BaseError),
    ],
)
async def test_retries(
        response_mock, errors_before_response, retries_count, expected_error,
):
    retry_counter = 0

    @wrappers.retries(
        retries_count=retries_count,
        wait_between_retries=1,
        retry_multiplier=1,
        max_random_retry_delay=1,
    )
    async def request(**kwargs):
        nonlocal retry_counter
        if retry_counter < errors_before_response:
            retry_counter += 1
            raise errors.BaseError
        return response_mock(status=200)

    if expected_error:
        with pytest.raises(expected_error):
            await request()
    else:
        response = await request()
        assert response.status == 200
