import pytest

from test_clownductor.cron.test_sync_duty_admins import asserters
from test_clownductor.cron.test_sync_duty_admins import consts


# test process services in next order
# test_project:test-service:stable
# test_project:test-service:testing
# test_project_2:test-service-2
# test_project_2:test-service-5
# make sure your mocks follow this order
@pytest.mark.config(
    CLOWNDUCTOR_ABC_API_V4_USAGE={
        'service_by_id': 1,
        'add_member': 1,
        'get_members': 1,
        'service': 1,
    },
    CLOWNDUCTOR_SYNC_DUTY_ADMINS={
        'enabled': True,
        'dry_run': False,
        'duty_request_limit': 5,
        'abc_request_limit': 5,
        'clowny_balancers_request_limit': 5,
        'denylist': [
            {
                'project_name': 'test_project_2',
                'service_name': 'test-service-4',
            },
        ],
        'allowlist': [
            {
                'project_name': 'test_project_2',
                'service_name': 'test-service-5',
            },
        ],
        'no_duty_in_stable_owners': [
            {'project_name': 'test_project', 'service_name': 'test-service'},
        ],
        'mdb_ignore_logins': ['project_login_22'],
    },
)
@pytest.mark.parametrize(
    (
        'nanny_additional_logins',
        'nanny_logins_to_remove',
        'nanny_adding_groups',
        'awacs_additional_logins',
        'awacs_logins_to_remove',
        'delete_from_abc_enabled',
        'with_project_owners',
        'with_developers_in_nanny',
        'with_evicters_in_nanny',
    ),
    [
        pytest.param(
            [[], [], [], []],
            [],
            [['1', '50889']] * 4,
            [[], ['some_admin'], [], []],
            None,
            False,
            True,
            False,
            False,
            id='defaults',
        ),
        pytest.param(
            [[], ['d1mbas-super', 'd1mbas-service_1'], [], []],
            None,
            [['1', '50889']] * 4,
            [
                [],  # no awacs additions cause of no_duty_in_stable_owners
                ['d1mbas-service_1', 'd1mbas-super', 'some_admin'],
                [],
                [],
            ],
            None,
            False,
            True,
            True,
            True,
            marks=[
                pytest.mark.config(
                    CLOWNDUCTOR_SYNC_DUTY_SETTINGS={
                        '__default__': {
                            '__default__': {
                                'remove_old_admins': False,
                                'add_admins_from_idm_for_project': False,
                                'add_admins_from_idm_for_service': False,
                                'give_nanny_developer': True,
                                'give_nanny_evicter': True,
                            },
                        },
                        'test_project': {
                            '__default__': {
                                'remove_old_admins': False,
                                'add_admins_from_idm_for_project': False,
                                'add_admins_from_idm_for_service': False,
                            },
                            'test-service': {
                                'remove_old_admins': False,
                                'add_admins_from_idm_for_project': True,
                                'add_admins_from_idm_for_service': True,
                            },
                        },
                    },
                ),
            ],
            id='enable idm roles for test-service only',
        ),
        pytest.param(
            [[], ['d1mbas-super', 'd1mbas-service_1'], [], []],
            None,
            [['1']] * 4,
            [
                [],  # no awacs additions cause of no_duty_in_stable_owners
                ['d1mbas-service_1', 'd1mbas-super', 'some_admin'],
                [],
                [],
            ],
            None,
            False,
            False,
            True,
            True,
            marks=[
                pytest.mark.config(
                    CLOWNDUCTOR_SYNC_DUTY_SETTINGS={
                        '__default__': {
                            '__default__': {
                                'remove_old_admins': False,
                                'use_project_owners': False,
                                'give_nanny_developer': True,
                                'give_nanny_evicter': True,
                                'add_admins_from_idm_for_project': False,
                                'add_admins_from_idm_for_service': False,
                            },
                        },
                        'test_project': {
                            '__default__': {
                                'remove_old_admins': False,
                                'add_admins_from_idm_for_project': False,
                                'add_admins_from_idm_for_service': False,
                            },
                            'test-service': {
                                'remove_old_admins': False,
                                'add_admins_from_idm_for_project': True,
                                'add_admins_from_idm_for_service': True,
                            },
                        },
                    },
                ),
            ],
            id=(
                'enable idm roles for test-service only '
                '(project owners disabled)'
            ),
        ),
        pytest.param(
            [[], [], [], []],
            ['test-nanny-1', 'test-nanny-2'],
            [['1', '50889'], ['1', '50889'], ['50889'], ['1', '50889']],
            [[], ['some_admin'], [], ['d1mbas-super']],
            [
                [],
                [],
                ['namespace-login-1', 'namespace-login-2'],
                ['namespace-login-1', 'namespace-login-2'],
            ],
            True,
            True,
            True,
            True,
            marks=[
                pytest.mark.config(
                    CLOWNDUCTOR_SYNC_DUTY_SETTINGS={
                        '__default__': {
                            '__default__': {
                                'remove_old_admins': False,
                                'add_admins_from_idm_for_project': False,
                                'add_admins_from_idm_for_service': False,
                                'give_nanny_developer': True,
                                'give_nanny_evicter': True,
                            },
                        },
                        'test_project_2': {
                            '__default__': {
                                'remove_old_admins': False,
                                'add_admins_from_idm_for_project': False,
                                'add_admins_from_idm_for_service': False,
                            },
                            'test-service-2': {
                                'remove_old_admins': True,
                                'add_admins_from_idm_for_project': True,
                                'add_admins_from_idm_for_service': True,
                            },
                        },
                    },
                ),
            ],
            id='enable idm roles and removing extras for test-service-2 only',
        ),
        pytest.param(
            [[], [], [], []],
            ['test-nanny-1', 'test-nanny-2'],
            [['1'], ['1'], [], ['1']],
            [[], ['some_admin'], [], ['d1mbas-super']],
            [
                [],
                [],
                ['namespace-login-1', 'namespace-login-2'],
                ['namespace-login-1', 'namespace-login-2'],
            ],
            True,
            False,
            True,
            True,
            marks=[
                pytest.mark.config(
                    CLOWNDUCTOR_SYNC_DUTY_SETTINGS={
                        '__default__': {
                            '__default__': {
                                'remove_old_admins': False,
                                'use_project_owners': False,
                                'give_nanny_developer': True,
                                'give_nanny_evicter': True,
                                'add_admins_from_idm_for_project': False,
                                'add_admins_from_idm_for_service': False,
                            },
                        },
                        'test_project_2': {
                            '__default__': {
                                'remove_old_admins': False,
                                'add_admins_from_idm_for_project': False,
                                'add_admins_from_idm_for_service': False,
                            },
                            'test-service-2': {
                                'remove_old_admins': True,
                                'add_admins_from_idm_for_project': True,
                                'add_admins_from_idm_for_service': True,
                            },
                        },
                    },
                ),
            ],
            id=(
                'enable idm roles and removing extras for test-service-2 only '
                '(project owners disabled)'
            ),
        ),
    ],
)
@pytest.mark.features_off('enable_root_for_maintainers')
@pytest.mark.features_on(
    'sync_duty_admins_mdb_types', 'enable_sync_mdb_admins',
)
@pytest.mark.parametrize(
    ('duty_service_die',),
    [
        pytest.param(True, id='duty_service_die'),
        pytest.param(False, id='duty_service_works'),
    ],
)
@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
async def test_sync_duty_admins(
        cron_runner,
        mockserver,
        nanny_additional_logins,
        nanny_logins_to_remove,
        nanny_adding_groups,
        awacs_additional_logins,
        awacs_logins_to_remove,
        delete_from_abc_enabled,
        with_project_owners,
        with_developers_in_nanny,
        with_evicters_in_nanny,
        staff_mockserver,
        duty_service_die,
        balancers_get_handler,
        get_namespace_handler,
):
    staff_mockserver()

    @mockserver.json_handler('/duty-api/api/duty_group')
    def duty_group_handler(request):
        if duty_service_die:
            return mockserver.make_response(status=500)

        group_name = 'badbadbad'
        users = []
        current_event = None
        if request.query['group_id'] == '1b69be79c5755f678048a169':
            users = [
                {'user': 'abc_member_1'},
                {'user': 'abc_member_2'},
                {'user': 'abc_member_3'},
                {'user': 'abc_member_1'},
                {'user': 'some_admin'},
            ]
            current_event = {'user': 'some_admin'}
            group_name = 'svc_taxidutyadmins_administration'
        return {
            'result': {
                'data': {
                    'currentEvent': current_event,
                    'suggestedEvents': users,
                    'staffGroups': [group_name],
                },
                'ok': True,
            },
        }

    @mockserver.json_handler('/client-abc/v4/services/members/')
    def abc_members_handler(request):
        if request.method == 'GET':
            return {
                'next': None,
                'previous': None,
                'results': [
                    {'person': {'login': 'abc_member_1'}, 'id': 1},
                    {'person': {'login': 'abc_member_2'}, 'id': 2},
                    {'person': {'login': 'abc_member_3'}, 'id': 3},
                    {'person': {'login': 'abc_member_1'}, 'id': 4},
                    {'person': {'login': 'some_admin'}, 'id': 5},
                ],
            }
        return {}

    deleted_member_ships = set()

    @mockserver.json_handler(
        r'/client-abc/v3/services/members/(?P<member_id>\d+)/', regex=True,
    )
    def abc_delete_member_handler(request, member_id):
        assert request.method == 'DELETE'
        deleted_member_ships.add(int(member_id))
        return {}

    abc_delete_member_handler.deleted_member_ships = deleted_member_ships

    @mockserver.json_handler(
        '/client-nanny/v2/services/test-service-1-direct/auth_attrs/',
    )
    def get_nanny_attrs_ts1(request):
        if request.method == 'GET':
            return asserters.nanny_attrs_get()
        return {}

    @mockserver.json_handler(
        '/client-nanny/v2/services/test-service-1-direct-testing/auth_attrs/',
    )
    def get_nanny_attrs_ts1_test(request):
        if request.method == 'GET':
            return asserters.nanny_attrs_get()
        return {}

    @mockserver.json_handler(
        '/client-nanny/v2/services/test-service-2-direct/auth_attrs/',
    )
    def get_nanny_attrs_ts2(request):
        if request.method == 'GET':
            return asserters.nanny_attrs_get()
        return {}

    @mockserver.json_handler(
        '/client-nanny/v2/services/test-service-5-direct/auth_attrs/',
    )
    def get_nanny_attrs_ts5(request):
        if request.method == 'GET':
            return asserters.nanny_attrs_get()
        return {}

    @mockserver.json_handler('/client-abc/v4/services/')
    def abc_service_handler(request):
        assert request.method == 'GET'
        assert request.query['is_exportable__in'] == 'true,false'
        assert request.query['slug'] in consts.ABC_SLUGS
        assert request.query['fields'] == 'id'
        return {'results': [{'id': 1337}]}

    @mockserver.json_handler('/client-awacs/api/UpdateNamespace/')
    def update_namespace_handler(request):
        assert request.method == 'POST'
        return {}

    await cron_runner.sync_duty_admins()

    asserters.assert_abc_delete_members(
        abc_delete_member_handler, delete_from_abc_enabled, duty_service_die,
    )
    if duty_service_die:
        assert abc_service_handler.times_called == 0
        return
    asserters.assert_duty_group(duty_group_handler)
    assert abc_service_handler.times_called == 5
    asserters.assert_abc_members(abc_members_handler, with_project_owners)
    asserters.assert_get_namespace(get_namespace_handler)

    service_1_stable_ns_supers = [
        'namespace-login-1',
        'namespace-login-2',
        'robot-taxi-clown',
    ]
    service_1_tst_ns_supers = [
        'abc_member_1',
        'abc_member_2',
        'abc_member_3',
        'karachevda',
        'meow',
    ] + service_1_stable_ns_supers[:]
    service_2_stable_ns_supers = [
        'namespace-login-1',
        'namespace-login-2',
        'robot-taxi-clown',
    ]
    if with_project_owners:
        service_1_stable_ns_supers.insert(-1, 'project_login_11')
        service_1_tst_ns_supers.insert(-1, 'project_login_11')
        service_2_stable_ns_supers.insert(-1, 'project_login_21')
        service_2_stable_ns_supers.insert(-1, 'project_login_22')
    fqdn_map = {
        'test-service-1.taxi.yandex.net': service_1_stable_ns_supers[:],
        'test-service-1.taxi.tst.yandex.net': service_1_tst_ns_supers[:],
        'test-service-2.taxi.yandex.net': service_2_stable_ns_supers[:],
    }
    assert update_namespace_handler.times_called == 3
    asserters.assert_update_namespace(
        update_namespace_handler,
        fqdn_map,
        awacs_additional_logins,
        awacs_logins_to_remove,
    )
    asserters.assert_balancers(balancers_get_handler)
    service_1_logins_stable = (
        ['project_login_11'] if with_project_owners else []
    )
    service_1_logins_testing = [
        'abc_member_1',
        'abc_member_2',
        'abc_member_3',
        'karachevda',
        'meow',
        'some_admin',
    ]
    if with_project_owners:
        service_1_logins_testing.insert(-1, 'project_login_11')
    asserters.assert_nanny_attrs(
        get_nanny_attrs_ts1,
        service_1_logins_stable + nanny_additional_logins[0],
        expected_groups=nanny_adding_groups[0],
        developers=(
            {'groups': [], 'logins': ['some-developer']}
            if with_developers_in_nanny
            else None
        ),
        evicters=(
            {'groups': [], 'logins': ['some-evicter']}
            if with_evicters_in_nanny
            else None
        ),
    )
    asserters.assert_nanny_attrs(
        get_nanny_attrs_ts1_test,
        service_1_logins_testing + nanny_additional_logins[1],
        expected_groups=nanny_adding_groups[1],
        developers=(
            {'groups': [], 'logins': ['some-developer']}
            if with_developers_in_nanny
            else None
        ),
        evicters=(
            {'groups': [], 'logins': ['some-evicter']}
            if with_evicters_in_nanny
            else None
        ),
    )
    asserters.assert_nanny_attrs(
        get_nanny_attrs_ts2,
        (
            (
                ['project_login_21', 'project_login_22']
                if with_project_owners
                else []
            )
            + nanny_additional_logins[2]
        ),
        nanny_logins_to_remove,
        expected_groups=nanny_adding_groups[2],
    )
    asserters.assert_nanny_attrs(
        get_nanny_attrs_ts5,
        (
            ['project_login_21', 'project_login_22']
            if with_project_owners
            else []
        )
        + nanny_additional_logins[3],
        expected_groups=nanny_adding_groups[3],
    )
