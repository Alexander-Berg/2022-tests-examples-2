import pytest


def invalidate_existing(cursor, data, is_not_exist=False):
    count = 0 if is_not_exist else 1
    session_id = data['session_id']
    cursor.execute(
        'SELECT session_id FROM state.sessions '
        'WHERE session_id = {}'.format(session_id),
    )
    assert len(cursor.fetchall()) == count

    checks_ids = data['checks_ids']
    for name in checks_ids:
        if checks_ids[name]:
            cursor.execute(
                'SELECT condition_id FROM checks.{0} '
                'WHERE check_id = {1}'.format(name, checks_ids[name]),
            )
            assert len(cursor.fetchall()) == count

    conditions = data['conditions']
    for condition_id in conditions:
        cursor.execute(
            'SELECT condition_id FROM checks.conditions '
            'WHERE condition_id = {}'.format(condition_id),
        )
        # as of now those are deleted separately by pgcleaner
        assert len(cursor.fetchall()) == 1

    configs = data['configs']
    for config_id in configs:
        cursor.execute(
            'SELECT config_id FROM checks.config '
            'WHERE config_id = {}'.format(config_id),
        )
        # as of now those are deleted separately by pgcleaner
        assert len(cursor.fetchall()) == 1


def create_dict(cursor, session_id):
    cursor.execute(
        'SELECT duration_id, arrival_id, immobility_id, surge_arrival_id, '
        'out_of_area_id, route_id, transporting_arrival_id '
        'FROM state.sessions '
        'WHERE session_id = {}'.format(session_id),
    )
    rows = cursor.fetchall()
    assert len(rows) == 1
    session = rows[0]
    checks_ids = {
        'duration': session[0],
        'arrival': session[1],
        'immobility': session[2],
        'surge_arrival': session[3],
        'out_of_area': session[4],
        'route': session[5],
        'transporting_arrival': session[6],
    }
    conditions = []
    configs = []
    for name in checks_ids:
        if checks_ids[name]:
            cursor.execute(
                'SELECT condition_id, config_id FROM checks.{0} '
                'WHERE check_id = {1}'.format(name, checks_ids[name]),
            )
            rows = cursor.fetchall()
            assert len(rows) == 1
            rule = rows[0]
            condition_id = rule[0]
            config_id = rule[1]
            if condition_id:
                conditions.append(condition_id)
            if config_id:
                configs.append(config_id)

    result = {
        'session_id': session_id,
        'conditions': conditions,
        'configs': configs,
        'checks_ids': checks_ids,
    }
    return result


@pytest.mark.parametrize('session_id', [1, 22, 32])
@pytest.mark.pgsql(
    'reposition_watcher',
    files=[
        'check_configs.sql',
        'conditions.sql',
        'check_rules.sql',
        'sessions.sql',
    ],
)
async def test_v1_service_session_removed(
        taxi_reposition_watcher, pgsql, session_id,
):
    request = {'session_id': session_id}
    cursor = pgsql['reposition_watcher'].cursor()
    data = create_dict(cursor, session_id)
    invalidate_existing(cursor, data, False)
    response = await taxi_reposition_watcher.post(
        'v1/service/session/remove', json=request,
    )
    assert response.status_code == 200
    invalidate_existing(cursor, data, True)


@pytest.mark.pgsql(
    'reposition_watcher',
    files=[
        'check_configs.sql',
        'conditions.sql',
        'check_rules.sql',
        'sessions.sql',
    ],
)
async def test_v1_service_session_remove_not_existing(
        taxi_reposition_watcher, pgsql,
):
    request = {'session_id': 98989}
    response = await taxi_reposition_watcher.post(
        'v1/service/session/remove', json=request,
    )
    assert response.status_code == 200
