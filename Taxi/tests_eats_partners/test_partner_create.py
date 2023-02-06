import pytest

from testsuite.utils import matching


def get_update_in_vendor_experiment(disabled: bool):
    # Возвращает эксперимент eats_partners_update_in_vendor
    return pytest.mark.experiments3(
        name='eats_partners_update_in_vendor',
        consumers=['eats_partners/internal_create'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always true',
                'predicate': {'type': 'true'},
                'value': {'disabled': disabled},
            },
        ],
        is_config=True,
    )


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
async def request_create_partner(taxi_eats_partners, email):
    headers = {'Content-type': 'application/json'}
    extra = {'headers': headers}

    return await taxi_eats_partners.post(
        '/internal/partners/v1/create',
        **extra,
        json={
            'name': 'nananuna',
            'email': email,
            'places': [1, 2, 3],
            'is_fast_food': False,
            'timezone': 'Europe/Moscow',
            'country_code': 'RU',
            'password': 'qwerty',
            'roles': [1, 3],
        },
    )


@pytest.mark.config(
    EATS_PARTNERS_SENDING_MAILS_SETTINGS={
        'enables_sending_events': ['create-user'],
    },
)
@pytest.mark.parametrize(
    'status_code,partner_id,partner_email,expected_count,has_ac_create_call,'
    + 'has_ac_add_system_call,has_ac_update_call,has_pa_reset_call, communications_request',
    [
        pytest.param(
            200,
            42,
            'nana@nuna.nu',
            2,
            False,
            False,
            False,
            False,
            {'email': ['nana@nuna.nu'], 'password': 'qwerty'},
            id='experiment not found',
        ),
        pytest.param(
            200,
            42,
            'NANA@NUNA.NU',
            2,
            False,
            False,
            False,
            False,
            {'email': ['NANA@NUNA.NU'], 'password': 'qwerty'},
            id='experiment not found (uppercase)',
        ),
        pytest.param(
            200,
            42,
            'nana@nuna.nu',
            2,
            False,
            False,
            False,
            False,
            {'email': ['nana@nuna.nu'], 'password': 'qwerty'},
            marks=(
                get_update_in_vendor_experiment(False),
                get_update_in_access_control(False),
            ),
            id='experiment enabled',
        ),
        pytest.param(
            200,
            1,
            'nana@nuna.nu',
            2,
            False,
            False,
            False,
            False,
            {'email': ['nana@nuna.nu'], 'password': 'qwerty'},
            marks=(
                get_update_in_vendor_experiment(True),
                get_update_in_access_control(False),
            ),
            id='experiment disabled',
        ),
        pytest.param(
            200,
            12,
            'test@test.test',
            1,
            False,
            False,
            False,
            True,
            {'email': ['test@test.test'], 'password': 'qwerty'},
            marks=(
                get_update_in_vendor_experiment(False),
                get_update_in_access_control(False),
            ),
            id='partner exists',
        ),
        pytest.param(
            200,
            42,
            'nana@nuna.nu',
            2,
            True,
            True,
            False,
            False,
            {'email': ['nana@nuna.nu'], 'password': 'qwerty'},
            marks=(
                get_update_in_vendor_experiment(False),
                get_update_in_access_control(True),
            ),
            id='experiment enabled and access-control sync enabled',
        ),
        pytest.param(
            200,
            12,
            'test@test.test',
            1,
            False,
            True,
            True,
            True,
            {'email': ['test@test.test'], 'password': 'qwerty'},
            marks=(
                get_update_in_vendor_experiment(False),
                get_update_in_access_control(True),
            ),
            id='partner exists and access-control sync enabled',
        ),
    ],
)
@pytest.mark.pgsql('eats_partners', files=['insert_partner_data.sql'])
async def test_partners_create(
        taxi_eats_partners,
        pgsql,
        status_code,
        partner_id,
        partner_email,
        expected_count,
        has_ac_create_call,
        has_ac_add_system_call,
        has_ac_update_call,
        has_pa_reset_call,
        mockserver,
        mock_personal_store,
        mock_personal_retrieve,
        communications_request,
):
    @mockserver.json_handler(
        '/eats-restapp-communications/internal/communications/v1/send-event',
    )
    def _mock_communications_sender(request):
        assert (
            request.json['recipients']['emails']
            == communications_request['email']
        )
        assert (
            request.json['data']['password']
            == communications_request['password']
        )
        return mockserver.make_response(status=204)

    @mockserver.json_handler('/eats-vendor/api/v1/server/users')
    def _mock_vendor_users_create(req):
        return mockserver.make_response(
            status=200,
            json={'isSuccess': True, 'payload': {'id': partner_id}},
        )

    @mockserver.json_handler(
        '/eats-restapp-authorizer/internal/partner/search',
    )
    def _mock_search_partner(request):
        partners = []
        if partner_id:
            partners.append(
                {'login': request.json['logins'][0], 'partner_id': partner_id},
            )
        return mockserver.make_response(
            status=200, json={'partners': partners},
        )

    @mockserver.json_handler(
        '/eats-restapp-authorizer/internal/partner/set_credentials',
    )
    def _set_creds(request):
        return mockserver.make_response(status=204)

    @mockserver.json_handler('/access-control/v1/admin/users/create/')
    def _mock_access_control_user_create(req):
        return {}

    @mockserver.json_handler(
        '/access-control/v1/admin/users/bulk-add-to-system/',
    )
    def _mock_access_control_user_add_to_system(req):
        return {
            'invalid_users': [],
            'non_existing_users': [],
            'non_existing_groups': [],
        }

    @mockserver.json_handler('/access-control/v1/admin/groups/users/retrieve/')
    def _mock_access_control_groups_retrieve(req):
        return {
            'users': [
                {
                    'provider': 'restapp',
                    'provider_user_id': str(partner_id),
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
                    'user': {
                        'provider': 'restapp',
                        'provider_user_id': str(partner_id),
                    },
                    'group_slug': 'test_group_slug',
                },
            ],
        }

    @mockserver.json_handler('/eats-restapp-authorizer/place-access/reset')
    def _mock_place_access_reset_by_partner(request):
        return mockserver.make_response(status=200)

    response = await request_create_partner(taxi_eats_partners, partner_email)
    assert response.status_code == status_code
    assert response.json() == {'payload': {'id': partner_id}}

    cursor = pgsql['eats_partners'].cursor()
    cursor.execute(
        'SELECT personal_email_id, timezone, '
        'country_code, is_fast_food, partner_uuid '
        'FROM eats_partners.partners '
        'WHERE partner_id = {}'.format(partner_id),
    )
    assert list(cursor) == [
        (
            partner_email + '_id',
            'Europe/Moscow',
            'RU',
            False,
            matching.RegexString(
                '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',
            ),
        ),
    ]
    cursor.execute('SELECT COUNT(*) FROM eats_partners.partners')
    assert cursor.fetchone()[0] == expected_count

    cursor.execute(
        'SELECT partner_id, place_id FROM eats_partners.partner_places',
    )
    assert set(cursor) == {(partner_id, 1), (partner_id, 2), (partner_id, 3)}

    cursor.execute(
        'SELECT partner_id, role_id FROM eats_partners.partner_roles',
    )
    assert set(cursor) == {(partner_id, 1), (partner_id, 3)}

    assert _mock_access_control_user_create.has_calls == has_ac_create_call
    assert (
        _mock_access_control_user_add_to_system.has_calls
        == has_ac_add_system_call
    )
    assert _mock_access_control_groups_retrieve.has_calls == has_ac_update_call
    assert _mock_access_control_bulk_detach.has_calls == has_ac_update_call
    assert _mock_place_access_reset_by_partner.has_calls == has_pa_reset_call
    assert _mock_communications_sender.times_called == 1

    if has_ac_create_call:
        create_args = _mock_access_control_user_create.next_call()

        assert create_args['req'].json['provider'] == 'restapp'
        assert create_args['req'].json['provider_user_id'] == str(partner_id)

    if has_ac_add_system_call:
        add_to_system_args = (
            _mock_access_control_user_add_to_system.next_call()
        )

        assert (
            add_to_system_args['req'].json['users'][0]['provider'] == 'restapp'
        )
        assert add_to_system_args['req'].json['users'][0][
            'provider_user_id'
        ] == str(partner_id)
        assert add_to_system_args['req'].json['groups'] == [
            'communications_common',
            'menu_common',
            'orders_cancel',
            'orders_changes',
            'orders_common',
            'orders_history',
            'places_common',
            'places_pickup_enable',
            'places_plus_common',
            'support_common',
            'support_write',
        ]

    if has_ac_update_call:
        retrieve_args = _mock_access_control_groups_retrieve.next_call()
        assert retrieve_args['req'].query['system'] == 'restapp'
        assert retrieve_args['req'].json['filters']['provider'] == 'restapp'
        assert retrieve_args['req'].json['filters']['provider_user_ids'] == [
            str(partner_id),
        ]
        assert retrieve_args['req'].json['limit'] == 1

        detach_args = _mock_access_control_bulk_detach.next_call()
        assert detach_args['req'].json == {
            'users': [
                {
                    'user': {'provider': 'restapp', 'provider_user_id': '12'},
                    'group_slug': 'test_group_slug',
                },
            ],
        }


