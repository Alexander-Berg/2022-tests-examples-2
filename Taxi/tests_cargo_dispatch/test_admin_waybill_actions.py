import pytest


def get_translated(
        action: str,
        claim_point_id: int,
        *,
        language: str = 'ru',
        visit_order: int = 1,
):
    return f'{language} {action} {visit_order} (#{claim_point_id})'


def get_translated_with_time(
        action: str,
        claim_point_id: int,
        elapsed_minutes: int,
        *,
        language: str = 'ru',
        visit_order: int = 1,
):
    return (
        f'{language} {action} {elapsed_minutes} мин {visit_order} '
        + f'(#{claim_point_id})'
    )


def find_actions(json, action_type):
    found_actions = []
    for action in json['actions']:
        if action['action'] == action_type:
            found_actions.append(action)
    return found_actions


async def test_base(
        happy_path_state_performer_found,
        taxi_cargo_dispatch,
        get_point_execution_by_visit_order,
        waybill_ref='waybill_fb_3',
):
    point = await get_point_execution_by_visit_order(
        waybill_ref=waybill_ref, visit_order=1,
    )
    claim_point_id = point['claim_point_id']

    response = await taxi_cargo_dispatch.post(
        '/v1/admin/waybill/actions',
        params={'waybill_external_ref': waybill_ref},
    )
    assert response.status_code == 200
    assert response.json() == {
        'actions': [
            {
                'action': 'confirm',
                'point_id': claim_point_id,
                'title': get_translated('confirm', claim_point_id),
            },
            {
                'action': 'return',
                'point_id': claim_point_id,
                'title': get_translated('return', claim_point_id),
            },
            {
                'action': 'init',
                'point_id': claim_point_id,
                'title': get_translated('init', claim_point_id),
            },
            {
                'action': 'autoreorder',
                'point_id': 0,
                'title': 'ru autoreorder',
            },
        ],
    }


async def test_no_performer(
        happy_path_state_orders_created,
        taxi_cargo_dispatch,
        get_point_execution_by_visit_order,
        waybill_ref='waybill_fb_3',
):
    point = await get_point_execution_by_visit_order(
        waybill_ref=waybill_ref, visit_order=1,
    )
    claim_point_id = point['claim_point_id']

    response = await taxi_cargo_dispatch.post(
        '/v1/admin/waybill/actions',
        params={'waybill_external_ref': waybill_ref},
    )
    assert response.status_code == 200
    assert response.json() == {
        'actions': [
            {
                'action': 'confirm',
                'point_id': claim_point_id,
                'title': get_translated('confirm', claim_point_id),
            },
            {
                'action': 'return',
                'point_id': claim_point_id,
                'title': get_translated('return', claim_point_id),
            },
            {
                'action': 'init',
                'point_id': claim_point_id,
                'title': get_translated('init', claim_point_id),
            },
            {
                'action': 'autoreorder',
                'point_id': 0,
                'title': 'ru autoreorder',
            },
        ],
    }


async def test_batch_with_skipped_segment(
        happy_path_state_performer_found,
        taxi_cargo_dispatch,
        dispatch_return_point,
        get_point_execution_by_visit_order,
        waybill_ref='waybill_smart_1',
):
    """
    Waybill 'waybill_smart_1':
        seg1_A1_p1 (11) -> seg1_A2_p2 (12) -> seg2_A1_p1 (21) ->
        seg1_B1_p3 (13) -> seg1_B2_p4 (14) -> seg1_B3_p5 (15) ->
        seg2_B1_p2 (22) -> seg1_A2_p6 (12) -> seg1_A1_p7 (11) ->
        seg2_C1_p3 (23)

    """
    # Skip segment
    response = await dispatch_return_point(waybill_ref, visit_order=1)
    assert response.status_code == 200

    # Check actions
    response = await taxi_cargo_dispatch.post(
        '/v1/admin/waybill/actions',
        params={'waybill_external_ref': waybill_ref},
    )
    assert response.status_code == 200

    point = await get_point_execution_by_visit_order(
        waybill_ref=waybill_ref, visit_order=3,
    )
    claim_point_id = point['claim_point_id']

    assert response.json() == {
        'actions': [
            {
                'action': 'confirm',
                'point_id': 21,
                'title': get_translated(
                    'confirm', claim_point_id, visit_order=3,
                ),
            },
            {
                'action': 'return',
                'point_id': 21,
                'title': get_translated(
                    'return', claim_point_id, visit_order=3,
                ),
            },
            {
                'action': 'init',
                'point_id': 21,
                'title': get_translated('init', claim_point_id, visit_order=3),
            },
            {
                'action': 'autoreorder',
                'point_id': 0,
                'title': 'ru autoreorder',
            },
        ],
    }


