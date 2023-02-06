import datetime

import pytest


@pytest.mark.parametrize(
    ['license_pd_id', 'found', 'spurious'],
    (
        pytest.param('id1', True, False, id='found_excluded_1'),
        pytest.param('id2', True, False, id='found_excluded_2'),
        pytest.param('id3', True, False, id='found_forever_excluded'),
        pytest.param(
            'id1',
            True,
            False,
            id='found_excluded_with_delta',
            marks=pytest.mark.config(EXCLUDED_DRIVERS_DELTA=60),
        ),
        pytest.param(
            'id2',
            False,
            False,
            id='not_found_excluded_with_delta',
            marks=pytest.mark.config(EXCLUDED_DRIVERS_DELTA=60),
        ),
        pytest.param(
            'id3',
            True,
            False,
            id='found_forever_excluded_with_delta',
            marks=pytest.mark.config(EXCLUDED_DRIVERS_DELTA=60),
        ),
        pytest.param('id4', False, False, id='no_exclusion'),
        pytest.param(
            'id5', True, True, id='check_on_same_order_after_exclusion',
        ),
    ),
)
async def test_check_order(
        taxi_excluded_drivers,
        stq_runner,
        testpoint,
        license_pd_id,
        found,
        spurious,
):
    order_id = 'order_id'
    phone_id = {'$oid': '5bbb5faf15870bd76635d5e2'}
    license_pd_id = license_pd_id
    assigned_at = datetime.datetime(2018, 8, 10, 21, 1, 30)

    @testpoint('found-assigned-excluded-drivers')
    def handle_found(arg):
        pass

    @testpoint('not-found-assigned-excluded-drivers')
    def handle_not_found(arg):
        pass

    @testpoint('spurious-found-assigned-excluded-drivers')
    def handle_spurious_found(arg):
        pass

    await taxi_excluded_drivers.enable_testpoints()

    await stq_runner.excluded_drivers_check_order.call(
        task_id='id', args=[order_id, phone_id, license_pd_id, assigned_at],
    )

    if found:
        if not spurious:
            assert handle_found.times_called == 1
            assert handle_not_found.times_called == 0
        else:
            assert handle_spurious_found.times_called == 1
    else:
        assert handle_found.times_called == 0
        assert handle_not_found.times_called == 1
