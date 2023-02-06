import datetime

import pytest

from taxi.util import dates

from callcenter_operators import exceptions
from callcenter_operators import models
from callcenter_operators.storage.postgresql import db
from test_callcenter_operators import test_utils


async def extract_last_visit(internal_id, conn):
    query = (
        'SELECT last_visited_at from callcenter_auth.current_info'
        ' WHERE id = $1;'
    )
    return await conn.fetchval(query, internal_id)


@pytest.mark.parametrize(
    'requested_operator',
    [
        pytest.param(
            {
                'yandex_uid': 'uid1',
                'yandex_login': 'login1',
                'callcenter_id': 'cc1',
                'first_name': 'name1',
                'last_name': 'surname',
                'supervisor_login': 'some_admin',
                'roles_to_add': ['operator', 'supervisor'],
                'phone_number': '+111',
                'working_domain': 'unit.test',
                'staff_login': 'login1_staff',
                'timezone': 'Europe/Moscow',
            },
            id='empty_db',
        ),
        pytest.param(
            {
                'yandex_uid': 'uid2',
                'yandex_login': 'login2',
                'callcenter_id': 'cc2',
                'first_name': 'name2',
                'last_name': 'surname',
                'middle_name': 'middlename',
                'supervisor_login': 'some_admin',
                'roles_to_add': ['operator', 'supervisor'],
                'phone_number': '+222',
                'working_domain': 'unit.test',
                'staff_login': 'login2_staff',
                'timezone': 'Europe/Moscow',
            },
            id='recreation of operator',
            marks=pytest.mark.pgsql(
                'callcenter_auth',
                files=['callcenter_auth_existing_operators.sql'],
            ),
        ),
    ],
)
async def test_grant_access(web_context, requested_operator):
    req_op = requested_operator
    pool = db.OperatorsRepo.get_pool(web_context)
    async with pool.acquire() as conn:
        await db.OperatorsRepo.grant_access(
            web_context,
            conn,
            **req_op,
            password='password1111',
            now=dates.utc_with_tz(),
        )
    req_op['roles'] = req_op.pop('roles_to_add')
    res_op_raw = await test_utils.get_operator(
        req_op['yandex_uid'], web_context,
    )
    for key, req_value in req_op.items():
        assert res_op_raw[key] == req_value

    res_op = models.Operator.from_db(res_op_raw)
    assert res_op.state == 'enlisting'


@pytest.mark.parametrize(
    ['requested_uids', 'expected_answer'],
    [
        pytest.param(['uid1', 'uid2'], [False, False], id='empty_db'),
        pytest.param(
            ['uid1', 'uid2'],
            [True, False],
            id='not empty db, one is deleted',
            marks=pytest.mark.pgsql(
                'callcenter_auth',
                files=['callcenter_auth_existing_operators.sql'],
            ),
        ),
    ],
)
async def test_is_active(web_context, requested_uids, expected_answer):

    ro_pool = db.OperatorsRepo.get_ro_pool(web_context)
    for uid, answer in zip(requested_uids, expected_answer):
        async with ro_pool.acquire() as conn:
            is_active = await db.OperatorsRepo.check_operator(
                uid, web_context, conn,
            )
        assert is_active == answer


@pytest.mark.pgsql(
    'callcenter_auth', files=['callcenter_auth_existing_operators.sql'],
)
async def test_get_salted_password(web_context):
    ro_pool = db.OperatorsRepo.get_ro_pool(web_context)
    async with ro_pool.acquire() as conn:
        password = await db.OperatorsRepo.get_operator_password(
            'login1@unit.test', web_context, conn,
        )
    assert password == 'rgNIgYs0QpgbUs7DFCBMdI/oY5c+0EKB8Nvxm6uMw4Y='


@pytest.mark.pgsql(
    'callcenter_auth', files=['callcenter_auth_existing_operators.sql'],
)
async def test_get_operators_by_yandex_uids(web_context):
    ro_pool = db.OperatorsRepo.get_ro_pool(web_context)
    async with ro_pool.acquire() as conn:
        ops = await db.OperatorsRepo.get_operators(
            web_context,
            conn,
            uids=['uid1', 'uid2'],
            with_not_ready=True,
            project_metaqueues=['disp', 'help'],
        )
    operators = [models.Operator.from_db(op) for op in ops]
    operators_logins = {op.yandex_login for op in operators}
    assert operators_logins == {'login1', 'login2'}


