import pytest


def get_update_in_access_control(enabled: bool):
    return pytest.mark.experiments3(
        name='eats_partners_update_in_access_control',
        consumers=['eats_partners/internal_ac'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always true',
                'predicate': {'type': 'true'},
                'value': {'enabled': enabled},
            },
        ],
        is_config=True,
    )


@pytest.mark.pgsql('eats_partners', files=['insert_partner_data.sql'])
async def request_update_partner(
        taxi_eats_partners,
        partner_id=1,
        email='partner1@partner.com',
        roles=None,
):
    headers = {'Content-type': 'application/json'}
    extra = {'headers': headers}

    json_body = {
        'email': email,
        'name': 'test_name',
        'places': [343, 454],
        'is_fast_food': False,
        'timezone': 'America/New_York',
        'country_code': 'KZ',
        'password': 'password',
    }

    if roles is not None:
        json_body['roles'] = roles

    return await taxi_eats_partners.patch(
        '/internal/partners/v1/update?partner_id={}'.format(partner_id),
        **extra,
        json=json_body,
    )


@pytest.mark.config(
    EATS_PARTNERS_SENDING_MAILS_SETTINGS={
        'enables_sending_events': ['update-password'],
    },
)
@pytest.mark.pgsql('eats_partners', files=['insert_partner_data.sql'])
@pytest.mark.parametrize(
    'input_body,expected_unset,expected_set_creds,communications_request',
    [
        ({'name': 'test_name'}, False, False, 0),
        ({'name': 'Партнер2'}, False, False, 0),
        ({'is_fast_food': False}, True, False, 0),
        ({'is_fast_food': True}, False, False, 0),
        ({'password': 'some_password'}, True, True, 1),
        ({'email': 'partner2@partner.com'}, False, False, 0),
        ({'email': 'partner3@partner.com'}, True, True, 0),
        ({'timezone': 'America/New_York'}, False, False, 0),
    ],
)
async def test_unset_session(
        taxi_eats_partners,
        mock_vendor_users_update,
        mockserver,
        input_body,
        expected_unset,
        expected_set_creds,
        communications_request,
        mock_personal_retrieve,
        mock_personal_store,
):
    @mockserver.json_handler(
        '/eats-restapp-communications/internal/communications/v1/send-event',
    )
    def _mock_communications_sender(req):
        return mockserver.make_response(status=204)

    @mockserver.json_handler(
        '/eats-restapp-authorizer/internal/partner/set_credentials',
    )
    def _set_creds(request):
        return mockserver.make_response(status=204)

    @mockserver.json_handler(
        '/eats-restapp-authorizer/v1/session/unset-by-partner',
    )
    def _mock_unset_by_partner(request):
        return mockserver.make_response(status=200)

    @mockserver.json_handler('/eats-restapp-authorizer/place-access/reset')
    def _mock_place_access_reset_by_partner(request):
        return mockserver.make_response(status=200)

    headers = {'Content-type': 'application/json'}
    extra = {'headers': headers}
    response = await taxi_eats_partners.patch(
        '/internal/partners/v1/update?partner_id=1', **extra, json=input_body,
    )
    assert response.status_code == 200

    assert _mock_unset_by_partner.has_calls == expected_unset
    assert _set_creds.has_calls == expected_set_creds
    assert _mock_place_access_reset_by_partner.times_called == 1
    assert _mock_communications_sender.times_called == communications_request


