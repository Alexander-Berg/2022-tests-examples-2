import pytest

from test_clownductor.cron.test_sync_duty_admins import asserters
from test_clownductor.cron.test_sync_duty_admins import consts


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
        'duty_request_limit': 1,
        'abc_request_limit': 1,
        'clowny_balancers_request_limit': 1,
        'no_duty_in_stable_owners': [
            {'project_name': 'test_project', 'service_name': 'test-service'},
        ],
    },
)
@pytest.mark.parametrize(
    'nanny_admin_logins, awacs_admin_logins',
    [
        pytest.param(
            consts.STABLE_TEST_ADMINS,
            consts.STABLE_TEST_ADMINS,
            marks=[
                pytest.mark.config(
                    CLOWNDUCTOR_SYNC_DUTY_SETTINGS={
                        '__default__': {
                            '__default__': {
                                'remove_old_admins': False,
                                'add_admins_from_idm_for_project': True,
                                'add_admins_from_idm_for_service': True,
                                'add_admins_from_idm_for_service_test': True,
                            },
                        },
                    },
                ),
            ],
            id='stable on and test on on default level',
        ),
        pytest.param(
            consts.TEST_ADMINS,
            consts.TEST_ADMINS,
            marks=[
                pytest.mark.config(
                    CLOWNDUCTOR_SYNC_DUTY_SETTINGS={
                        '__default__': {
                            '__default__': {
                                'remove_old_admins': False,
                                'add_admins_from_idm_for_project': True,
                                'add_admins_from_idm_for_service': False,
                                'add_admins_from_idm_for_service_test': True,
                            },
                        },
                    },
                ),
            ],
            id='stable off and test on on default level',
        ),
        pytest.param(
            consts.STABLE_ADMINS,
            consts.STABLE_ADMINS,
            marks=[
                pytest.mark.config(
                    CLOWNDUCTOR_SYNC_DUTY_SETTINGS={
                        '__default__': {
                            '__default__': {
                                'remove_old_admins': False,
                                'add_admins_from_idm_for_project': True,
                                'add_admins_from_idm_for_service': True,
                                'add_admins_from_idm_for_service_test': False,
                            },
                        },
                    },
                ),
            ],
            id='stable on and test off on default level',
        ),
        pytest.param(
            consts.STABLE_TEST_ADMINS,
            consts.STABLE_TEST_ADMINS,
            marks=[
                pytest.mark.config(
                    CLOWNDUCTOR_SYNC_DUTY_SETTINGS={
                        '__default__': {
                            '__default__': {
                                'remove_old_admins': False,
                                'add_admins_from_idm_for_project': True,
                                'add_admins_from_idm_for_service': False,
                                'add_admins_from_idm_for_service_test': False,
                            },
                        },
                        'test_project': {
                            '__default__': {
                                'remove_old_admins': False,
                                'add_admins_from_idm_for_project': True,
                                'add_admins_from_idm_for_service': True,
                                'add_admins_from_idm_for_service_test': True,
                            },
                        },
                    },
                ),
            ],
            id='stable on and test on on project level',
        ),
        pytest.param(
            consts.TEST_ADMINS,
            consts.TEST_ADMINS,
            marks=[
                pytest.mark.config(
                    CLOWNDUCTOR_SYNC_DUTY_SETTINGS={
                        '__default__': {
                            '__default__': {
                                'remove_old_admins': False,
                                'add_admins_from_idm_for_project': True,
                                'add_admins_from_idm_for_service': True,
                                'add_admins_from_idm_for_service_test': False,
                            },
                        },
                        'test_project': {
                            '__default__': {
                                'remove_old_admins': False,
                                'add_admins_from_idm_for_project': True,
                                'add_admins_from_idm_for_service': False,
                                'add_admins_from_idm_for_service_test': True,
                            },
                        },
                    },
                ),
            ],
            id='stable off and test on on project level',
        ),
        pytest.param(
            consts.STABLE_ADMINS,
            consts.STABLE_ADMINS,
            marks=[
                pytest.mark.config(
                    CLOWNDUCTOR_SYNC_DUTY_SETTINGS={
                        '__default__': {
                            '__default__': {
                                'remove_old_admins': False,
                                'add_admins_from_idm_for_project': True,
                                'add_admins_from_idm_for_service': False,
                                'add_admins_from_idm_for_service_test': True,
                            },
                        },
                        'test_project': {
                            '__default__': {
                                'remove_old_admins': False,
                                'add_admins_from_idm_for_project': True,
                                'add_admins_from_idm_for_service': True,
                                'add_admins_from_idm_for_service_test': False,
                            },
                        },
                    },
                ),
            ],
            id='stable on and test off on project level',
        ),
        pytest.param(
            consts.STABLE_TEST_ADMINS,
            consts.STABLE_TEST_ADMINS,
            marks=[
                pytest.mark.config(
                    CLOWNDUCTOR_SYNC_DUTY_SETTINGS={
                        '__default__': {
                            '__default__': {
                                'remove_old_admins': False,
                                'add_admins_from_idm_for_project': True,
                                'add_admins_from_idm_for_service': False,
                                'add_admins_from_idm_for_service_test': False,
                            },
                        },
                        'test_project': {
                            '__default__': {
                                'remove_old_admins': False,
                                'add_admins_from_idm_for_project': True,
                                'add_admins_from_idm_for_service': False,
                                'add_admins_from_idm_for_service_test': False,
                            },
                            'test-service': {
                                'remove_old_admins': False,
                                'add_admins_from_idm_for_project': True,
                                'add_admins_from_idm_for_service': True,
                                'add_admins_from_idm_for_service_test': True,
                            },
                        },
                    },
                ),
            ],
            id='stable on and test on on service level',
        ),
        pytest.param(
            consts.TEST_ADMINS,
            consts.TEST_ADMINS,
            marks=[
                pytest.mark.config(
                    CLOWNDUCTOR_SYNC_DUTY_SETTINGS={
                        '__default__': {
                            '__default__': {
                                'remove_old_admins': False,
                                'add_admins_from_idm_for_project': True,
                                'add_admins_from_idm_for_service': False,
                                'add_admins_from_idm_for_service_test': False,
                            },
                        },
                        'test_project': {
                            '__default__': {
                                'remove_old_admins': False,
                                'add_admins_from_idm_for_project': True,
                                'add_admins_from_idm_for_service': True,
                                'add_admins_from_idm_for_service_test': False,
                            },
                            'test-service': {
                                'remove_old_admins': False,
                                'add_admins_from_idm_for_project': True,
                                'add_admins_from_idm_for_service': False,
                                'add_admins_from_idm_for_service_test': True,
                            },
                        },
                    },
                ),
            ],
            id='stable off and test on on service level',
        ),
        pytest.param(
            consts.STABLE_ADMINS,
            consts.STABLE_ADMINS,
            marks=[
                pytest.mark.config(
                    CLOWNDUCTOR_SYNC_DUTY_SETTINGS={
                        '__default__': {
                            '__default__': {
                                'remove_old_admins': False,
                                'add_admins_from_idm_for_project': True,
                                'add_admins_from_idm_for_service': False,
                                'add_admins_from_idm_for_service_test': False,
                            },
                        },
                        'test_project': {
                            '__default__': {
                                'remove_old_admins': False,
                                'add_admins_from_idm_for_project': True,
                                'add_admins_from_idm_for_service': False,
                                'add_admins_from_idm_for_service_test': True,
                            },
                            'test-service': {
                                'remove_old_admins': False,
                                'add_admins_from_idm_for_project': True,
                                'add_admins_from_idm_for_service': True,
                                'add_admins_from_idm_for_service_test': False,
                            },
                        },
                    },
                ),
            ],
            id='stable on and test off on service level',
        ),
    ],
)
@pytest.mark.parametrize('content_logins', [['nanny-login']])
@pytest.mark.features_off('enable_root_for_maintainers')
@pytest.mark.pgsql(
    'clownductor', files=['init_test_sync_duty_admins_branch_root.sql'],
)
async def test_sync_duty_admins_branch_root(
        cron_runner,
        mockserver,
        nanny_admin_logins,
        awacs_admin_logins,
        content_logins,
        staff_mockserver,
        balancers_get_handler,
        get_namespace_handler,
):
    staff_mockserver()

    @mockserver.json_handler('/duty-api/api/duty_group')
    def duty_group_handler(request):  # pylint: disable=unused-variable
        group_name = 'duty_group_name'
        users = []
        current_event = None
        if request.query['group_id'] == '1b69be79c5755f678048a169':
            users = [{'user': 'abc_member_1'}, {'user': 'some_admin'}]
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

    @mockserver.json_handler(
        '/client-nanny/v2/services/test-service-direct/auth_attrs/',
    )
    def get_nanny_attrs_ts1(request):
        if request.method == 'GET':
            return asserters.nanny_attrs_get(content_logins)
        return {}

    @mockserver.json_handler(
        '/client-nanny/v2/services/test-service-direct-testing/auth_attrs/',
    )
    def get_nanny_attrs_ts1_test(request):
        if request.method == 'GET':
            return asserters.nanny_attrs_get(content_logins)
        return {}

    @mockserver.json_handler('/client-awacs/api/UpdateNamespace/')
    def update_namespace_handler(request):
        assert request.method == 'POST'
        return {}

    await cron_runner.sync_duty_admins()

    stable_namespace_supers = [
        'namespace-login-1',
        'namespace-login-2',
        'robot-taxi-clown',
        'special_admin_login',
    ]
    testing_namespace_supers = stable_namespace_supers[:] + [
        'abc_member_1',
        'some_admin',
        'test_maintainer',
        'vokhcuhz',
    ]
    fqdn_map = {
        'test-service-1.taxi.yandex.net': stable_namespace_supers[:],
        'test-service-1.taxi.tst.yandex.net': testing_namespace_supers[:],
    }
    asserters.assert_update_namespace(
        update_namespace_handler, fqdn_map, awacs_admin_logins,
    )

    service_1_logins_stable = ['special_admin_login']
    service_1_logins_testing = [
        'abc_member_1',
        'some_admin',
        'special_admin_login',
        'test_maintainer',
        'vokhcuhz',
    ]
    asserters.assert_nanny_attrs(
        nanny_mock=get_nanny_attrs_ts1,
        added=service_1_logins_stable + nanny_admin_logins[0],
        expected_logins=content_logins[:],
        expected_groups=['1', '50889'],
    )
    asserters.assert_nanny_attrs(
        nanny_mock=get_nanny_attrs_ts1_test,
        added=service_1_logins_testing + nanny_admin_logins[1],
        expected_logins=content_logins[:],
        expected_groups=['1', '50889'],
    )
