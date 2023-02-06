import pytest


async def test_order_cancellation_not_found(
        taxi_cargo_performer_fines, default_cargo_order_id,
):
    response = await taxi_cargo_performer_fines.post(
        '/order/cancel/info',
        params={'cargo_order_id': default_cargo_order_id},
    )
    assert response.status_code == 200
    assert response.json() == {'cancellations': []}


async def test_empty_id(taxi_cargo_performer_fines):
    response = await taxi_cargo_performer_fines.post(
        '/order/cancel/info', json={},
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': 'bad_request',
        'message': 'cargo_order_id or taxi_order_id must be sent',
    }


async def test_cargo_and_taxi_id(
        taxi_cargo_performer_fines,
        default_cargo_order_id,
        default_taxi_order_id,
):
    response = await taxi_cargo_performer_fines.post(
        '/order/cancel/info',
        params={
            'cargo_order_id': default_cargo_order_id,
            'taxi_order_id': default_taxi_order_id,
        },
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': 'bad_request',
        'message': 'cargo_order_id or taxi_order_id must be sent',
    }


@pytest.mark.pgsql('cargo_performer_fines', files=['cancellation.sql'])
@pytest.mark.parametrize('by_taxi_order', [False, True])
async def test_order_cancel_info(
        taxi_cargo_performer_fines,
        default_cargo_order_id,
        default_taxi_order_id,
        default_dbid_uuid,
        by_taxi_order,
):
    park_id = default_dbid_uuid['dbid']
    driver_id = default_dbid_uuid['uuid']
    if by_taxi_order:
        params = {'cargo_order_id': default_cargo_order_id}
    else:
        params = {'taxi_order_id': default_taxi_order_id}
    response = await taxi_cargo_performer_fines.post(
        '/order/cancel/info', params=params,
    )
    assert response.status_code == 200
    assert response.json() == {
        'cancellations': [
            {
                'cancel_id': 1,
                'cargo_order_id': default_cargo_order_id,
                'taxi_order_id': default_taxi_order_id,
                'park_id': park_id,
                'driver_id': driver_id,
                'cargo_cancel_reason': 'reason',
                'created_ts': '2020-02-03T13:33:54.827958+00:00',
                'updated_ts': '2020-02-03T13:34:54.827958+00:00',
                'completed': True,
                'guilty': False,
                'free_cancellations_limit_exceeded': False,
            },
        ],
    }


@pytest.mark.yt(dyn_table_data=['yt_cancels.yaml'])
@pytest.mark.usefixtures('yt_apply')
@pytest.mark.config(CARGO_PERFORMER_FINES_ENABLE_YT=True)
@pytest.mark.parametrize('by_taxi_order', [False, True])
async def test_from_yt(
        taxi_cargo_performer_fines,
        default_cargo_order_id,
        default_taxi_order_id,
        default_dbid_uuid,
        by_taxi_order,
):
    park_id = default_dbid_uuid['dbid']
    driver_id = default_dbid_uuid['uuid']
    if by_taxi_order:
        params = {'cargo_order_id': default_cargo_order_id}
    else:
        params = {'taxi_order_id': default_taxi_order_id}
    params['allow_restore'] = True
    response = await taxi_cargo_performer_fines.post(
        '/order/cancel/info', params=params,
    )
    assert response.status_code == 200
    assert response.json() == {
        'cancellations': [
            {
                'cancel_id': 1,
                'cargo_cancel_reason': 'reason',
                'cargo_order_id': default_cargo_order_id,
                'created_ts': '2022-05-27T09:27:41+00:00',
                'driver_id': driver_id,
                'free_cancellations_limit_exceeded': False,
                'completed': True,
                'guilty': True,
                'park_id': park_id,
                'taxi_order_id': 'taxi',
                'updated_ts': '2022-05-27T09:27:41+00:00',
            },
        ],
    }
