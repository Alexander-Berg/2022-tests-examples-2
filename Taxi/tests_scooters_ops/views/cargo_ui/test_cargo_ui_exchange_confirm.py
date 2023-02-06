import pytest

from tests_scooters_ops import common
from tests_scooters_ops import db_utils
from tests_scooters_ops import utils
import tests_scooters_ops.views.cargo_ui.common as ui_common

HANDLER = '/driver/v1/scooters-ops/v1/cargo-ui/exchange/confirm'


def _create_mission(
        first_point_status=None,
        first_point_first_job_status=None,
        first_point_first_job_type=None,
        first_point_first_job_extra=None,
        first_point_second_job_status=None,
        first_point_second_job_type=None,
        first_point_second_job_extra=None,
        second_point_status=None,
        second_point_job_type=None,
        second_point_job_extra=None,
):
    return {
        'mission_id': 'mission_id_1',
        'cargo_claim_id': 'claim_uuid_1',
        'performer_id': 'performer_1',
        'created_at': '2022-02-14T6:30:00+03',
        'points': [
            {
                'point_id': 'point_id1',
                'cargo_point_id': '2',
                'type': 'depot',
                'typed_extra': {'depot': {'id': 'depot1'}},
                'status': first_point_status or 'arrived',
                'jobs': [
                    {
                        'job_id': 'first_point_job_id1',
                        'status': first_point_first_job_status or 'completed',
                        'type': (first_point_first_job_type or 'do_nothing'),
                        'expected_execution_time': '60 seconds',
                        'typed_extra': first_point_first_job_extra or {},
                    },
                    {
                        'job_id': 'first_point_job_id2',
                        'status': first_point_second_job_status or 'completed',
                        'type': (first_point_second_job_type or 'do_nothing'),
                        'expected_execution_time': '60 seconds',
                        'typed_extra': first_point_second_job_extra or {},
                    },
                ],
            },
            {
                'point_id': 'point_id2',
                'cargo_point_id': '3',
                'type': 'depot',
                'typed_extra': {'depot': {'id': 'depot2'}},
                'address': 'Вот сюда надо приехать',
                'eta': '2022-02-14T10:00:00+00:00',
                'status': second_point_status or 'planned',
                'jobs': [
                    {
                        'job_id': 'second_point_job_id',
                        'status': 'performing',
                        'type': second_point_job_type or 'do_nothing',
                        'expected_execution_time': '60 seconds',
                        'typed_extra': second_point_job_extra or {},
                    },
                ],
            },
        ],
    }


def _create_point_draft(point_id):
    return {
        'draft_id': 'point_draft',
        'type': 'recharge',
        'revision': 1,
        'typed_extra': {'vehicle_id': 'vehicle_id'},
        'mission_id': 'mission_id_1',
        'point_id': point_id,
    }


def _create_job_draft(point_id, job_id, draft_type=None, typed_extra=None):
    return {
        'draft_id': 'job_draft',
        'type': draft_type or 'recharge',
        'revision': 1,
        'typed_extra': typed_extra or {'vehicle_id': 'vehicle_id'},
        'mission_id': 'mission_id_1',
        'point_id': point_id,
        'job_id': job_id,
    }


REQUEST_BODY = {
    'cargo_ref_id': 'unique_cargo_ref_id',
    'last_known_status': 'pickup_confirmation',
    'point_id': 1,
}