@pytest.mark.pgsql(
    'callcenter_auth', files=['callcenter_auth_existing_operators.sql'],
)
async def get_control_models(web_context):
    ro_pool = db.OperatorsRepo.get_ro_pool(web_context)
    async with ro_pool.acquire() as conn:
        ops = await db.OperatorsRepo.get_control_models(
            web_context, conn, uids=['uid1', 'uid2'],
        )
    operators = [models.OperatorControlModel.from_db(op) for op in ops]
    operators_logins = {op.yandex_login for op in operators}
    assert operators_logins == {'login1'}

    async with ro_pool.acquire() as conn:
        ops = await db.OperatorsRepo.get_control_models(
            web_context, conn, internal_ids=[3, 4],
        )
    operators = [models.OperatorControlModel.from_db(op) for op in ops]
    operators_logins = {op.yandex_login for op in operators}
    assert operators_logins == {'login1'}

    async with ro_pool.acquire() as conn:
        ops = await db.OperatorsRepo.get_control_models(
            web_context, conn, logins=['login1', 'login2'],
        )
    operators = [models.OperatorControlModel.from_db(op) for op in ops]
    operators_logins = {op.yandex_login for op in operators}
    assert operators_logins == {'login1'}


@pytest.mark.pgsql(
    'callcenter_auth', files=['callcenter_auth_existing_operators.sql'],
)
async def test_get_operators_by_ext_logins(web_context):
    ro_pool = db.OperatorsRepo.get_ro_pool(web_context)
    async with ro_pool.acquire() as conn:
        ops = await db.OperatorsRepo.get_operators(
            web_context, conn, logins=['login1@unit.test', 'login2@unit.test'],
        )
    operators = [models.Operator.from_db(op) for op in ops]
    operators_logins = {op.yandex_login for op in operators}
    assert operators_logins == {'login1'}


@pytest.mark.pgsql(
    'callcenter_auth',
    files=['callcenter_auth_test_collision_while_increment.sql'],
)
async def test_collision(web_context):
    pool = db.OperatorsRepo.get_pool(web_context)
    with pytest.raises(exceptions.DBError):
        async with pool.acquire() as conn:
            await db.OperatorsRepo.grant_access(
                web_context,
                conn,
                yandex_uid='123456',
                yandex_login='test_login',
                callcenter_id='cc1',
                first_name='name',
                last_name='test',
                password='password1111',
                supervisor_login='supervisor_login',
                roles_to_add=['operator'],
                phone_number='+79999999999',
                working_domain='unit.test',
                now=dates.utc_with_tz(),
            )
    async with pool.acquire() as conn:
        await db.OperatorsRepo.grant_access(
            web_context,
            conn,
            yandex_uid='123456',
            yandex_login='test_login',
            callcenter_id='cc1',
            first_name='name',
            last_name='test',
            password='password1111',
            supervisor_login='supervisor_login',
            roles_to_add=['operator'],
            phone_number='+79999999999',
            working_domain='unit.test',
            now=dates.utc_with_tz(),
        )
    db_op = models.Operator.from_db(
        await test_utils.get_operator('123456', web_context),
    )
    assert db_op.agent_id == '1000000001'


@pytest.mark.pgsql(
    'callcenter_auth', files=['callcenter_auth_existing_operators.sql'],
)
async def test_set_as_ready(web_context):
    pool = db.OperatorsRepo.get_pool(web_context)
    async with pool.acquire() as conn:
        await db.OperatorsRepo.set_operator_as_ready(
            4, dates.utc_with_tz(), web_context, conn,
        )
    db_op = models.Operator.from_db(
        await test_utils.get_operator('uid2', web_context),
    )
    assert db_op.state == 'ready'


@pytest.mark.pgsql(
    'callcenter_auth', files=['callcenter_auth_existing_operators.sql'],
)
async def test_set_as_deleted(web_context):
    pool = db.OperatorsRepo.get_pool(web_context)
    async with pool.acquire() as conn:
        await db.OperatorsRepo.set_operator_as_deleted(
            3, dates.utc_with_tz(), web_context, conn,
        )
    db_op = models.Operator.from_db(
        await test_utils.get_operator('uid1', web_context),
    )
    assert db_op.state == 'deleted'