@pytest.mark.parametrize(
    'experiment',
    [
        pytest.param(None, id='experiment not found'),
        pytest.param(
            True,
            marks=(get_update_in_vendor_experiment(False)),
            id='experiment enabled',
        ),
    ],
)
async def test_partners_create_vendor_error(
        taxi_eats_partners,
        mock_vendor_users_create_error,
        pgsql,
        experiment,
        taxi_eats_partners_monitor,
        mockserver,
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

    response = await request_create_partner(taxi_eats_partners, 'nana@nuna.nu')

    assert response.status_code == 400
    assert response.json() == {'code': '420', 'message': 'some vendor error'}

    metrics = await taxi_eats_partners_monitor.get_metrics()
    assert metrics['global-sync-statistics']['create_error.vendor'] == 0

    assert _mock_communications_sender.times_called == 0


def set_experiment_for_email(email: str):
    # Возвращает эксперимент eats_partners_update_in_vendor
    predicate = {
        'init': {'value': email, 'arg_name': 'email', 'arg_type': 'string'},
        'type': 'eq',
    }
    return pytest.mark.experiments3(
        name='eats_partners_update_in_vendor',
        consumers=['eats_partners/internal_create'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Matching email',
                'predicate': predicate,
                'value': {'disabled': False},
            },
            {
                'title': 'Other emails',
                'predicate': {'init': {'predicate': predicate}, 'type': 'not'},
                'value': {'disabled': True},
            },
        ],
        is_config=True,
    )