@pytest.mark.parametrize('accept_language', ['ru', 'en'])
async def test_translations(
        happy_path_state_performer_found,
        taxi_cargo_dispatch,
        get_point_execution_by_visit_order,
        accept_language: str,
        waybill_ref='waybill_fb_3',
):
    point = await get_point_execution_by_visit_order(
        waybill_ref=waybill_ref, visit_order=1,
    )
    claim_point_id = point['claim_point_id']

    response = await taxi_cargo_dispatch.post(
        '/v1/admin/waybill/actions',
        headers={'Accept-Language': accept_language},
        params={'waybill_external_ref': waybill_ref},
    )
    assert response.status_code == 200

    assert response.json() == {
        'actions': [
            {
                'action': 'confirm',
                'point_id': claim_point_id,
                'title': get_translated(
                    'confirm', claim_point_id, language=accept_language,
                ),
            },
            {
                'action': 'return',
                'point_id': claim_point_id,
                'title': get_translated(
                    'return', claim_point_id, language=accept_language,
                ),
            },
            {
                'action': 'init',
                'point_id': claim_point_id,
                'title': get_translated(
                    'init', claim_point_id, language=accept_language,
                ),
            },
            {
                'action': 'autoreorder',
                'point_id': 0,
                'title': f'{accept_language} autoreorder',
            },
        ],
    }


@pytest.mark.config(CARGO_DISPATCH_ENABLE_FORCED_CONFIRM=True)
async def test_no_return_action_on_return_point(
        happy_path_state_performer_found,
        taxi_cargo_dispatch,
        happy_path_claims_segment_db,
        get_point_execution_by_visit_order,
        waybill_ref='waybill_fb_3',
):
    segment = happy_path_claims_segment_db.get_segment('seg3')
    segment.set_point_visit_status('p1', 'visited')
    segment.set_point_visit_status('p2', 'skipped')

    # Check actions
    response = await taxi_cargo_dispatch.post(
        '/v1/admin/waybill/actions',
        params={'waybill_external_ref': waybill_ref},
    )
    assert response.status_code == 200

    point = await get_point_execution_by_visit_order(
        waybill_ref=waybill_ref, visit_order=3,
    )

    # Test no return action on return point
    action_types = [
        a['action']
        for a in response.json()['actions']
        if a['point_id'] == point['claim_point_id']
    ]
    assert 'return' not in action_types

    assert response.json() == {
        'actions': [
            {
                'action': 'confirm',
                'point_id': 33,
                'title': 'ru confirm 3 (#33)',
            },
            {'action': 'init', 'point_id': 33, 'title': 'ru init 3 (#33)'},
            {
                'action': 'confirm',
                'point_id': 32,
                'title': 'ru forced confirm 2 (#32)',
            },
            {
                'action': 'return',
                'point_id': 32,
                'title': 'ru return_repeat 2 (#32)',
            },
        ],
    }


async def test_no_autoreorder_if_point_visited(
        happy_path_state_performer_found,
        taxi_cargo_dispatch,
        happy_path_claims_segment_db,
        get_point_execution_by_visit_order,
        waybill_ref='waybill_fb_3',
):
    segment = happy_path_claims_segment_db.get_segment('seg3')
    segment.set_point_visit_status('p1', 'visited')

    # Check actions
    response = await taxi_cargo_dispatch.post(
        '/v1/admin/waybill/actions',
        params={'waybill_external_ref': waybill_ref},
    )
    assert response.status_code == 200

    # Test no autoreorder action
    action_types = [a['action'] for a in response.json()['actions']]
    assert 'autoreorder' not in action_types


async def test_paper_flow_no_init(
        happy_path_state_performer_found,
        taxi_cargo_dispatch,
        mock_claims_exchange_confirm,
        get_point_execution_by_visit_order,
        dispatch_confirm_point,
        waybill_ref='waybill_fb_3',
):
    mock_claims_exchange_confirm()
    # Set paper_flow flag
    response = await dispatch_confirm_point(waybill_ref, with_support=True)
    assert response.status_code == 200

    point_a = await get_point_execution_by_visit_order(
        waybill_ref=waybill_ref, visit_order=1,
    )
    claim_point_id_a = point_a['claim_point_id']

    point_b = await get_point_execution_by_visit_order(
        waybill_ref=waybill_ref, visit_order=2,
    )
    claim_point_id_b = point_b['claim_point_id']

    response = await taxi_cargo_dispatch.post(
        '/v1/admin/waybill/actions',
        params={'waybill_external_ref': waybill_ref},
    )
    assert response.status_code == 200
    assert response.json() == {
        'actions': [
            {
                'action': 'confirm',
                'point_id': claim_point_id_b,
                'title': get_translated(
                    'confirm', claim_point_id_b, visit_order=2,
                ),
            },
            {
                'action': 'return',
                'point_id': claim_point_id_b,
                'title': get_translated(
                    'return', claim_point_id_b, visit_order=2,
                ),
            },
            {
                'action': 'confirm',
                'point_id': claim_point_id_a,
                'title': get_translated(
                    'confirm_repeat', claim_point_id_a, visit_order=1,
                ),
            },
        ],
    }


