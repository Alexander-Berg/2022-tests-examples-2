import pytest

NOW = '2021-09-10T12:00:00+03:00'

HEADER = {'Accept-Language': 'ru'}

PERFORMER_DATA = {
    'performer_id': 2,
    'shift_id': 2,
    'park_id': 'parkid2',
    'driver_id': 'driverid2',
}

PERFORMER_DATA_VALID = {
    'performer_id': str(PERFORMER_DATA['performer_id']),
    'shift_id': str(PERFORMER_DATA['shift_id']),
    'dbid_uuid': '{}_{}'.format(
        PERFORMER_DATA['park_id'], PERFORMER_DATA['driver_id'],
    ),
}

PERFORMER_DATA_INVALID_BY_PERFORMER_ID_TYPE = {
    **PERFORMER_DATA_VALID,
    'performer_id': int(PERFORMER_DATA_VALID['performer_id']),
}

PERFORMER_DATA_INVALID_BY_PERFORMER_ID = {
    **PERFORMER_DATA_VALID,
    'performer_id': 'tseastaffs',
}

PERFORMER_DATA_INVALID_BY_SHIFT_ID_TYPE = {
    **PERFORMER_DATA_VALID,
    'shift_id': int(PERFORMER_DATA_VALID['shift_id']),
}

PERFORMER_DATA_INVALID_BY_SHIFT_ID_CONVERSION_ISSUES = {
    **PERFORMER_DATA_VALID,
    'shift_id': 'strsags',
}

PERFORMER_DATA_INVALID_BY_SHIFT_ID = {
    **PERFORMER_DATA_VALID,
    'shift_id': '1231245',
}


@pytest.mark.now(NOW)
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.pgsql('eda_couriers_schedule', files=['filling_data.sql'])
async def test_couirier_shifts_validate_start_pass_due_no_lessons(
        mockserver, taxi_eats_performer_shifts,
):
    performer_data_without_lessons = {
        **PERFORMER_DATA_VALID,
        'performer_id': '1',
        'shift_id': '1',
    }

    @mockserver.json_handler(
        '/driver-lessons/internal/driver-lessons/v1/lessons-progress/bulk-retrieve',
    )
    def _mock_lessons_progress_bulk_retrieve(request):
        assert (
            performer_data_without_lessons['driver_id']
            == request.json['drivers'][0]['driver_id']
        )
        assert (
            performer_data_without_lessons['park_id']
            == request.json['drivers'][0]['park_id']
        )

        return mockserver.make_response(
            status=200, json={'lessons_progress': []},
        )

    response = await taxi_eats_performer_shifts.post(
        path='/internal/eats-performer-shifts/v1/courier-shifts/validate/start',
        json=performer_data_without_lessons,
        headers=HEADER,
    )

    assert response.status_code == 200
    assert response.json() == {'errors': [], 'is_valid': True}


@pytest.mark.now(NOW)
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.pgsql('eda_couriers_schedule', files=['filling_data.sql'])
async def test_couirier_shifts_validate_start_fail_due_invalid_performer_data_400(
        taxi_eats_performer_shifts,
):
    invalid_bodies = [
        PERFORMER_DATA_INVALID_BY_PERFORMER_ID_TYPE,
        PERFORMER_DATA_INVALID_BY_SHIFT_ID_TYPE,
        PERFORMER_DATA_INVALID_BY_SHIFT_ID_CONVERSION_ISSUES,
    ]

    for invalid_body in invalid_bodies:
        response = await taxi_eats_performer_shifts.post(
            path='/internal/eats-performer-shifts/v1/courier-shifts/validate/start',
            json=invalid_body,
            headers=HEADER,
        )

        assert response.status_code == 400
        response_json = response.json()
        assert response_json['code'] == '400'
        assert (
            isinstance(response_json['message'], str)
            and response_json['message']
        )

    request_bodies_for_no_data = [
        PERFORMER_DATA_INVALID_BY_PERFORMER_ID,
        PERFORMER_DATA_INVALID_BY_SHIFT_ID,
    ]

    for invalid_body in request_bodies_for_no_data:
        response = await taxi_eats_performer_shifts.post(
            path='/internal/eats-performer-shifts/v1/courier-shifts/validate/start',
            json=invalid_body,
            headers=HEADER,
        )
        response_json = response.json()
        if invalid_body == PERFORMER_DATA_INVALID_BY_PERFORMER_ID:
            assert response.status_code == 400
            assert response_json['code'] == '400'
        else:
            print(response_json['message'])
            assert response.status_code == 404
            assert response_json['code'] == '404'
        assert (
            isinstance(response_json['message'], str)
            and response_json['message']
        )


