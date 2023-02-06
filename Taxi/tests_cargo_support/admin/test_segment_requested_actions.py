from tests_cargo_support import utils_pg


def translate_action(action_type, locale='ru'):
    return locale + ' ' + action_type


def find_action(json, action_type):
    for action in json['actions']:
        if action['action'] == translate_action(action_type):
            return action
    return None


def check_action(
        action,
        claim_point_id,
        action_type,
        reason,
        status,
        *,
        reorder_or_cancel_type=None,
):
    assert action['cargo_order_id'] == '11111111-1111-1111-1111-111111111111'
    assert action['taxi_order_id'] == 'taxi_order_id_1'
    assert action['segment_id'] == 'segment_id_1'
    assert action['point_id'] == claim_point_id
    assert action['claim_id'] == 'claim_id_1'
    assert action['park_id'] == 'park_id_1'
    assert action['driver_id'] == 'driver_id_1'
    assert action['action'] == translate_action(action_type)
    assert action['reason'] == reason
    assert action['admin_login'] == 'admin_login_1'
    assert action['ticket'] == 'ticket_1'
    assert action['text_reason'] == 'text reason'
    assert not action['is_reorder_disabled_by_admin']

    if reorder_or_cancel_type is None:
        assert 'reorder_or_cancel_type' not in action
    else:
        assert action['reorder_or_cancel_type'] == reorder_or_cancel_type

    assert not action['is_cancelled_paid_waiting']
    assert not action['is_cancelled_paid_arriving']
    assert not action['is_fine_required']
    assert action['status'] == status
    assert action['created_at'] == '2020-01-01T10:00:00+00:00'
    assert action['updated_at'] == '2020-01-01T10:00:00+00:00'


async def test_no_actions(taxi_cargo_support):
    response = await taxi_cargo_support.post(
        '/v1/admin/segment/requested-actions',
        params={'waybill_external_ref': 'wb_1'},
    )
    assert response.status_code == 200
    assert response.json()['actions'] == []


async def test_happy_path(pgsql, taxi_cargo_support):
    valid_waybill_ref = 'waybill_ref_1'

    utils_pg.insert_point_action(
        pgsql,
        valid_waybill_ref,
        1,
        'long_wait',
        'long_wait__invalid_status',
        status='success',
    )
    utils_pg.insert_point_action(
        pgsql,
        valid_waybill_ref,
        2,
        'cancel_order',
        'cancel_order__invalid_status',
        status='in_progress',
        reorder_or_cancel_type='reorder',
    )

    utils_pg.insert_point_action(
        pgsql,
        'waybill_ref_2',
        3,
        'long_wait',
        'long_wait__invalid_status',
        status='success',
    )

    response = await taxi_cargo_support.post(
        '/v1/admin/segment/requested-actions',
        params={'waybill_external_ref': valid_waybill_ref},
    )
    assert response.status_code == 200
    json = response.json()
    assert len(json['actions']) == 2
    check_action(
        find_action(json, 'long_wait'),
        1,
        'long_wait',
        'Курьер не прожал статус.',
        status='success',
        reorder_or_cancel_type=None,
    )
    check_action(
        find_action(json, 'cancel_order'),
        2,
        'cancel_order',
        'Курьер не прожал статус.',
        status='in_progress',
        reorder_or_cancel_type='reorder',
    )