@common.DEEPLINKS_CONFIG
@common.TRANSLATIONS
@common.SCOOTERS_PROBLEMS_CONFIG
@pytest.mark.config(
    SCOOTERS_OPS_DRAFTS_SETTINGS_BY_TYPE={
        'recharge': {'unlock_tags': ['battery_low']},
    },
)
@pytest.mark.now('2022-02-14T12:00:00+03')
@pytest.mark.parametrize(
    'first_point_first_job_type, first_point_first_job_extra, '
    'first_point_second_job_type, first_point_second_job_extra, '
    'first_point_second_job_extra_new, response_json',
    [
        pytest.param(
            'pickup_vehicles',
            {
                'vehicles': [
                    {'id': 'vehicle_id1', 'status': 'processed'},
                    {
                        'id': 'vehicle_id2',
                        'status': 'problems',
                        'problems': ['not_found'],
                    },
                    {'id': 'vehicle_id3', 'status': 'processed'},
                ],
            },
            'dropoff_vehicles',
            {'quantity': 3, 'vehicles': []},
            {
                'quantity': 3,
                'vehicles': [],
                'vehicle_with_problems_ids': ['vehicle_id2'],
            },
            'items_to_dropoff_screen.json',
            id='exchange_confirm_not_last_job_dropoff_screen',
        ),
        pytest.param(
            'pickup_vehicles',
            {
                'vehicles': [
                    {
                        'id': 'vehicle_id2',
                        'status': 'problems',
                        'problems': ['not_found'],
                    },
                ],
            },
            'dropoff_vehicles',
            {'quantity': 1, 'vehicles': []},
            {
                'quantity': 1,
                'vehicles': [],
                'vehicle_with_problems_ids': ['vehicle_id2'],
            },
            'no_items_to_dropoff_screen.json',
            id='exchange_confirm_not_last_job_no_dropoff_items_screen',
        ),
        pytest.param(
            'do_nothing',
            {},
            'pickup_vehicles',
            {
                'vehicles': [
                    {
                        'id': 'vehicle_id1',
                        'number': '0001',
                        'status': 'pending',
                    },
                    {
                        'id': 'vehicle_id2',
                        'number': '0002',
                        'status': 'pending',
                    },
                ],
            },
            None,
            'items_to_pickup_screen.json',
            id='exchange_confirm_not_last_job_pickup_screen',
        ),
    ],
)
async def test_cargo_ui_exchange_confirm_ok_not_last_job_at_point(
        taxi_scooters_ops,
        cargo_orders,
        mockserver,
        load_json,
        pgsql,
        first_point_first_job_type,
        first_point_first_job_extra,
        first_point_second_job_type,
        first_point_second_job_extra,
        first_point_second_job_extra_new,
        response_json,
):
    @mockserver.json_handler('/scooter-backend/api/taxi/car/tag_remove')
    def mock_tag_remove(request):
        assert request.json == {
            'object_ids': ['vehicle_id'],
            'tag_names': ['battery_low'],
        }
        return {}

    db_utils.add_mission(
        pgsql,
        _create_mission(
            first_point_first_job_status='performing',
            first_point_first_job_type=first_point_first_job_type,
            first_point_first_job_extra=first_point_first_job_extra,
            first_point_second_job_status='planned',
            first_point_second_job_type=first_point_second_job_type,
            first_point_second_job_extra=first_point_second_job_extra,
        ),
    )

    db_utils.add_draft(pgsql, _create_point_draft('point_id1'))
    db_utils.add_draft(
        pgsql, _create_job_draft('point_id1', 'first_point_job_id1'),
    )

    resp = await taxi_scooters_ops.post(
        HANDLER, headers=common.DAP_HEADERS, json=REQUEST_BODY,
    )

    assert resp.status == 200
    assert ui_common.stabilize_response(resp.json()) == load_json(
        response_json,
    )

    point = db_utils.get_points(pgsql, ids=['point_id1'], job_params={})[0]
    utils.assert_partial_diff(
        point,
        {
            'status': 'arrived',
            'jobs': [
                {
                    'status': 'completed',
                    'typed_extra': first_point_first_job_extra,
                },
                {
                    'status': 'performing',
                    'typed_extra': (
                        first_point_second_job_extra_new
                        or first_point_second_job_extra
                    ),
                },
            ],
        },
    )

    history = db_utils.get_history(pgsql, fields=['type', 'extra'])
    expected_history = [
        {
            'extra': {'job_type': first_point_first_job_type},
            'type': 'job_completed',
        },
        {
            'extra': {'job_type': first_point_second_job_type},
            'type': 'job_started',
        },
    ]
    utils.assert_partial_diff(history, expected_history)

    assert db_utils.get_draft(
        pgsql, 'job_draft', fields=['status', 'revision'],
    ) == {'status': 'processed', 'revision': 2}

    assert db_utils.get_draft(
        pgsql, 'point_draft', fields=['status', 'revision'],
    ) == {'status': 'pending', 'revision': 1}

    assert cargo_orders.exchange_confirm.times_called == 0
    assert cargo_orders.get_order_info.times_called == 1
    assert mock_tag_remove.times_called == 1