@pytest.mark.config(
    EATS_PARTNERS_SENDING_MAILS_SETTINGS={
        'enables_sending_events': ['update-password'],
    },
)
@pytest.mark.pgsql('eats_partners', files=['insert_partner_data.sql'])
@pytest.mark.parametrize(
    'partner_email',
    [pytest.param('test@test.com'), pytest.param('TEST@TEST.COM')],
)
async def test_partners_update(
        taxi_eats_partners,
        mock_vendor_users_update,
        mock_personal_retrieve,
        pgsql,
        mockserver,
        partner_email,
):
    @mockserver.json_handler(
        '/eats-restapp-communications/internal/communications/v1/send-event',
    )
    def _mock_communications_sender(req):
        return mockserver.make_response(status=204)

    @mockserver.json_handler('/personal/v1/emails/store')
    def _email_store(request):
        return {
            'id': request.json['value'] + '_id',
            'value': request.json['value'],
        }

    @mockserver.json_handler(
        '/eats-restapp-authorizer/internal/partner/set_credentials',
    )
    def _set_creds(request):
        return mockserver.make_response(status=204)

    @mockserver.json_handler(
        '/eats-restapp-authorizer/v1/session/unset-by-partner',
    )
    def _mock_unset_by_partner(request):
        return mockserver.make_response(status=200)

    @mockserver.json_handler('/eats-restapp-authorizer/place-access/reset')
    def _mock_place_access_reset_by_partner(request):
        return mockserver.make_response(status=200)

    response = await request_update_partner(
        taxi_eats_partners, email=partner_email, roles=[2],
    )

    assert response.status_code == 200
    payload = response.json()['payload']
    assert payload['country_code'] == 'KZ'
    assert not payload['is_fast_food']
    assert payload['timezone'] == 'America/New_York'
    assert set(payload['places']) == {343, 454}
    assert payload['roles'] == [
        {'id': 2, 'slug': 'ROLE_OPERATOR', 'title': 'operator'},
    ]
    assert payload['email'] == partner_email
    assert payload['personal_email_id'] == (partner_email + '_id')

    cursor = pgsql['eats_partners'].cursor()
    cursor.execute(
        """
        SELECT personal_email_id, timezone, country_code, is_fast_food
        FROM eats_partners.partners
        WHERE partner_id = 1
        """,
    )
    assert list(cursor) == [
        (partner_email + '_id', 'America/New_York', 'KZ', False),
    ]

    cursor.execute(
        """
        SELECT partner_id, place_id,
            (deleted_at IS NOT NULL) as deleted
        FROM eats_partners.partner_places
        WHERE partner_id = 1
        """,
    )
    assert set(cursor) == {
        (1, 123, True),
        (1, 234, True),
        (1, 343, False),
        (1, 454, False),
    }

    cursor.execute(
        """
        SELECT partner_id, role_id,
            (deleted_at IS NOT NULL) as deleted
        FROM eats_partners.partner_roles
        WHERE partner_id = 1
        """,
    )
    assert set(cursor) == {(1, 1, True), (1, 2, False)}

    assert _mock_communications_sender.times_called == 1


@pytest.mark.config(
    EATS_PARTNERS_SENDING_MAILS_SETTINGS={
        'enables_sending_events': ['update-password'],
    },
)
@pytest.mark.pgsql('eats_partners', files=['insert_partner_data.sql'])
async def test_partners_update_vendor_error(
        taxi_eats_partners,
        mock_vendor_users_update_error,
        taxi_eats_partners_monitor,
        mockserver,
        mock_personal_retrieve,
        mock_personal_store,
):
    @mockserver.json_handler(
        '/eats-restapp-communications/internal/communications/v1/send-event',
    )
    def _mock_communications_sender(req):
        return mockserver.make_response(status=204)

    @mockserver.json_handler(
        '/eats-restapp-authorizer/internal/partner/set_credentials',
    )
    def _set_creds(request):
        return mockserver.make_response(status=204)

    response = await request_update_partner(taxi_eats_partners, roles=[2])

    assert response.status_code == 400
    assert response.json() == {'code': '420', 'message': 'some vendor error'}

    metrics = await taxi_eats_partners_monitor.get_metrics()
    assert metrics['global-sync-statistics']['update_error.vendor'] == 0

    assert _mock_communications_sender.times_called == 0


