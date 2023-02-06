import pytest


@pytest.mark.pgsql(
    'callcenter_auth', files=['callcenter_auth_existing_operators.sql'],
)
@pytest.mark.config(
    CALLCENTER_OPERATORS_ACCESS_CONTROL_ROLES_MAP={
        'cargo_operator': {
            'group': 'cargo_operators',
            'local_name': '[Карго] Оператор',
            'project': 'cargo',
            'tags': ['operator', 'cc-reg'],
        },
        'cargo_qa_specialist': {
            'group': 'cargo_qa_specialists',
            'local_name': '[Карго] Специалист по контролю качества',
            'project': 'cargo',
        },
        'ru_disp_slavyansk_operator': {
            'group': 'slavyansk_operators',
            'local_name': '[Славянск] Оператор диспетчерской',
            'project': 'disp_slavyansk',
            'tags': ['operator', 'cc-reg'],
        },
        'operator': {
            'group': 'slavyansk_team_leaders',
            'local_name': '[Славянск] Руководитель группы',
            'project': 'disp_slavyansk',
        },
        'supervisor': {
            'group': 'team_leaders',
            'local_name': 'Руководитель группы',
            'project': 'disp',
        },
        'admin': {
            'group': 'ya_eats_support_operators',
            'local_name': 'Оператор саппорта Яндекс.Еды',
            'project': '',
            'tags': ['operator', 'cc-reg'],
        },
    },
)
async def test_get_all_roles_of_users_for_idm(taxi_callcenter_operators_web):
    resp = await taxi_callcenter_operators_web.get(
        '/v1/idm/get-all-roles', json={},
    )
    assert resp.status == 200
    resp_body = await resp.json()

    assert resp_body == {
        'code': 0,
        'users': [
            {
                'login': 'admin',
                'roles': [{'callcenter_stuff': 'common', 'role': 'admin'}],
            },
            {
                'login': 'supervisor',
                'roles': [{'callcenter_stuff': 'disp', 'role': 'supervisor'}],
            },
        ],
    }
