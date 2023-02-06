import pytest

from taxi.core import async
from taxi.internal import user_manager
from taxi.internal.order_kit import cancel_handler


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize(
    'order_finished,late_in_transporting,can_be_canclled',
    [
        (True, False, False),
        (False, False, True),
        (True, True, False),
        (False, True, False),
    ]
)
def test_can_order_be_cancelled(
        stub, patch, order_finished, late_in_transporting, can_be_canclled):

    @patch('taxi.internal.order_kit.cancel_handler._is_late_in_transporting')
    def _is_late_in_transporting(order):
        return late_in_transporting

    order = stub(finished=order_finished)
    assert cancel_handler.can_order_be_cancelled(order) is can_be_canclled


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize('user_position,driver_point', [
    (None, object()),
    (object(), None),
])
@pytest.inline_callbacks
def test_can_be_cancelled_by_user_without_data(user_position, driver_point):
    assert (yield cancel_handler.can_be_cancelled_by_user(
        user_position, driver_point
    ))


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize('accuracy,distance,max_distance,expected', [
    (0, 999, 1000, False),
    (0, 1001, 1000, True),
    (1, 1000, 1000, True),
])
@pytest.inline_callbacks
def test_can_be_cancelled_by_user(
        patch, stub, accuracy, distance, max_distance, expected):
    driver_point = (37.6, 55.6)
    user_point = (37.5, 55.7)
    user_position = user_manager.UserPosition(user_point, accuracy)

    @patch(
        'taxi.internal.order_kit.cancel_handler.'
        '_get_max_allowed_distance_to_cancel')
    @async.inline_callbacks
    def _get_max_allowed_distance_to_cancel():
        yield
        async.return_value(max_distance)

    @patch('taxi.util.geometry.approx_distance')
    def approx_distance(point1, point2):
        return distance

    result = yield cancel_handler.can_be_cancelled_by_user(
        user_position, driver_point
    )

    assert result is expected