async def test_no_autoreorder_if_no_cargo_order_id(
        happy_path_state_fallback_waybills_proposed,
        taxi_cargo_dispatch,
        waybill_ref='waybill_fb_1',
):

    # Check actions
    response = await taxi_cargo_dispatch.post(
        '/v1/admin/waybill/actions',
        params={'waybill_external_ref': waybill_ref},
    )
    assert response.status_code == 200

    # Test no autoreorder action
    action_types = [a['action'] for a in response.json()['actions']]
    assert 'autoreorder' not in action_types


@pytest.mark.now('2020-06-10T10:15:30+0300')
async def test_monitoring_actions_happy_path(
        happy_path_state_performer_found,
        taxi_cargo_dispatch,
        happy_path_claims_segment_db,
        get_point_execution_by_visit_order,
        set_up_admin_actions_execution_exp,
        set_up_admin_actions_exp,
        waybill_ref='waybill_fb_3',
        elapsed_minutes=15,
):
    await set_up_admin_actions_execution_exp()
    await set_up_admin_actions_exp()

    point = await get_point_execution_by_visit_order(
        waybill_ref=waybill_ref, visit_order=1,
    )
    claim_point_id = point['claim_point_id']

    segment = happy_path_claims_segment_db.get_segment('seg3')
    segment.set_point_visit_status('p1', 'arrived')

    response = await taxi_cargo_dispatch.post(
        '/v1/admin/waybill/actions',
        params={'waybill_external_ref': waybill_ref},
    )
    assert response.status_code == 200
    assert find_actions(response.json(), 'long_wait') == [
        {
            'action': 'long_wait',
            'point_id': claim_point_id,
            'title': get_translated_with_time(
                'long_wait', claim_point_id, elapsed_minutes,
            ),
            'reasons': [
                {
                    'reason': 'long_wait__order_will_be_ready_before_timeout',
                    'title': 'Заказ не готов. Отдадим до 10 минут.',
                },
                {
                    'reason': 'long_wait__invalid_status',
                    'title': 'Курьер не прожал статус.',
                },
            ],
        },
    ]
    assert find_actions(response.json(), 'fake_return') == [
        {
            'action': 'fake_return',
            'point_id': claim_point_id,
            'title': get_translated_with_time(
                'fake_return', claim_point_id, elapsed_minutes,
            ),
            'reasons': [
                {
                    'reason': 'fake_return__invalid_status',
                    'title': 'Курьер не прожал статус.',
                },
                {
                    'reason': 'fake_return__receiver_answered',
                    'title': 'Получатель ответил.',
                },
            ],
        },
    ]
    assert find_actions(response.json(), 'cancel_order') == []


@pytest.mark.parametrize(
    ['visit_status'],
    [
        # Current point: A, courier is not arrived
        pytest.param('pending'),
        # Current point: B
        pytest.param('visited'),
    ],
)
async def test_monitoring_actions_not_used(
        happy_path_state_performer_found,
        taxi_cargo_dispatch,
        happy_path_claims_segment_db,
        get_point_execution_by_visit_order,
        set_up_admin_actions_execution_exp,
        set_up_admin_actions_exp,
        visit_status,
        waybill_ref='waybill_fb_3',
):
    await set_up_admin_actions_execution_exp()
    await set_up_admin_actions_exp()

    segment = happy_path_claims_segment_db.get_segment('seg3')
    segment.set_point_visit_status('p1', visit_status)

    response = await taxi_cargo_dispatch.post(
        '/v1/admin/waybill/actions',
        params={'waybill_external_ref': waybill_ref},
    )
    assert response.status_code == 200
    assert find_actions(response.json(), 'long_wait') == []
    assert find_actions(response.json(), 'fake_return') == []
    assert find_actions(response.json(), 'cancel_order') == []