@common.DEEPLINKS_CONFIG
@common.TRANSLATIONS
@common.SCOOTERS_PROBLEMS_CONFIG
@pytest.mark.config(
    SCOOTERS_OPS_DRAFTS_SETTINGS_BY_TYPE={
        'recharge': {'unlock_tags': ['battery_low']},
    },
)
@pytest.mark.now('2022-02-14T12:00:00+03')
@pytest.mark.parametrize(
    'first_point_second_job_type, first_point_second_job_extra, response_json',
    [
        pytest.param(
            'dropoff_vehicles',
            {
                'quantity': 2,
                'vehicles': [
                    {
                        'id': 'vehicle_id2',
                        'number': '0002',
                        'status': 'processed',
                    },
                ],
                'vehicle_with_problems_ids': ['vehicle_id1'],
            },
            'to_point_screen.json',
            id='exchange_confirm_last_point_job_is_dropoff_vehicles',
        ),
        pytest.param(
            'pickup_vehicles',
            {
                'vehicles': [
                    {
                        'id': 'vehicle_id1',
                        'number': '0001',
                        'status': 'processed',
                    },
                    {
                        'id': 'vehicle_id2',
                        'status': 'problems',
                        'problems': ['not_found'],
                    },
                ],
            },
            'to_point_screen.json',
            id='exchange_confirm_last_point_job_is_pickup_vehicles',
        ),
    ],
)
async def test_cargo_ui_exchange_confirm_ok_to_the_next_point(
        taxi_scooters_ops,
        cargo_orders,
        mockserver,
        load_json,
        pgsql,
        first_point_second_job_type,
        first_point_second_job_extra,
        response_json,
):
    @mockserver.json_handler('/scooter-backend/api/taxi/car/tag_remove')
    def mock_tag_remove(request):
        assert request.json == {
            'object_ids': ['vehicle_id'],
            'tag_names': ['battery_low'],
        }
        return {}

    db_utils.add_mission(
        pgsql,
        _create_mission(
            first_point_second_job_status='performing',
            first_point_second_job_type=first_point_second_job_type,
            first_point_second_job_extra=first_point_second_job_extra,
        ),
    )

    db_utils.add_draft(pgsql, _create_point_draft('point_id1'))
    db_utils.add_draft(
        pgsql, _create_job_draft('point_id1', 'first_point_job_id1'),
    )

    resp = await taxi_scooters_ops.post(
        HANDLER, headers=common.DAP_HEADERS, json=REQUEST_BODY,
    )

    assert resp.status == 200
    assert ui_common.stabilize_response(resp.json()) == load_json(
        response_json,
    )

    points = db_utils.get_points(
        pgsql, ids=['point_id1', 'point_id2'], job_params={},
    )
    utils.assert_partial_diff(
        points,
        [
            {
                'status': 'visited',
                'jobs': [
                    {'status': 'completed', 'typed_extra': {}},
                    {
                        'status': 'completed',
                        'typed_extra': first_point_second_job_extra,
                    },
                ],
            },
            {'status': 'planned'},
        ],
    )

    history = db_utils.get_history(pgsql, fields=['type', 'extra'])
    expected_history = [
        {
            'extra': {'job_type': first_point_second_job_type},
            'type': 'job_completed',
        },
        {
            'extra': {
                'point_extra': {'depot': {'id': 'depot1'}},
                'point_type': 'depot',
            },
            'type': 'point_completed',
        },
    ]
    utils.assert_partial_diff(history, expected_history)

    assert db_utils.get_draft(
        pgsql, 'job_draft', fields=['status', 'revision'],
    ) == {'status': 'processed', 'revision': 2}

    assert db_utils.get_draft(
        pgsql, 'point_draft', fields=['status', 'revision'],
    ) == {'status': 'processed', 'revision': 2}

    assert cargo_orders.exchange_confirm.times_called == 1
    assert cargo_orders.get_order_info.times_called == 1
    assert mock_tag_remove.times_called == 2