@pytest.mark.config(
    EATS_PARTNERS_SENDING_MAILS_SETTINGS={
        'enables_sending_events': ['create-user'],
    },
)
@pytest.mark.parametrize(
    'first_partner_id, second_partner_id',
    [
        pytest.param(
            42,
            43,
            marks=(
                set_experiment_for_email('first@ya.ru'),
                pytest.mark.pgsql(
                    'eats_partners', files=['insert_partner_data.sql'],
                ),
            ),
            id='create with bigger id',
        ),
        pytest.param(
            42,
            70,
            marks=(
                set_experiment_for_email('first@ya.ru'),
                pytest.mark.pgsql(
                    'eats_partners',
                    files=['insert_partner_data_with_big_serial.sql'],
                ),
            ),
            id='create with smaller id',
        ),
    ],
)
async def test_partners_create_change_serial_value(
        taxi_eats_partners,
        mock_vendor_users_create,
        pgsql,
        first_partner_id,
        second_partner_id,
        mockserver,
        mock_personal_store,
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
        if request.json['logins'][0] == 'first@ya.ru':
            partners.append(
                {
                    'login': request.json['logins'][0],
                    'partner_id': first_partner_id,
                },
            )
        if request.json['logins'][0] == 'second@ya.ru':
            partners.append(
                {
                    'login': request.json['logins'][0],
                    'partner_id': second_partner_id,
                },
            )
        return mockserver.make_response(
            status=200, json={'partners': partners},
        )

    @mockserver.json_handler(
        '/eats-restapp-authorizer/internal/partner/set_credentials',
    )
    def _set_creds(request):
        return mockserver.make_response(status=204)

    response = await request_create_partner(taxi_eats_partners, 'first@ya.ru')
    assert response.status_code == 200
    assert response.json() == {'payload': {'id': first_partner_id}}

    response = await request_create_partner(taxi_eats_partners, 'second@ya.ru')
    assert response.status_code == 200
    assert response.json() == {'payload': {'id': second_partner_id}}

    assert _mock_communications_sender.times_called == 2


@pytest.mark.config(
    EATS_PARTNERS_SENDING_MAILS_SETTINGS={
        'enables_sending_events': ['create-user'],
    },
)
@pytest.mark.pgsql('eats_partners', files=['insert_partner_data.sql'])
async def test_partners_create_400_diff_id(
        taxi_eats_partners,
        pgsql,
        mockserver,
        mock_personal_store,
        mock_personal_retrieve,
):
    @mockserver.json_handler(
        '/eats-restapp-communications/internal/communications/v1/send-event',
    )
    def _mock_communications_sender(req):
        return mockserver.make_response(status=204)

    @mockserver.json_handler('/eats-vendor/api/v1/server/users')
    def _mock_vendor_users_create(req):
        return mockserver.make_response(
            status=200, json={'isSuccess': True, 'payload': {'id': 12}},
        )

    @mockserver.json_handler(
        '/eats-restapp-authorizer/internal/partner/search',
    )
    def _mock_search_partner(request):
        partners = []
        partners.append({'login': request.json['logins'][0], 'partner_id': 10})
        return mockserver.make_response(
            status=200, json={'partners': partners},
        )

    response = await request_create_partner(taxi_eats_partners, 'aaa@aaa.com')
    assert response.status_code == 400

    assert _mock_communications_sender.times_called == 0
