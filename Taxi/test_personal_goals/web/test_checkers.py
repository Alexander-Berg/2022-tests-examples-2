import datetime
import typing

from bson import tz_util
import pytest

from personal_goals import models as goals
from personal_goals.models import parse
from personal_goals.modules.goalcheck import check as goalcheck
from personal_goals.modules.goalcheck import exceptions as error_code
from personal_goals.modules.goalcheck import models


class ExceptionCatcher(typing.NamedTuple):
    raised: bool
    exception: typing.Optional[error_code.CheckException] = None


def _make_ride_goal(conditions: dict):
    conditions = {
        'type': 'ride',
        'count': 5,
        'date_finish': '2019-07-24T18:29:55.372+03:00',
        **conditions,
    }
    result = goals.parse.parse_conditions(conditions)
    return models.UserGoal(goal_id='random', conditions=result)


async def exception_catcher(checker, *args, **kwargs) -> ExceptionCatcher:
    try:
        await checker(*args, **kwargs)
    except error_code.CheckException as exc:
        return ExceptionCatcher(raised=True, exception=exc)
    return ExceptionCatcher(raised=False)


@pytest.mark.parametrize(
    'condition_tariffs, tariff, raises',
    [
        (['econom', 'confortplus'], 'econom', False),
        (['econom', 'confortplus'], 'business', True),
    ],
)
async def test_classes(condition_tariffs, tariff, raises, make_default_order):
    goal = _make_ride_goal({'classes': condition_tariffs})
    order = make_default_order({'performer': {'tariff': {'class': tariff}}})
    order_info = parse.parse_order(order)

    catcher = await exception_catcher(
        # pylint: disable=W0212
        goalcheck._check_classes,
        goal,
        order_info,
    )
    assert catcher.raised == raises
    if catcher.raised:
        assert catcher.exception.error_code == error_code.ERROR_INVALID_CLASS


@pytest.mark.parametrize(
    'airport, source_type, raises',
    [
        (True, 'аэропорт', False),
        (True, 'другое', True),
        (False, 'аэропорт', False),
        (False, 'другое', False),
    ],
)
async def test_source_type(airport, source_type, raises, make_default_order):
    goal = _make_ride_goal({'source': {'airport': airport}})
    order = make_default_order(
        {
            'request': {
                'source': {'object_type': source_type},
                'destinations': [],
            },
        },
    )
    order_info = parse.parse_order(order)

    catcher = await exception_catcher(
        # pylint: disable=W0212
        goalcheck._check_source,
        goal,
        order_info,
    )
    assert catcher.raised == raises
    if catcher.raised:
        code = catcher.exception.error_code
        assert code == error_code.ERROR_NOT_AIRPORT_SOURCE


@pytest.mark.parametrize(
    'source_zones, order_zone, raises',
    [(['moscow', 'kirov'], 'moscow', False), (['kirov'], 'moscow', True)],
)
async def test_source_zones(
        source_zones, order_zone, raises, make_default_order,
):
    goal = _make_ride_goal({'source': {'zones': source_zones}})
    order = make_default_order({'nz': order_zone})
    order_info = parse.parse_order(order)

    catcher = await exception_catcher(
        # pylint: disable=W0212
        goalcheck._check_source,
        goal,
        order_info,
    )
    assert catcher.raised == raises
    if catcher.raised:
        code = catcher.exception.error_code
        assert code == error_code.ERROR_INVALID_SOURCE_ZONE


@pytest.mark.parametrize(
    'airport, destinations, raises',
    [
        (True, ['аэропорт'], False),
        (True, ['другое'], True),
        (False, ['аэропорт'], False),
        (True, ['другое', 'аэропорт'], False),
    ],
)
async def test_destination_type(
        airport, destinations, raises, make_default_order,
):
    goal = _make_ride_goal({'destination': {'airport': airport}})
    order = make_default_order(
        {
            'request': {
                'destinations': [
                    {'object_type': destination_type}
                    for destination_type in destinations
                ],
                'source': {},
            },
        },
    )
    order_info = parse.parse_order(order)

    catcher = await exception_catcher(
        # pylint: disable=W0212
        goalcheck._check_destination,
        goal,
        order_info,
    )
    assert catcher.raised == raises
    if catcher.raised:
        code = catcher.exception.error_code
        assert code == error_code.ERROR_NOT_AIRPORT_DESTINATION


@pytest.mark.parametrize(
    'payment_types, order_payment, raises',
    [(['cash', 'card'], 'card', False), (['cash', 'googlepay'], 'card', True)],
)
async def test_payment_type(
        payment_types, order_payment, raises, make_default_order,
):
    goal = _make_ride_goal({'payment_types': payment_types})
    order = make_default_order({'payment_tech': {'type': order_payment}})
    order_info = parse.parse_order(order)

    catcher = await exception_catcher(
        # pylint: disable=W0212
        goalcheck._check_payment,
        goal,
        order_info,
    )
    assert catcher.raised == raises
    if catcher.raised:
        code = catcher.exception.error_code
        assert code == error_code.ERROR_INVALID_PAYMENT_TYPE


@pytest.mark.parametrize(
    'date_start, created, raises',
    [
        (
            '2019-07-24T19:21:55.372+03:00',
            datetime.datetime(2019, 7, 24, 16, 25, 55, tzinfo=tz_util.utc),
            False,
        ),
        (
            '2019-07-24T19:29:55.372+03:00',
            datetime.datetime(2019, 7, 24, 16, 10, 55, tzinfo=tz_util.utc),
            True,
        ),
    ],
)
async def test_date_start(date_start, created, raises, make_default_order):
    goal = _make_ride_goal({'date_start': date_start})
    order = make_default_order({'created': created})
    order_info = parse.parse_order(order)

    catcher = await exception_catcher(
        # pylint: disable=W0212
        goalcheck._check_date_start,
        goal,
        order_info,
    )
    assert catcher.raised == raises
    if catcher.raised:
        code = catcher.exception.error_code
        assert code == error_code.ERROR_TOO_EARLY


@pytest.mark.parametrize(
    'date_finish, created, raises',
    [
        (
            '2019-07-24T21:21:55.372+03:00',
            datetime.datetime(2019, 7, 24, 16, 25, 55, tzinfo=tz_util.utc),
            False,
        ),
        (
            '2019-07-24T18:29:55.372+03:00',
            datetime.datetime(2019, 7, 24, 16, 10, 55, tzinfo=tz_util.utc),
            True,
        ),
    ],
)
async def test_date_finish(date_finish, created, raises, make_default_order):
    goal = _make_ride_goal({'date_finish': date_finish})
    order = make_default_order({'created': created})
    order_info = parse.parse_order(order)

    catcher = await exception_catcher(
        # pylint: disable=W0212
        goalcheck._check_date_finish,
        goal,
        order_info,
    )
    assert catcher.raised == raises
    if catcher.raised:
        code = catcher.exception.error_code
        assert code == error_code.ERROR_TOO_LATE