@pytest.mark.config(
    EATS_PARTNERS_SENDING_MAILS_SETTINGS={
        'enables_sending_events': ['update-password'],
    },
)
@pytest.mark.pgsql('eats_partners', files=['insert_partner_data.sql'])
async def test_nonexisting_partners_update(
        taxi_eats_partners, mockserver, pgsql, mock_personal_retrieve,
):
    @mockserver.json_handler(
        '/eats-restapp-communications/internal/communications/v1/send-event',
    )
    def _mock_communications_sender(req):
        return mockserver.make_response(status=204)

    @mockserver.json_handler(
        '/eats-restapp-authorizer/internal/partner/search',
    )
    def _mock_search_partner(request):
        partners = []
        if request.json['logins'][0] == 'partner2@partner.com':
            partners.append(
                {'login': request.json['logins'][0], 'partner_id': 1},
            )
        if request.json['logins'][0] == 'existing@partner.com':
            partners.append(
                {'login': request.json['logins'][0], 'partner_id': 2},
            )
        if request.json['logins'][0] == 'aaa@aaa.ru':
            partners.append(
                {'login': request.json['logins'][0], 'partner_id': 42},
            )
        return mockserver.make_response(
            status=200, json={'partners': partners},
        )

    @mockserver.json_handler('/personal/v1/emails/store')
    def _email_store(request):
        return {
            'id': request.json['value'] + '_id',
            'value': request.json['value'],
        }

    @mockserver.json_handler(
        '/eats-restapp-authorizer/internal/partner/set_credentials',
    )
    def _set_creds(request):
        return mockserver.make_response(status=204)

    @mockserver.json_handler('/eats-vendor/api/v1/server/users/42')
    def _mock_vendor_users_update(req):
        return mockserver.make_response(
            status=200,
            json={
                'isSuccess': True,
                'payload': {
                    'id': 42,
                    'name': 'Name',
                    'email': 'aaa@aaa.ru',
                    'restaurants': [123],
                    'isFastFood': False,
                    'timezone': 'Europe/Moscow',
                    'roles': [
                        {'id': 1, 'role': 'ROLE_MANAGER', 'title': 'manager'},
                    ],
                },
            },
        )

    response = await request_update_partner(
        taxi_eats_partners, partner_id=42, roles=[2],
    )

    assert response.status_code == 200
    payload = response.json()['payload']
    assert payload['id'] == 42
    assert payload['email'] == 'aaa@aaa.ru'
    assert payload['personal_email_id'] == 'aaa@aaa.ru_id'
    assert payload['name'] == ''
    assert not payload['is_fast_food']
    assert payload['timezone'] == 'Europe/Moscow'
    assert set(payload['places']) == {123}
    assert payload['roles'] == [
        {'id': 1, 'slug': 'ROLE_MANAGER', 'title': 'manager'},
    ]

    cursor = pgsql['eats_partners'].cursor()
    cursor.execute(
        """
        SELECT personal_email_id, name, timezone, country_code, is_fast_food
        FROM eats_partners.partners
        WHERE partner_id = 42
        """,
    )
    assert list(cursor) == [
        ('aaa@aaa.ru_id', None, 'Europe/Moscow', '', False),
    ]

    cursor.execute(
        """
        SELECT partner_id, place_id
        FROM eats_partners.partner_places
        WHERE partner_id = 42
        """,
    )
    assert set(cursor) == {(42, 123)}

    cursor.execute(
        """
        SELECT partner_id, role_id
        FROM eats_partners.partner_roles
        WHERE partner_id = 42
        """,
    )
    assert set(cursor) == {(42, 1)}

    assert _mock_communications_sender.times_called == 1


@pytest.mark.config(
    EATS_PARTNERS_SENDING_MAILS_SETTINGS={
        'enables_sending_events': ['update-password'],
    },
)
@pytest.mark.pgsql('eats_partners', files=['insert_partner_data.sql'])
@pytest.mark.parametrize(
    'partner_email',
    [
        pytest.param('existing@partner.com'),
        pytest.param('EXISTING@PARTNER.COM'),
        pytest.param('ExIsTiNg@pArTnEr.cOm'),
    ],
)
async def test_partners_update_to_existing_email(
        taxi_eats_partners,
        mock_vendor_users_update_error,
        pgsql,
        partner_email,
        mock_personal_store,
        mock_personal_retrieve,
        mockserver,
):
    @mockserver.json_handler(
        '/eats-restapp-communications/internal/communications/v1/send-event',
    )
    def _mock_communications_sender(req):
        return mockserver.make_response(status=204)

    response = await request_update_partner(
        taxi_eats_partners, email=partner_email, roles=[2],
    )

    assert response.status_code == 400

    assert _mock_communications_sender.times_called == 0


