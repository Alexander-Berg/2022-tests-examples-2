import pytest

from callcenter_operators import models

DISCONNECT_URL = '/cc/v1/callcenter-operators/v1/disconnect_bulk'


def _get_status(pgsql, idx):
    cursor = pgsql['callcenter_auth'].cursor()
    cursor.execute(
        f' SELECT status'
        f' FROM callcenter_auth.current_info'
        f' WHERE id = {idx};',
    )
    status = cursor.fetchone()
    if status:
        return status[0]
    return None


@pytest.mark.parametrize(
    ['request_data', 'response_data', 'expected_status'],
    (
        pytest.param(
            {'yandex_uids': ['uid1', 'uid2']}, {}, 200, id='ok_request',
        ),
        pytest.param(
            {
                'yandex_uids': ['uid1', 'uid2', 'uid3'],
                'project': 'test_project',
            },
            {
                'items': [
                    {
                        'code': 'bad_access',
                        'yandex_login': 'login2@unit.test',
                        'yandex_uid': 'uid2',
                        'metaqueues': ['test_another'],
                    },
                    {'code': 'not_found', 'yandex_uid': 'uid3'},
                ],
            },
            409,
            id='failed_operators',
        ),
        pytest.param(
            {
                'yandex_uids': ['uid' + str(i) for i in range(11)],
                'project': 'test_project',
            },
            {
                'code': 'too_much_operators',
                'message': '11 operators are too many (limit is 10)',
            },
            400,
            id='too_much_operators_request',
        ),
    ),
)
@pytest.mark.pgsql('callcenter_auth', files=['insert_connected_operators.sql'])
@pytest.mark.config(
    CALLCENTER_STATS_PROJECT_INFO_MAP={
        'test_project': {
            'metaqueues': ['test'],
            'should_use_internal_queue_service': True,
            'reg_groups': ['ru'],
        },
    },
)
async def test_operators_disconnect(
        taxi_callcenter_operators_web,
        request_data,
        response_data,
        expected_status,
        mock_save_status,
        mockserver,
        mock_set_status_cc_queues,
        pgsql,
):
    resp = await taxi_callcenter_operators_web.post(
        DISCONNECT_URL, json=request_data,
    )

    if expected_status == 200:
        op_status = _get_status(pgsql, 1)
        assert op_status == models.TelState.DISCONNECTED
        op_status = _get_status(pgsql, 2)
        assert op_status == models.TelState.DISCONNECTED

    if expected_status == 409:
        op_status = _get_status(pgsql, 1)
        assert op_status == models.TelState.DISCONNECTED
        op_status = _get_status(pgsql, 2)
        assert op_status == models.TelState.CONNECTED

    assert resp.status == expected_status
    assert await resp.json() == response_data
