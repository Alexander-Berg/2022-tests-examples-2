import operator

import pytest

from tests_scooters_ops import db_utils
from tests_scooters_ops import utils


DRAFT_ID = 'draft_01'


@pytest.mark.config(SCOOTERS_OPS_DRAFTS_SETTINGS_BY_TYPE={})
async def test_no_settings(mockserver, stq_runner, pgsql):
    db_utils.add_draft(
        pgsql,
        {
            'draft_id': DRAFT_ID,
            'type': 'recharge',
            'typed_extra': {'vehicle_id': 'vid'},
        },
    )

    await stq_runner.scooters_ops_process_draft.call(
        task_id=DRAFT_ID, kwargs={'draft_id': DRAFT_ID}, expect_fail=True,
    )


@pytest.mark.config(SCOOTERS_OPS_DRAFTS_SETTINGS_BY_TYPE={'recharge': {}})
@pytest.mark.parametrize(
    'draft_before,draft_after',
    [
        pytest.param(
            {'status': 'failed'},
            {'status': 'failed', 'revision': 1},
            id='draft failed -> do nothing',
        ),
        pytest.param(
            {'status': 'processed'},
            {'status': 'processed', 'revision': 1},
            id='draft processed -> do nothing',
        ),
        pytest.param(
            {'status': 'actual'},
            {'status': 'actual', 'revision': 1},
            id='draft actual -> do nothing',
        ),
    ],
)
async def test_do_not_process(stq_runner, pgsql, draft_before, draft_after):
    db_utils.add_draft(
        pgsql,
        {
            **{
                'draft_id': DRAFT_ID,
                'type': 'recharge',
                'typed_extra': {'vehicle_id': 'vid'},
            },
            **draft_before,
        },
    )

    await stq_runner.scooters_ops_process_draft.call(
        task_id=DRAFT_ID, kwargs={'draft_id': DRAFT_ID},
    )

    utils.assert_partial_diff(db_utils.get_draft(pgsql, DRAFT_ID), draft_after)


@pytest.mark.config(
    SCOOTERS_OPS_DRAFTS_SETTINGS_BY_TYPE={
        'recharge': {
            'required_tags': ['battery_low'],
            'prohibited_tags': ['broken'],
            'unlock_tags': ['battery_low'],
        },
    },
)
async def test_tags_mismatch(mockserver, stq_runner, pgsql, load_json):
    db_utils.add_draft(
        pgsql,
        {
            'draft_id': DRAFT_ID,
            'type': 'recharge',
            'typed_extra': {'vehicle_id': 'vid'},
        },
    )

    @mockserver.json_handler('/scooter-backend/api/taxi/car/details')
    def mock_car_details(request):
        assert request.args['car_id'] == 'vid'
        return load_json('car_details_with_car_no_tags.json')

    @mockserver.json_handler('/scooter-backend/api/taxi/car/tag_remove')
    def mock_tag_remove(request):
        assert request.json == {
            'object_ids': ['vid'],
            'tag_names': ['battery_low'],
        }
        return {}

    await stq_runner.scooters_ops_process_draft.call(
        task_id=DRAFT_ID, kwargs={'draft_id': DRAFT_ID},
    )

    utils.assert_partial_diff(
        db_utils.get_draft(pgsql, DRAFT_ID),
        {'status': 'failed', 'revision': 2},
    )

    assert mock_car_details.times_called == 1
    assert mock_tag_remove.times_called == 1


@pytest.mark.config(
    SCOOTERS_OPS_DRAFTS_SETTINGS_BY_TYPE={
        'recharge': {
            'required_tags': ['battery_low'],
            'lock_tags': ['lockme'],
            'unlock_tags': ['battery_low'],
        },
    },
)
@pytest.mark.parametrize(
    'car_details_responses,calls',
    [
        pytest.param(
            [
                'car_details_car_reservation.json',
                'car_details_car_reservation.json',
            ],
            {'mock_car_details': 2, 'mock_tag_remove': 1},
            id='reserved before locking',
        ),
        pytest.param(
            [
                'car_details_with_car_has_tags.json',
                'car_details_with_car_has_tags.json',
                'car_details_car_reservation.json',
            ],
            {'mock_car_details': 3, 'mock_tag_remove': 1, 'mock_tag_add': 1},
            id='reserved after lock tag added',
        ),
    ],
)
async def test_vehicle_rented(
        mockserver, stq_runner, pgsql, load_json, car_details_responses, calls,
):
    db_utils.add_draft(
        pgsql,
        {
            'draft_id': DRAFT_ID,
            'type': 'recharge',
            'typed_extra': {'vehicle_id': 'vid'},
        },
    )

    @mockserver.json_handler('/scooter-backend/api/taxi/car/details')
    def mock_car_details(request):
        return load_json(car_details_responses.pop(0))

    @mockserver.json_handler('/scooter-backend/api/taxi/car/tag_remove')
    def mock_tag_remove(request):
        assert request.json == {
            'object_ids': ['vid'],
            'tag_names': ['battery_low'],
        }
        return {}

    @mockserver.json_handler('/scooter-backend/api/taxi/car/tag_add')
    def mock_tag_add(request):
        assert request.json == {'object_ids': ['vid'], 'tag_name': 'lockme'}
        assert request.query == {'unique_policy': 'skip_if_exists'}
        return {
            'tagged_objects': [{'object_id': 'vid', 'tag_id': ['tag_id1']}],
        }

    await stq_runner.scooters_ops_process_draft.call(
        task_id=DRAFT_ID, kwargs={'draft_id': DRAFT_ID},
    )

    utils.assert_partial_diff(
        db_utils.get_draft(pgsql, DRAFT_ID),
        {'status': 'failed', 'revision': 2},
    )

    assert mock_car_details.times_called == calls.get('mock_car_details', 0)
    assert mock_tag_remove.times_called == calls.get('mock_tag_remove', 0)
    assert mock_tag_add.times_called == calls.get('mock_tag_add', 0)