@common.DEEPLINKS_CONFIG
@common.TRANSLATIONS
@common.SCOOTERS_PROBLEMS_CONFIG
@pytest.mark.config(
    SCOOTERS_OPS_DRAFTS_SETTINGS_BY_TYPE={
        'recharge': {'unlock_tags': ['battery_low']},
    },
)
@pytest.mark.now('2022-02-14T12:00:00+03')
@pytest.mark.parametrize(
    'second_point_job_type, second_point_job_extra, response_json',
    [
        pytest.param(
            'dropoff_vehicles',
            {
                'quantity': 1,
                'vehicles': [
                    {
                        'id': 'vehicle_id2',
                        'number': '0002',
                        'status': 'processed',
                    },
                ],
            },
            'final_screen.json',
            id='exchange_confirm_last_job_is_dropoff_vehicles',
        ),
    ],
)
async def test_cargo_ui_exchange_confirm_ok_final_screen(
        taxi_scooters_ops,
        cargo_orders,
        mockserver,
        load_json,
        pgsql,
        second_point_job_type,
        second_point_job_extra,
        response_json,
):
    @mockserver.json_handler('/scooter-backend/api/taxi/car/tag_remove')
    def mock_tag_remove(request):
        assert request.json == {
            'object_ids': ['vehicle_id'],
            'tag_names': ['battery_low'],
        }
        return {}

    cargo_orders.resolve_current_point_and_move()

    db_utils.add_mission(
        pgsql,
        _create_mission(
            second_point_status='arrived',
            second_point_job_type=second_point_job_type,
            second_point_job_extra=second_point_job_extra,
        ),
    )

    db_utils.add_draft(pgsql, _create_point_draft('point_id2'))
    db_utils.add_draft(
        pgsql, _create_job_draft('point_id2', 'second_point_job_id'),
    )

    resp = await taxi_scooters_ops.post(
        HANDLER, headers=common.DAP_HEADERS, json=REQUEST_BODY,
    )

    assert resp.status == 200
    assert ui_common.stabilize_response(resp.json()) == load_json(
        response_json,
    )

    points = db_utils.get_points(pgsql, ids=['point_id2'], job_params={})
    utils.assert_partial_diff(
        points,
        [
            {
                'status': 'visited',
                'jobs': [
                    {
                        'status': 'completed',
                        'typed_extra': second_point_job_extra,
                    },
                ],
            },
        ],
    )

    history = db_utils.get_history(pgsql, fields=['type', 'extra'])
    expected_history = [
        {
            'extra': {'job_type': second_point_job_type},
            'type': 'job_completed',
        },
        {
            'extra': {
                'point_extra': {'depot': {'id': 'depot2'}},
                'point_type': 'depot',
            },
            'type': 'point_completed',
        },
    ]
    utils.assert_partial_diff(history, expected_history)

    assert db_utils.get_draft(
        pgsql, 'job_draft', fields=['status', 'revision'],
    ) == {'status': 'processed', 'revision': 2}

    assert db_utils.get_draft(
        pgsql, 'point_draft', fields=['status', 'revision'],
    ) == {'status': 'processed', 'revision': 2}

    assert cargo_orders.exchange_confirm.times_called == 1
    assert cargo_orders.get_order_info.times_called == 1
    assert mock_tag_remove.times_called == 2


