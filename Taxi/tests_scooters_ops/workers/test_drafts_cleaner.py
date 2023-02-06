import pytest


from tests_scooters_ops import db_utils
from tests_scooters_ops import utils


@pytest.mark.config(
    SCOOTERS_OPS_PERIODICS={
        'sleep_time_ms': 100,
        'drafts_cleaner': {
            'sleep_time_ms': 100,
            'enabled': True,
            'delete_failed_enabled': True,
            'delete_limit': 1,
            'mark_expired_enabled': False,
            'check_actual_enabled': False,
        },
    },
)
@pytest.mark.parametrize(
    'drafts,expected_after',
    [
        pytest.param(
            [{'draft_id': 'hello', 'type': 'recharge', 'status': 'failed'}],
            [],
            id='delete one draft',
        ),
        pytest.param(
            [
                {'draft_id': 'hello', 'type': 'recharge', 'status': 'failed'},
                {'draft_id': 'hello2', 'type': 'recharge', 'status': 'failed'},
            ],
            [{'draft_id': 'hello2'}],
            id='delete one draft by limit',
        ),
        pytest.param(
            [
                {
                    'draft_id': 'deleted_long_ago',
                    'type': 'recharge',
                    'status': 'failed',
                    'updated_at': '2022-03-10T12:00:00+0000',
                },
                {
                    'draft_id': 'deleted_just_now',
                    'type': 'recharge',
                    'status': 'failed',
                    'updated_at': '2022-05-10T11:59:00+0000',
                },
            ],
            [{'draft_id': 'deleted_just_now'}],
            marks=[
                pytest.mark.config(
                    SCOOTERS_OPS_PERIODICS={
                        'sleep_time_ms': 100,
                        'drafts_cleaner': {
                            'sleep_time_ms': 100,
                            'enabled': True,
                            'delete_failed_enabled': True,
                            'delete_limit': 100,
                            'delete_delay_s': 3600,
                            'mark_expired_enabled': False,
                            'check_actual_enabled': False,
                        },
                    },
                ),
            ],
            id='delete one by delay',
        ),
    ],
)
@pytest.mark.now('2022-05-10T12:00:00+0000')
async def test_delete_failed(
        taxi_scooters_ops, pgsql, now, drafts, expected_after,
):
    for draft in drafts:
        db_utils.add_draft(pgsql, {**{'updated_at': now}, **draft})

    await taxi_scooters_ops.run_task('testsuite-drafts-cleaner')

    utils.assert_partial_diff(db_utils.get_drafts(pgsql), expected_after)


@pytest.mark.config(
    SCOOTERS_OPS_PERIODICS={
        'sleep_time_ms': 100,
        'drafts_cleaner': {
            'sleep_time_ms': 100,
            'enabled': True,
            'delete_failed_enabled': False,
            'delete_limit': 1,
            'mark_expired_enabled': True,
            'check_actual_enabled': False,
        },
    },
    SCOOTERS_OPS_DRAFTS_SETTINGS_BY_TYPE={
        'recharge': {'unlock_tags': ['battery_low']},
    },
)
@pytest.mark.now('2022-05-10T12:00:00+0000')
async def test_mark_expired(taxi_scooters_ops, pgsql, mockserver):
    db_utils.add_draft(
        pgsql,
        {
            'draft_id': 'expired',
            'type': 'recharge',
            'status': 'actual',
            'expires_at': '2022-05-10T11:00:00+0000',
            'typed_extra': {'vehicle_id': 'vid1'},
        },
    )
    db_utils.add_draft(
        pgsql,
        {
            'draft_id': 'notexpired',
            'type': 'recharge',
            'status': 'actual',
            'expires_at': '2022-05-10T13:00:00+0000',
            'typed_extra': {'vehicle_id': 'vid2'},
        },
    )

    @mockserver.json_handler('/scooter-backend/api/taxi/car/tag_remove')
    def mock_tag_remove(request):
        assert request.json == {
            'object_ids': ['vid1'],
            'tag_names': ['battery_low'],
        }
        return {}

    await taxi_scooters_ops.run_task('testsuite-drafts-cleaner')

    utils.assert_partial_diff(
        db_utils.get_drafts(pgsql),
        [
            {'draft_id': 'expired', 'status': 'failed'},
            {'draft_id': 'notexpired', 'status': 'actual'},
        ],
    )

    assert mock_tag_remove.times_called == 1


@pytest.mark.config(
    SCOOTERS_OPS_PERIODICS={
        'sleep_time_ms': 100,
        'drafts_cleaner': {
            'sleep_time_ms': 100,
            'enabled': True,
            'delete_failed_enabled': False,
            'delete_limit': 1,
            'mark_expired_enabled': False,
            'check_actual_enabled': True,
        },
    },
    SCOOTERS_OPS_DRAFTS_SETTINGS_BY_TYPE={
        'recharge': {
            'required_tags': ['hello'],
            'unlock_tags': ['battery_low'],
        },
    },
)
async def test_check_actual(
        taxi_scooters_ops, pgsql, mockserver, load_json, testpoint,
):
    db_utils.add_draft(
        pgsql,
        {
            'draft_id': 'bad-tags',
            'type': 'recharge',
            'status': 'actual',
            'typed_extra': {'vehicle_id': 'vid1'},
        },
    )
    db_utils.add_draft(
        pgsql,
        {
            'draft_id': 'good-tags',
            'type': 'recharge',
            'status': 'actual',
            'typed_extra': {'vehicle_id': 'vid2'},
        },
    )
    db_utils.add_draft(
        pgsql,
        {
            'draft_id': 'vehicle-not-found',
            'type': 'recharge',
            'status': 'actual',
            'typed_extra': {'vehicle_id': 'absent'},
        },
    )

    @testpoint('check_draft_vehicle_tags')
    def check_tags_testpoint(data):
        assert data == {'prohibited_tags': [], 'required_tags': ['hello']}

    @mockserver.json_handler('/scooter-backend/api/taxi/car/details')
    def mock_car_details(request):
        return load_json('car_details.json')

    @mockserver.json_handler('/scooter-backend/api/taxi/car/tag_remove')
    def mock_tag_remove(request):
        assert request.json == {
            'object_ids': ['vid1'],
            'tag_names': ['battery_low'],
        }
        return {}

    await taxi_scooters_ops.run_task('testsuite-drafts-cleaner')

    utils.assert_partial_diff(
        db_utils.get_drafts(pgsql),
        [
            {'draft_id': 'bad-tags', 'status': 'failed'},
            {'draft_id': 'good-tags', 'status': 'actual'},
            {'draft_id': 'vehicle-not-found', 'status': 'failed'},
        ],
    )

    assert check_tags_testpoint.times_called == 2
    assert mock_car_details.times_called == 1
    assert mock_tag_remove.times_called == 1
