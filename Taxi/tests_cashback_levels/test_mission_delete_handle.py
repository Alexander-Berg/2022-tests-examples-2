# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import common_pb2
import mission_pb2
import pytest


def get_notifications_from_db(cursor):
    cursor.execute(
        f"""
        SELECT yandex_uid, task_description_id, stage_id, version
        FROM cashback_levels.missions_notifications;
        """,
    )
    return [*cursor]


def get_progress_from_db(cursor):
    cursor.execute(
        f"""
        SELECT yandex_uid, task_description_id, stage_id, version, completions
        FROM cashback_levels.missions_completed;
        """,
    )
    return [*cursor]


@pytest.mark.config(
    CASHBACK_LEVELS_MISSION_CONTROL_ENDPOINTS=['localhost:1083'],
)
@pytest.mark.pgsql('cashback_levels', files=['test_mission_delete_handle.sql'])
@pytest.mark.experiments3(filename='config3_cashback_tasks_description.json')
@pytest.mark.parametrize(
    (
        'request_data',
        'yandex_uid',
        'delete_mission_called',
        'expected_requests',
        'expected_responses',
        'expected_notifications_db',
        'expected_progress_db',
    ),
    [
        pytest.param(
            {'mission_ids': ['task_id_1', 'task_id_2']},
            '123',
            2,
            [
                dict(
                    puid=123,
                    customer=mission_pb2.Customer.CUSTOMER_LEVELS,
                    external_id='task_id_1',
                ),
                dict(
                    puid=123,
                    customer=mission_pb2.Customer.CUSTOMER_LEVELS,
                    external_id='task_id_2',
                ),
            ],
            [
                dict(
                    status=common_pb2.ResponseStatus.RESPONSE_STATUS_SUCCESS,
                    deleted_amount=1,
                ),
                dict(
                    status=common_pb2.ResponseStatus.RESPONSE_STATUS_SUCCESS,
                    deleted_amount=1,
                ),
            ],
            [('123', 'task_id_3', 'stage1', 0)],
            [('123', 'task_id_3', 'stage1', 0, 3)],
            id='delete_2_missions',
        ),
    ],
)
async def test_mission_delete_handle(
        pgsql,
        request_data,
        yandex_uid,
        delete_mission_called,
        expected_requests,
        expected_responses,
        mock_mc_user_mission_service,
        expected_notifications_db,
        expected_progress_db,
        taxi_cashback_levels,
):
    cursor = pgsql['cashback_levels'].cursor()

    async with mock_mc_user_mission_service(
            expected_requests, expected_responses,
    ) as service:
        result = await taxi_cashback_levels.post(
            '/4.0/cashback-levels/v1/missions/delete',
            json=request_data,
            headers={'X-Yandex-UID': yandex_uid},
        )
        assert result.status == 200
        assert service.servicer.delete_mission_called == delete_mission_called

        if expected_notifications_db:
            actual_notifications_db = get_notifications_from_db(cursor)
            assert not (
                set(expected_notifications_db) ^ set(actual_notifications_db)
            )

        if expected_progress_db:
            actual_progress_db = get_progress_from_db(cursor)
            assert not set(expected_progress_db) ^ set(actual_progress_db)