@pytest.mark.parametrize(
    ['op_filter', 'expected_logins'],
    [
        pytest.param({}, {'login1', 'login2', 'admin', 'supervisor'}, id=''),
        pytest.param(
            {'callcenters': ['cc1']},
            {'login1', 'admin', 'supervisor'},
            id='callcenters',
        ),
        pytest.param(
            {'supervisors': ['supervisor@unit.test']},
            {'login2'},
            id='supervisors',
        ),
        pytest.param(
            {'states': ['ready']},
            {'login1', 'login2', 'admin', 'supervisor'},
            id='states',
        ),
        pytest.param({'states': ['deleted']}, set(), id='states deleted'),
        pytest.param(
            {'roles': ['supervisor']}, {'login2', 'supervisor'}, id='roles',
        ),
        pytest.param({'metaqueues': ['corp']}, {'login1'}, id='metaqueues'),
        pytest.param(
            {'logins_agent_ids': ['1000000000'], 'name_formats': []},
            {'login1'},
            id='agent_ids',
        ),
        pytest.param(
            {'logins_agent_ids': ['login1'], 'name_formats': []},
            {'login1'},
            id='logins',
        ),
        pytest.param(
            {'logins_agent_ids': ['login1_staff'], 'name_formats': []},
            {'login1'},
            id='staff logins',
        ),
        pytest.param(
            {'logins_agent_ids': ['login1@unit.test'], 'name_formats': []},
            {'login1'},
            id='external logins',
        ),
        pytest.param(
            {'logins_agent_ids': ['login1%'], 'name_formats': []},
            set(),
            id='bad login',
        ),
        pytest.param(
            {'logins_agent_ids': [], 'name_formats': ['%name1%']},
            {'login1'},
            id='name formats',
        ),
        pytest.param(
            {'logins_agent_ids': ['name1'], 'name_formats': ['%name1%']},
            {'login1'},
            id='name formats with bad logins_agent_ids',
        ),
        pytest.param(
            {'logins_agent_ids': ['login1'], 'name_formats': ['%login1%']},
            {'login1'},
            id='logins with bad name formats',
        ),
        pytest.param(
            {'project_metaqueues': ['help']},
            {'login1', 'login2', 'supervisor', 'admin'},
            id='project metaqueues',
        ),
        pytest.param(
            {'project_metaqueues': ['disp', 'corp']},
            {'login1', 'supervisor', 'admin'},
            id='project metaqueues with one bad metaqueue',
        ),
        pytest.param(
            {
                'callcenters': ['cc2'],
                'supervisors': ['supervisor@unit.test'],
                'states': ['ready'],
                'roles': ['supervisor'],
                'queues': ['help_on_1'],
                'logins_agent_ids': [
                    'login2',
                    '1000000001',
                    'login2@unit.test',
                ],
                'name_formats': [
                    '%name2%',
                    'surname%',
                    '%name name2%',
                    'surname name2%',
                ],
                'project_metaqueues': ['help'],
            },
            {'login2'},
            id='max filters',
        ),
        pytest.param(
            {
                'callcenters': ['cc1', 'cc2'],
                'supervisors': ['admin@unit.test', 'supervisor@unit.test'],
                'states': ['ready', 'deleted'],
                'roles': ['supervisor', 'operator'],
                'queues': ['corp_on_1', 'disp_on_1', 'help_on_1'],
                'logins_agent_ids': ['login1', '1000000001'],
                'name_formats': ['surname%'],
                'project_metaqueues': ['help', 'disp'],
            },
            {'login1', 'login2'},
            id='mixed filters',
        ),
    ],
)
@pytest.mark.pgsql(
    'callcenter_auth', files=['callcenter_auth_test_filter.sql'],
)
async def test_get_ready_operators_by_filter(
        web_context, op_filter, expected_logins,
):
    ro_pool = db.OperatorsRepo.get_ro_pool(web_context)
    async with ro_pool.acquire() as conn:
        ops = await db.OperatorsRepo.get_operators_by_filter(
            op_filter, web_context, conn,
        )
    operators = [models.Operator.from_db(op) for op in ops]
    operators_logins = {op.yandex_login for op in operators}

    assert operators_logins == expected_logins