@pytest.mark.parametrize(
    'expected_check_tags,expected_tag_add_requests',
    [
        pytest.param(
            {'required_tags': ['battery_low'], 'prohibited_tags': ['dead']},
            [{'object_ids': ['vid'], 'tag_name': 'lockme'}],
            marks=[
                pytest.mark.config(
                    SCOOTERS_OPS_DRAFTS_SETTINGS_BY_TYPE={
                        'recharge': {
                            'required_tags': ['battery_low'],
                            'lock_tags': ['lockme'],
                            'prohibited_tags': ['dead'],
                        },
                    },
                ),
            ],
            id='lock_tags and required_tags do not intersect',
        ),
        pytest.param(
            {'required_tags': [], 'prohibited_tags': ['dead']},
            [
                {'object_ids': ['vid'], 'tag_name': 'lockme'},
                {'object_ids': ['vid'], 'tag_name': 'battery_low'},
            ],
            marks=[
                pytest.mark.config(
                    SCOOTERS_OPS_DRAFTS_SETTINGS_BY_TYPE={
                        'recharge': {
                            'required_tags': ['battery_low'],
                            'lock_tags': ['lockme', 'battery_low'],
                            'prohibited_tags': ['dead'],
                        },
                    },
                ),
            ],
            id='lock_tags contains required',
        ),
    ],
)
async def test_success(
        mockserver,
        stq_runner,
        pgsql,
        load_json,
        testpoint,
        expected_check_tags,
        expected_tag_add_requests,
):
    db_utils.add_draft(
        pgsql,
        {
            'draft_id': DRAFT_ID,
            'type': 'recharge',
            'typed_extra': {'vehicle_id': 'vid'},
        },
    )

    @testpoint('check_draft_vehicle_tags')
    def check_tags_testpoint(data):
        assert data == expected_check_tags

    @mockserver.json_handler('/scooter-backend/api/taxi/car/details')
    def mock_car_details(request):
        return load_json('car_details_with_car_has_tags.json')

    tag_add_requests = []

    @mockserver.json_handler('/scooter-backend/api/taxi/car/tag_add')
    def mock_tag_add(request):
        tag_add_requests.append(request.json)
        assert request.query == {'unique_policy': 'skip_if_exists'}
        return {
            'tagged_objects': [{'object_id': 'vid', 'tag_id': ['tag_id1']}],
        }

    await stq_runner.scooters_ops_process_draft.call(
        task_id=DRAFT_ID, kwargs={'draft_id': DRAFT_ID},
    )

    utils.assert_partial_diff(
        db_utils.get_draft(pgsql, DRAFT_ID),
        {'status': 'actual', 'revision': 2},
    )

    assert sorted(
        tag_add_requests, key=operator.itemgetter('tag_name'),
    ) == sorted(expected_tag_add_requests, key=operator.itemgetter('tag_name'))

    assert check_tags_testpoint.times_called == 1
    assert mock_car_details.times_called == 3
    assert mock_tag_add.times_called == len(expected_tag_add_requests)


@pytest.mark.config(
    SCOOTERS_OPS_DRAFTS_SETTINGS_BY_TYPE={
        'recharge': {
            'required_tags': ['battery_low'],
            'lock_tags': ['lockme'],
            'lock_on': 'mission_preparing',
        },
    },
)
async def test_lock_on_preparing(mockserver, stq_runner, pgsql, load_json):
    db_utils.add_draft(
        pgsql,
        {
            'draft_id': DRAFT_ID,
            'type': 'recharge',
            'typed_extra': {'vehicle_id': 'vid'},
        },
    )

    @mockserver.json_handler('/scooter-backend/api/taxi/car/details')
    def mock_car_details(request):
        return load_json('car_details_with_car_has_tags.json')

    await stq_runner.scooters_ops_process_draft.call(
        task_id=DRAFT_ID, kwargs={'draft_id': DRAFT_ID},
    )

    utils.assert_partial_diff(
        db_utils.get_draft(pgsql, DRAFT_ID),
        {'status': 'actual', 'revision': 2},
    )

    assert mock_car_details.times_called == 1


@pytest.mark.config(SCOOTERS_OPS_DRAFTS_SETTINGS_BY_TYPE={'recharge': {}})
async def test_vehicle_already_has_actual_draft(
        pgsql, stq_runner, mockserver, load_json,
):
    db_utils.add_draft(
        pgsql,
        {
            'draft_id': 'draft01',
            'type': 'recharge',
            'typed_extra': {'vehicle_id': 'vid'},
            'status': 'actual',
        },
    )
    db_utils.add_draft(
        pgsql,
        {
            'draft_id': 'draft02',
            'type': 'recharge',
            'typed_extra': {'vehicle_id': 'vid'},
        },
    )

    @mockserver.json_handler('/scooter-backend/api/taxi/car/details')
    def mock_car_details(request):
        return load_json('car_details_with_car_has_tags.json')

    await stq_runner.scooters_ops_process_draft.call(
        task_id=DRAFT_ID, kwargs={'draft_id': 'draft02'},
    )

    assert db_utils.get_draft(pgsql, 'draft02', fields=['status']) == {
        'status': 'failed',
    }

    assert mock_car_details.times_called == 1