@pytest.mark.config(
    EATS_PARTNERS_SENDING_MAILS_SETTINGS={
        'enables_sending_events': ['update-password'],
    },
)
@pytest.mark.pgsql('eats_partners', files=['insert_partner_data.sql'])
@pytest.mark.parametrize(
    'partner_email, roles, added_to_system, groups_retrieved, groups_detached',
    [
        pytest.param(
            'test@test.com',
            [2],
            False,
            False,
            False,
            marks=get_update_in_access_control(False),
            id='update disabled by config',
        ),
        pytest.param(
            'test@test.com',
            None,
            False,
            False,
            False,
            marks=get_update_in_access_control(True),
            id='update enabled, request without roles',
        ),
        pytest.param(
            'test@test.com',
            [1, 2],
            True,
            True,
            True,
            marks=get_update_in_access_control(True),
            id='update enabled, request with roles',
        ),
        pytest.param(
            'test@test.com',
            [2],
            True,
            True,
            True,
            marks=get_update_in_access_control(True),
            id='update enabled, request with role operator',
        ),
        pytest.param(
            'test@test.com',
            [1],
            True,
            True,
            True,
            marks=get_update_in_access_control(True),
            id='update enabled, request with role manager',
        ),
    ],
)
async def test_update_in_access_control(
        taxi_eats_partners,
        mock_vendor_users_update,
        mock_personal_retrieve,
        mockserver,
        partner_email,
        roles,
        added_to_system,
        groups_retrieved,
        groups_detached,
):
    @mockserver.json_handler(
        '/eats-restapp-communications/internal/communications/v1/send-event',
    )
    def _mock_communications_sender(req):
        return mockserver.make_response(status=204)

    @mockserver.json_handler('/personal/v1/emails/store')
    def _email_store(request):
        return {
            'id': request.json['value'] + '_id',
            'value': request.json['value'],
        }

    @mockserver.json_handler(
        '/eats-restapp-authorizer/internal/partner/set_credentials',
    )
    def _set_creds(request):
        return mockserver.make_response(status=204)

    @mockserver.json_handler('/access-control/v1/admin/groups/users/retrieve/')
    def _mock_access_control_groups_retrieve(req):
        return {
            'users': [
                {
                    'provider': 'restapp',
                    'provider_user_id': '1',
                    'groups': [
                        {
                            'id': 1,
                            'name': 'test_name',
                            'slug': 'test_group_slug',
                            'system': 'restapp',
                        },
                    ],
                },
            ],
        }

    @mockserver.json_handler(
        '/access-control/v1/admin/groups/users/bulk-detach/',
    )
    def _mock_access_control_bulk_detach(req):
        return {
            'detached_users': [
                {
                    'user': {'provider': 'restapp', 'provider_user_id': '1'},
                    'group_slug': 'test_group_slug',
                },
            ],
        }

    @mockserver.json_handler(
        '/access-control/v1/admin/users/bulk-add-to-system/',
    )
    def _mock_access_control_user_add_to_system(req):
        return {
            'invalid_users': [],
            'non_existing_users': [],
            'non_existing_groups': [],
        }

    @mockserver.json_handler(
        '/eats-restapp-authorizer/v1/session/unset-by-partner',
    )
    def _mock_unset_by_partner(request):
        return mockserver.make_response(status=200)

    @mockserver.json_handler('/eats-restapp-authorizer/place-access/reset')
    def _mock_place_access_reset_by_partner(request):
        return mockserver.make_response(status=200)

    response = await request_update_partner(
        taxi_eats_partners, email=partner_email, roles=roles,
    )

    assert response.status_code == 200

    assert _mock_access_control_user_add_to_system.has_calls == added_to_system
    assert _mock_access_control_groups_retrieve.has_calls == groups_retrieved
    assert _mock_access_control_bulk_detach.has_calls == groups_detached
    assert _mock_place_access_reset_by_partner.times_called == 1
    assert _mock_communications_sender.times_called == 1

    if added_to_system:
        manager_roles = [
            'places_common',
            'communications_common',
            'menu_common',
            'orders_common',
            'orders_history',
            'orders_cancel',
            'orders_changes',
            'support_write',
        ]
        operator_roles = [
            'places_common',
            'communications_common',
            'menu_common',
            'orders_common',
            'orders_history',
            'orders_cancel',
            'orders_changes',
            'support_common',
            'places_pickup_enable',
            'places_plus_common',
        ]

        if roles == [1]:
            expected_roles = manager_roles
        elif roles == [2]:
            expected_roles = operator_roles
        else:
            expected_roles = set(manager_roles + operator_roles)

        add_to_system_args = (
            _mock_access_control_user_add_to_system.next_call()
        )

        assert (
            add_to_system_args['req'].json['users'][0]['provider'] == 'restapp'
        )
        assert (
            add_to_system_args['req'].json['users'][0]['provider_user_id']
            == '1'
        )
        assert add_to_system_args['req'].json['groups'] == sorted(
            expected_roles,
        )

    if groups_retrieved:
        retrieve_args = _mock_access_control_groups_retrieve.next_call()
        assert retrieve_args['req'].query['system'] == 'restapp'
        assert retrieve_args['req'].json['filters']['provider'] == 'restapp'
        assert retrieve_args['req'].json['filters']['provider_user_ids'] == [
            '1',
        ]
        assert retrieve_args['req'].json['limit'] == 1

    if groups_detached:
        detach_args = _mock_access_control_bulk_detach.next_call()
        assert detach_args['req'].json == {
            'users': [
                {
                    'user': {'provider': 'restapp', 'provider_user_id': '1'},
                    'group_slug': 'test_group_slug',
                },
            ],
        }