@pytest.mark.pgsql(
    'callcenter_auth', files=['callcenter_auth_existing_operators.sql'],
)
async def test_revoke_access(web_context):
    pool = db.OperatorsRepo.get_pool(web_context)
    async with pool.acquire() as conn:
        await db.OperatorsRepo.revoke_access(
            3, dates.utc_with_tz(), web_context, conn,
        )
    db_op = models.Operator.from_db(
        await test_utils.get_operator('uid1', web_context),
    )
    assert db_op.state == 'deleting'
    assert db_op.roles == ['operator']


@pytest.mark.parametrize(
    ['op_filter', 'expected_logins'],
    [
        pytest.param(
            {}, {'login1', 'login2', 'login3', 'admin', 'supervisor'}, id='',
        ),
        pytest.param(
            {'callcenters': ['cc1']},
            {'login1', 'admin', 'supervisor'},
            id='callcenters',
        ),
        pytest.param(
            {'supervisors': ['supervisor@unit.test']},
            {'login2', 'login3'},
            id='supervisors',
        ),
        pytest.param(
            {'states': ['ready']},
            {'login1', 'login2', 'admin', 'supervisor'},
            id='states',
        ),
        pytest.param(
            {'states': ['deleting']}, {'login3'}, id='states deleted',
        ),
        pytest.param(
            {
                'callcenters': ['cc2'],
                'supervisors': ['supervisor@unit.test'],
                'states': ['ready'],
            },
            {'login2'},
            id='all filters',
        ),
        pytest.param(
            {'roles': ['supervisor']}, {'login2', 'supervisor'}, id='roles',
        ),
        pytest.param({'metaqueues': ['corp']}, {'login1'}, id='metaqueues'),
        pytest.param(
            {'logins_agent_ids': ['1000000000'], 'name_formats': []},
            {'login1'},
            id='agent_ids',
        ),
        pytest.param(
            {'logins_agent_ids': ['login1'], 'name_formats': []},
            {'login1'},
            id='logins',
        ),
        pytest.param(
            {'logins_agent_ids': ['login1_staff'], 'name_formats': []},
            {'login1'},
            id='staff logins',
        ),
        pytest.param(
            {'logins_agent_ids': ['login1@unit.test'], 'name_formats': []},
            {'login1'},
            id='external logins',
        ),
        pytest.param(
            {'logins_agent_ids': ['login1%'], 'name_formats': []},
            set(),
            id='bad login',
        ),
        pytest.param(
            {'logins_agent_ids': [], 'name_formats': ['%name1%']},
            {'login1'},
            id='name formats',
        ),
        pytest.param(
            {'logins_agent_ids': ['name1'], 'name_formats': ['%name1%']},
            {'login1'},
            id='name formats with bad logins_agent_ids',
        ),
        pytest.param(
            {'logins_agent_ids': ['login1'], 'name_formats': ['%login1%']},
            {'login1'},
            id='logins with bad name formats',
        ),
        pytest.param(
            {'project_metaqueues': ['help']},
            {'login1', 'login2', 'login3', 'supervisor', 'admin'},
            id='project metaqueues',
        ),
        pytest.param(
            {'project_metaqueues': ['disp', 'corp']},
            {'login1', 'login3', 'supervisor', 'admin'},
            id='project metaqueues with one bad metaqueue',
        ),
        pytest.param(
            {
                'callcenters': ['cc1'],
                'supervisors': ['supervisor@unit.test'],
                'states': ['ready'],
            },
            set(),
            id='bad filters',
        ),
        pytest.param(
            {
                'callcenters': ['cc1', 'cc2'],
                'supervisors': ['admin@unit.test', 'supervisor@unit.test'],
                'states': ['ready', 'deleting'],
                'roles': ['supervisor', 'operator'],
                'logins_agent_ids': ['login3', '1888888888'],
                'name_formats': ['surname%'],
                'project_metaqueues': ['help', 'disp'],
            },
            {'login1', 'login2', 'login3', 'supervisor'},
            id='mixed',
        ),
    ],
)
@pytest.mark.pgsql(
    'callcenter_auth', files=['callcenter_auth_test_filter.sql'],
)
async def test_get_operators_by_filter(
        web_context, op_filter, expected_logins,
):
    ro_pool = db.OperatorsRepo.get_ro_pool(web_context)
    async with ro_pool.acquire() as conn:
        ops = await db.OperatorsRepo.get_operators_by_filter(
            op_filter, web_context, conn, with_not_ready=True,
        )
    operators = [models.Operator.from_db(op) for op in ops]
    operators_logins = {op.yandex_login for op in operators}
    assert operators_logins == expected_logins