@common.DEEPLINKS_CONFIG
@common.TRANSLATIONS
@common.SCOOTERS_PROBLEMS_CONFIG
@pytest.mark.config(
    SCOOTERS_OPS_DRAFTS_SETTINGS_BY_TYPE={
        'dropoff_vehicles': {'unlock_tags': ['battery_low']},
    },
)
@pytest.mark.now('2022-02-14T12:00:00+03')
@pytest.mark.parametrize(
    'is_last_point_job',
    [
        pytest.param(True, id='dropoff_draft_visited_point'),
        pytest.param(False, id='dropoff_draft_finished_not_last_point_job'),
    ],
)
async def test_cargo_ui_exchange_confirm_ok_dropoff_drafts(
        taxi_scooters_ops, cargo_orders, mockserver, pgsql, is_last_point_job,
):
    @mockserver.json_handler('/scooter-backend/api/taxi/car/tag_remove')
    def mock_tag_remove(request):
        assert request.json == {
            'object_ids': ['vehicle_id1', 'vehicle_id3', 'vehicle_id2'],
            'tag_names': ['battery_low'],
        }
        return {}

    dropoff_vehicles_extra = {
        'quantity': 3,
        'vehicles': [
            {'id': 'vehicle_id2', 'number': '0002', 'status': 'processed'},
            {'id': 'vehicle_id3', 'number': '0003', 'status': 'processed'},
        ],
        'vehicle_with_problems_ids': ['vehicle_id1'],
    }

    if is_last_point_job:
        db_utils.add_mission(
            pgsql,
            _create_mission(
                first_point_second_job_status='performing',
                first_point_second_job_type='dropoff_vehicles',
                first_point_second_job_extra=dropoff_vehicles_extra,
            ),
        )
    else:
        db_utils.add_mission(
            pgsql,
            _create_mission(
                first_point_first_job_status='performing',
                first_point_first_job_type='dropoff_vehicles',
                first_point_first_job_extra=dropoff_vehicles_extra,
                first_point_second_job_status='planned',
                first_point_second_job_type='dropoff_vehicles',
                first_point_second_job_extra=dropoff_vehicles_extra,
            ),
        )

    db_utils.add_draft(
        pgsql,
        _create_job_draft(
            'point_id1',
            'first_point_job_id2'
            if is_last_point_job
            else 'first_point_job_id1',
            'dropoff_vehicles',
            {
                'point_id': 'point_id1',
                'point_type': 'depot',
                'location': (37, 55),
                'dropoff': 1,
                'score': 1,
            },
        ),
    )

    resp = await taxi_scooters_ops.post(
        HANDLER, headers=common.DAP_HEADERS, json=REQUEST_BODY,
    )

    assert resp.status == 200

    draft = db_utils.get_draft(
        pgsql, 'job_draft', fields=['status', 'revision', 'typed_extra'],
    )
    utils.assert_partial_diff(
        draft,
        {
            'status': 'processed',
            'revision': 3,
            'typed_extra': {
                'vehicle_ids': ['vehicle_id1', 'vehicle_id3', 'vehicle_id2'],
            },
        },
    )

    assert cargo_orders.exchange_confirm.times_called == is_last_point_job
    assert cargo_orders.get_order_info.times_called == 1
    assert mock_tag_remove.times_called == 1


@common.DEEPLINKS_CONFIG
@common.TRANSLATIONS
@pytest.mark.now('2022-02-14T12:00:00+03')
@pytest.mark.parametrize(
    'first_point_status, first_point_first_job_status, '
    'first_point_first_job_type, first_point_first_job_extra, '
    'error_code, expected_json',
    [
        pytest.param(
            'planned',
            None,
            None,
            None,
            400,
            {'code': '400', 'message': 'Какая-то ужасная ошибка'},
            id='not_arrived_yet',
        ),
        pytest.param(
            'arrived',
            'planned',
            None,
            None,
            400,
            {'code': '400', 'message': 'Какая-то ужасная ошибка'},
            id='not_performing_yet',
        ),
        pytest.param(
            'arrived',
            'performing',
            'pickup_vehicles',
            {
                'vehicles': [
                    {'id': '1', 'number': '1', 'status': 'processed'},
                    {'id': '2', 'number': '2', 'status': 'pending'},
                ],
            },
            400,
            {'code': '400', 'message': 'Загрузил не все'},
            id='pickup_vehicles_not_all_processed',
        ),
        pytest.param(
            'arrived',
            'performing',
            'dropoff_vehicles',
            {
                'quantity': 2,
                'vehicles': [
                    {'id': '1', 'number': '1', 'status': 'processed'},
                ],
            },
            400,
            {
                'code': '400',
                'message': 'Выгрузил меньше, чем нужно. Осталось 1',
            },
            id='dropoff_vehicles_not_all_processed',
        ),
    ],
)
async def test_cargo_ui_exchange_confirm_relocation_errors(
        taxi_scooters_ops,
        pgsql,
        cargo_orders,
        first_point_status,
        first_point_first_job_status,
        first_point_first_job_type,
        first_point_first_job_extra,
        error_code,
        expected_json,
):
    db_utils.add_mission(
        pgsql,
        _create_mission(
            first_point_status=first_point_status,
            first_point_first_job_status=first_point_first_job_status,
            first_point_first_job_type=first_point_first_job_type,
            first_point_first_job_extra=first_point_first_job_extra,
        ),
    )

    response = await taxi_scooters_ops.post(
        HANDLER, headers=common.DAP_HEADERS, json=REQUEST_BODY,
    )

    assert response.status == error_code
    assert response.json() == expected_json

    assert cargo_orders.exchange_confirm.times_called == 0