@pytest.mark.now(NOW)
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.pgsql('eda_couriers_schedule', files=['filling_data.sql'])
async def test_couirier_shifts_validate_start_pass_due_lesson_progress_above_threshold(
        mockserver, taxi_eats_performer_shifts,
):
    @mockserver.json_handler(
        '/driver-lessons/internal/driver-lessons/v1/lessons-progress/bulk-retrieve',
    )
    def _mock_lessons_progress_bulk_retrieve(request):
        assert (
            PERFORMER_DATA['driver_id']
            == request.json['drivers'][0]['driver_id']
        )
        assert (
            PERFORMER_DATA['park_id'] == request.json['drivers'][0]['park_id']
        )

        return mockserver.make_response(
            status=200,
            json={
                'lessons_progress': [
                    {
                        'driver_id': request.json['drivers'][0]['driver_id'],
                        'park_id': request.json['drivers'][0]['park_id'],
                        'lesson_id': 'test_0',
                        'progress': 100,
                    },
                    {
                        'driver_id': request.json['drivers'][0]['driver_id'],
                        'park_id': request.json['drivers'][0]['park_id'],
                        'lesson_id': 'test_1',
                        'progress': 100,
                    },
                ],
            },
        )

    response = await taxi_eats_performer_shifts.post(
        path='/internal/eats-performer-shifts/v1/courier-shifts/validate/start',
        json=PERFORMER_DATA_VALID,
        headers=HEADER,
    )

    assert response.status_code == 200
    assert response.json() == {'errors': [], 'is_valid': True}


@pytest.mark.now(NOW)
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.pgsql('eda_couriers_schedule', files=['filling_data.sql'])
async def test_couirier_shifts_validate_start_fail_due_lesson_progress_below_threshold(
        mockserver, taxi_eats_performer_shifts,
):
    lesson_ids = ['test_0', 'test_1']
    progress = 0
    exp_threshold = 50

    @mockserver.json_handler(
        '/driver-lessons/internal/driver-lessons/v1/lessons-progress/bulk-retrieve',
    )
    def _mock_lessons_progress_bulk_retrieve(request):
        assert (
            PERFORMER_DATA['driver_id']
            == request.json['drivers'][0]['driver_id']
        )
        assert (
            PERFORMER_DATA['park_id'] == request.json['drivers'][0]['park_id']
        )

        return mockserver.make_response(
            status=200,
            json={
                'lessons_progress': [
                    {
                        'driver_id': request.json['drivers'][0]['driver_id'],
                        'park_id': request.json['drivers'][0]['park_id'],
                        'lesson_id': lesson_ids[0],
                        'progress': progress,
                    },
                    {
                        'driver_id': request.json['drivers'][0]['driver_id'],
                        'park_id': request.json['drivers'][0]['park_id'],
                        'lesson_id': lesson_ids[1],
                        'progress': progress,
                    },
                ],
            },
        )

    response = await taxi_eats_performer_shifts.post(
        path='/internal/eats-performer-shifts/v1/courier-shifts/validate/start',
        json=PERFORMER_DATA_VALID,
        headers=HEADER,
    )

    assert response.status_code == 200
    assert response.json() == {
        'errors': [
            {
                'type': 'error',
                'code': 'low_lesson_progress',
                'deeplink': 'taximeter://screen/lessons?id=test_1',
                'title': 'Обучение по ПДД не пройдено',
                'button_title': 'Пройти обучение',
            },
            {
                'type': 'error',
                'code': 'low_lesson_progress',
                'deeplink': 'taximeter://screen/lessons?id=test_0',
                'title': 'Обучение test_0 не пройдено',
                'button_title': 'Пройти обучение',
            },
        ],
        'is_valid': False,
    }


@pytest.mark.now(NOW)
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.pgsql('eda_couriers_schedule', files=['filling_data.sql'])
async def test_couirier_shifts_validate_start_fail_due_invalid_request_to_driver_lessons(
        mockserver, taxi_eats_performer_shifts,
):
    @mockserver.json_handler(
        '/driver-lessons/internal/driver-lessons/v1/lessons-progress/bulk-retrieve',
    )
    def _mock_lessons_progress_bulk_retrieve(request):
        assert (
            PERFORMER_DATA['driver_id']
            == request.json['drivers'][0]['driver_id']
        )
        assert (
            PERFORMER_DATA['park_id'] == request.json['drivers'][0]['park_id']
        )

        return mockserver.make_response(
            status=400, json={'code': '400', 'message': 'Bad request'},
        )

    response = await taxi_eats_performer_shifts.post(
        path='/internal/eats-performer-shifts/v1/courier-shifts/validate/start',
        json=PERFORMER_DATA_VALID,
        headers=HEADER,
    )

    assert response.status_code == 500
    assert response.json() == {
        'code': '500',
        'message': 'Internal Server Error',
    }


@pytest.mark.now(NOW)
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.pgsql('eda_couriers_schedule', files=['filling_data.sql'])
async def test_couirier_shifts_validate_start_fail_due_internal_error_in_driver_lessons(
        mockserver, taxi_eats_performer_shifts,
):
    @mockserver.json_handler(
        '/driver-lessons/internal/driver-lessons/v1/lessons-progress/bulk-retrieve',
    )
    def _mock_lessons_progress_bulk_retrieve(request):
        assert (
            PERFORMER_DATA['driver_id']
            == request.json['drivers'][0]['driver_id']
        )
        assert (
            PERFORMER_DATA['park_id'] == request.json['drivers'][0]['park_id']
        )

        return mockserver.make_response(
            status=500,
            json={'code': '500', 'message': 'Internal Server Error'},
        )

    response = await taxi_eats_performer_shifts.post(
        path='/internal/eats-performer-shifts/v1/courier-shifts/validate/start',
        json=PERFORMER_DATA_VALID,
        headers=HEADER,
    )

    assert response.status_code == 500
    assert response.json() == {
        'code': '500',
        'message': 'Internal Server Error',
    }
