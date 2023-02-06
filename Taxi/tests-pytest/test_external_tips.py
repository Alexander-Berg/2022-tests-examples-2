import pytest

from taxi.core import async
from taxi.external import tips as tips_service


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
    @patch('taxi.external.tips._perform_request')
    @async.inline_callbacks
    def _perform_request(method, location, params, log_extra):
        assert method == 'POST'
        assert location == expected_location
        assert params == expected_params
        if expected_exception_cls:
            raise expected_exception_cls()
        async.return_value(_Response(response))
        yield

    return _perform_request


@pytest.mark.parametrize(
    ['response', 'expected_exception_cls', 'expected_response'],
    [
        (
            {'need_hold_tips': True, 'time_before_take_tips': 1800},
            None,
            (True, 1800),
        ),
        (
            {'need_hold_tips': False, 'time_before_take_tips': 1800},
            None,
            (False, 1800),
        ),
        (None, tips_service.InvalidRequestError, None),
        (None, tips_service.NotFoundError, None),
        (None, tips_service.RequestError, None),
    ]
)
@pytest.inline_callbacks
def test_need_hold_tips(
        patch,
        response,
        expected_exception_cls,
        expected_response,
):
    order_id = 'some_order_id'
    mocked_func = _patch_perform_request(
        patch,
        expected_location='internal/tips/v1/need-hold-tips',
        expected_params={'order_id': order_id},
        response=response,
        expected_exception_cls=expected_exception_cls,
    )
    try:
        response = yield tips_service.need_hold_tips(order_id)
        assert response == expected_response
    except Exception as exc:
        assert expected_exception_cls is not None
        assert isinstance(exc, expected_exception_cls)
    assert len(mocked_func.calls) == 1


@pytest.inline_callbacks
def test_need_hold_tips_unexpected_response(patch):
    order_id = 'some_order_id'
    mocked_func = _patch_perform_request(
        patch,
        expected_location='internal/tips/v1/need-hold-tips',
        expected_params={'order_id': order_id},
        response={},  # handle must always return both fields on HTTP 200
    )
    try:
        yield tips_service.need_hold_tips(order_id)
        assert False, "tips_service.UnexpectedResponseError must be raised"
    except tips_service.UnexpectedResponseError:
        pass
    assert len(mocked_func.calls) == 1


@pytest.mark.parametrize(
    ['response', 'exception_cls', 'expected_result'],
    [
        ({'new_tips_sum': 600000}, None, 600000),  # happy path
        ({}, None, None),  # empty response - no tips
        (None, tips_service.InvalidRequestError, None),  # invalid request
        (None, tips_service.NotFoundError, None),  # order not found
        (None, tips_service.RequestError, None),
    ]
)
@pytest.inline_callbacks
def test_get_tips_sum(patch, response, exception_cls, expected_result):
    order_id = 'some_order_id'
    mocked_func = _patch_perform_request(
        patch,
        expected_location='internal/tips/v1/get-tips-sum',
        expected_params={'order_id': order_id},
        response=response,
        expected_exception_cls=exception_cls,
    )
    try:
        result = yield tips_service.get_tips_sum(order_id)
        assert result == expected_result
    except Exception as exc:
        assert isinstance(exc, exception_cls)
    assert len(mocked_func.calls) == 1