@common.TRANSLATIONS
@pytest.mark.parametrize(
    [
        'accumulator_statuses',
        'scooters_accumulator_response',
        'expected_response',
    ],
    [
        pytest.param(
            ['pickuped', 'booked'],
            {},
            {
                'code': 400,
                'json': {
                    'code': '400',
                    'message': 'Надо бы все таки забрать все аккумы',
                },
            },
            id='test_not_all_batteries_pickuped',
        ),
        *[
            pytest.param(
                ['pickuped', 'pickuped'],
                {'code': 400, 'json': {'code': code, 'booking_id': 'book_0'}},
                {'code': 400, 'json': {'code': '400', 'message': message}},
                id=code,
            )
            for (code, message) in [
                ('booking_without_accumulator', 'Какая-то ужасная ошибка'),
                ('wrong_booking', 'Какая-то ужасная ошибка'),
                ('cell_is_open', 'Одна из ячеек открыта. Закройте её'),
                ('accumulator_was_not_taken', 'Вы не забрали аккум. Заберите'),
                (
                    'non_processed_booking',
                    'Надо бы все таки забрать все аккумы',
                ),
            ]
        ],
    ],
)
async def test_cargo_ui_exchange_confirm_recharge_errors(
        taxi_scooters_ops,
        pgsql,
        cargo_orders,
        mockserver,
        accumulator_statuses,
        scooters_accumulator_response,
        expected_response,
):
    accumulators = []
    for i, status in enumerate(accumulator_statuses):
        accumulators.append(
            {
                'booking_id': f'accumulator_book_id_{i}',
                'cell_id': f'cell_{i}',
                'cabinet_id': 'cab_1',
                'cabinet_type': 'charge_station',
                'accumulator_id': f'accumulator_{i}',
                'ui_status': status,
            },
        )

    db_utils.add_mission(
        pgsql,
        _create_mission(
            first_point_first_job_status='performing',
            first_point_first_job_type='pickup_batteries',
            first_point_first_job_extra={'accumulators': accumulators},
            first_point_second_job_status='planned',
            first_point_second_job_type='return_batteries',
            first_point_second_job_extra={'quantity': 2},
        ),
    )

    @mockserver.json_handler(
        '/scooter-accumulator/scooter-accumulator/'
        'v2/cabinet/accumulator/validate-booked-taken',
    )
    async def _validate_booked_taken(request):
        assert sorted(request.json['booking_ids']) == [
            f'accumulator_book_id_{i}'
            for (i, _) in enumerate(accumulator_statuses)
        ]
        assert len(request.json['rebooking_ids']) == 2

        return mockserver.make_response(
            status=scooters_accumulator_response['code'],
            json=scooters_accumulator_response['json'],
        )

    resp = await taxi_scooters_ops.post(
        HANDLER, headers=common.DAP_HEADERS, json=REQUEST_BODY,
    )

    assert resp.status == expected_response['code']
    assert resp.json() == expected_response['json']

    assert _validate_booked_taken.times_called == (
        1 if scooters_accumulator_response else 0
    )