@pytest.mark.pgsql(
    'callcenter_auth', files=['callcenter_auth_test_custom_pause.sql'],
)
async def test_set_operator_control_model(web_context):
    pool = db.OperatorsRepo.get_pool(web_context)
    op_model = models.OperatorControlModel(
        2,
        '1000000000',
        '123',
        'login1',
        'unit.test',
        dates.utc_with_tz(),
        'login1_unit.test',
        ['new_queue'],
        'common',
        'disconnected',
        'new_sub_status',
    )
    async with pool.acquire() as conn:
        await db.OperatorsRepo.set_operator_control_model(
            op_model, web_context, conn,
        )
        new_model = await db.OperatorsRepo.get_control_model(
            web_context, conn, uid='uid1',
        )
    assert new_model
    new_model = models.OperatorControlModel.from_db(new_model)
    assert new_model.status == 'disconnected'
    assert new_model.sub_status == 'new_sub_status'
    assert new_model.metaqueues == ['new_queue']


@pytest.mark.now('2020-04-29 13:50:00')
async def test_save_last_visit(web_context):
    now = dates.utc_with_tz()
    pool = db.OperatorsRepo.get_pool(web_context)
    async with pool.acquire() as conn:
        await db.OperatorsRepo.save_last_visit(now, 1, web_context, conn)
        result = await extract_last_visit(1, conn)
        assert result == now

        # try to save one more time
        now = now + datetime.timedelta(minutes=10)
        await db.OperatorsRepo.save_last_visit(now, 1, web_context, conn)
        result = await extract_last_visit(1, conn)
        assert result == now


@pytest.mark.pgsql(
    'callcenter_auth', files=['callcenter_auth_existing_operators.sql'],
)
async def test_rewrite_agent_id(web_context):
    internal_id = 3
    new_agent_id = '123'
    pool = db.OperatorsRepo.get_pool(web_context)
    async with pool.acquire() as conn:
        await db.OperatorsRepo.rewrite_agent_id(
            internal_id, new_agent_id, web_context, conn,
        )
        res_op = models.Operator.from_db(
            await test_utils.get_operator('uid1', web_context),
        )
        assert res_op.agent_id == new_agent_id


@pytest.mark.pgsql(
    'callcenter_auth', files=['callcenter_auth_existing_operators.sql'],
)
async def test_reset_mentors(web_context):
    pool = db.OperatorsRepo.get_pool(web_context)
    async with pool.acquire() as conn:
        res_op = models.Operator.from_db(
            await test_utils.get_operator('admin_uid', web_context),
        )
        assert res_op.mentor_login is not None

        await db.OperatorsRepo.reset_mentors(web_context, conn, [1])
        res_op = models.Operator.from_db(
            await test_utils.get_operator('admin_uid', web_context),
        )
        assert res_op.mentor_login is None


@pytest.mark.parametrize(
    ('are_expired', 'expected_ids'),
    (
        pytest.param(
            True, list(), marks=[pytest.mark.now('2016-06-09 13:50:00')],
        ),
        pytest.param(
            False,
            [1, 2, 3, 4, 5],
            marks=[pytest.mark.now('2016-06-12 13:50:00')],
        ),
    ),
)
@pytest.mark.pgsql(
    'callcenter_auth', files=['callcenter_auth_existing_operators.sql'],
)
async def test_extract_with_idle_mentors(
        web_context, are_expired, expected_ids,
):
    pool = db.OperatorsRepo.get_pool(web_context)
    async with pool.acquire() as conn:
        result = await db.OperatorsRepo.extract_with_idle_mentors(
            web_context, conn, 10,
        )
        assert result == expected_ids
