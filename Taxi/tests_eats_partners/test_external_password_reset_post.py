import pytest


@pytest.mark.pgsql('eats_partners', files=['insert_partner_data.sql'])
@pytest.mark.parametrize(
    'email, partner_id, token, is_success',
    [
        ('partner1@partner.com', 1, '111111', True),
        ('PARTNER1@PARTNER.COM', 1, '111111', True),
        ('partner2@partner.com', 2, '222222', True),
        ('PARTNER2@PARTNER.COM', 2, '222222', True),
        ('partner1@partner.com', 1, '123455', False),
        ('PARTNER1@PARTNER.COM', 1, '123455', False),
        ('partner2@partner.com', 2, '123455', False),
        ('PARTNER2@PARTNER.COM', 2, '123455', False),
        ('partner3@partner.com', None, '111111', False),
        ('PARTNER3@PARTNER.COM', None, '111111', False),
    ],
)
async def test_external_reset_password(
        taxi_eats_partners,
        email,
        partner_id,
        token,
        is_success,
        pgsql,
        mockserver,
        mock_sender_password_reset,
        mock_vendor_users_empty_search,
        mock_communications_sender,
        mock_personal_retrieve,
):
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

    @mockserver.json_handler(
        '/eats-restapp-authorizer/v1/session/unset-by-partner',
    )
    def _mock_authorizer(request):
        return mockserver.make_response(status=200)

    @mockserver.json_handler(
        '/eats-vendor/api/v1/server/users/{}'.format(partner_id),
    )
    def _mock_vendor_users_update(req):
        return mockserver.make_response(
            status=200,
            json={
                'isSuccess': True,
                'payload': {
                    'id': partner_id,
                    'name': 'Name',
                    'email': email,
                    'restaurants': [],
                    'isFastFood': False,
                    'timezone': 'Europe/Moscow',
                    'roles': [],
                },
            },
        )

    cursor = pgsql['eats_partners'].cursor()
    cursor.execute('SELECT partner_id,token FROM eats_partners.action_tokens')
    assert len(list(cursor)) == 2

    response = await taxi_eats_partners.post(
        '/4.0/restapp-front/partners/v1/password/reset',
        json={'email': email, 'token': token},
    )

    if is_success:
        assert response.status_code == 200
        cursor.execute(
            'SELECT partner_id,token FROM eats_partners.action_tokens',
        )
        assert len(list(cursor)) == 1
    else:
        assert response.status_code == 400
        assert response.json() == {
            'code': '3',
            'message': (
                'Неверные логин и токен, либо срок действия токена истек'
            ),
        }
        cursor.execute(
            'SELECT partner_id,token FROM eats_partners.action_tokens',
        )
        assert len(list(cursor)) == 2


@pytest.mark.pgsql('eats_partners', files=['insert_partner_data.sql'])
@pytest.mark.parametrize(
    'email, partner_id, is_success',
    [
        ('partner1@partner.com', 1, True),
        ('partner2@partner.com', 2, True),
        ('partner3@partner.com', 3, False),
        ('partner4@partner.com', 4, True),
    ],
)
async def test_external_reset_password_flow(
        taxi_eats_partners,
        email,
        partner_id,
        is_success,
        pgsql,
        mockserver,
        mock_sender_request_reset,
        mock_sender_password_reset,
        mock_vendor_users_empty_search,
        mock_communications_sender,
        mock_personal_retrieve,
):
    @mockserver.json_handler(
        '/eats-restapp-authorizer/internal/partner/search',
    )
    def _mock_search_partner(request):
        assert request.json == {'logins': [email]}
        partners = []
        if is_success:
            partners.append({'partner_id': partner_id, 'login': email})
        return mockserver.make_response(
            status=200, json={'partners': partners},
        )

    @mockserver.json_handler('/personal/v1/emails/find')
    def _mock_personal_find_email(request):
        assert request.json == {'value': email, 'primary_replica': False}
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
    def _mock_authorizer(request):
        return mockserver.make_response(status=200)

    @mockserver.json_handler(
        '/eats-vendor/api/v1/server/users/{}'.format(partner_id),
    )
    def _mock_vendor_users_update(req):
        return mockserver.make_response(
            status=200,
            json={
                'isSuccess': True,
                'payload': {
                    'id': partner_id,
                    'name': 'Name',
                    'email': email,
                    'restaurants': [],
                    'isFastFood': False,
                    'timezone': 'Europe/Moscow',
                    'roles': [],
                },
            },
        )

    cursor = pgsql['eats_partners'].cursor()
    response = await taxi_eats_partners.post(
        '/4.0/restapp-front/partners/v1/password/request-reset',
        json={'email': email},
    )
    assert response.status_code == 200
    assert response.json() == {'is_success': True}
    cursor.execute(
        'SELECT token '
        'FROM eats_partners.action_tokens '
        'WHERE partner_id = {}'.format(partner_id),
    )
    res = list(cursor)
    count = 0
    if is_success:
        count = 1
    assert len(res) == count

    if is_success is False:
        return

    (token,) = res[0]
    response = await taxi_eats_partners.post(
        '/4.0/restapp-front/partners/v1/password/reset',
        json={'email': email, 'token': token},
    )
    assert response.status_code == 200


def get_update_in_vendor_experiment(disabled: bool):
    return pytest.mark.experiments3(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        is_config=True,
        name='eats_partners_update_in_vendor',
        consumers=['eats_partners/internal_create'],
        clauses=[],
        default_value={'disabled': disabled},
    )


@pytest.mark.pgsql('eats_partners', files=['insert_partner_data.sql'])
@pytest.mark.now('2020-01-01T01:00:00Z')
@pytest.mark.parametrize(
    'email, partner_id, is_update_in_vendor',
    [
        pytest.param(
            'partner1@partner.com',
            1,
            True,
            marks=(get_update_in_vendor_experiment(False)),
        ),
        pytest.param(
            'partner2@partner.com',
            2,
            False,
            marks=(get_update_in_vendor_experiment(True)),
        ),
    ],
)
async def test_external_reset_password_with_experiments(
        taxi_eats_partners,
        email,
        partner_id,
        is_update_in_vendor,
        pgsql,
        mockserver,
        mock_sender_request_reset,
        mock_sender_password_reset,
        mock_communications_sender,
        mock_personal_retrieve,
):
    @mockserver.json_handler(
        '/eats-restapp-authorizer/internal/partner/search',
    )
    def _mock_search_partner(request):
        return mockserver.make_response(
            status=200,
            json={
                'partners': [
                    {
                        'login': request.json['logins'][0],
                        'partner_id': partner_id,
                    },
                ],
            },
        )

    @mockserver.json_handler(
        '/eats-restapp-authorizer/internal/partner/set_credentials',
    )
    def _set_creds(request):
        return mockserver.make_response(status=204)

    @mockserver.json_handler(
        '/eats-restapp-authorizer/v1/session/unset-by-partner',
    )
    def _mock_authorizer(request):
        return mockserver.make_response(status=200)

    if is_update_in_vendor:

        @mockserver.json_handler(
            '/eats-vendor/api/v1/server/users/{}'.format(partner_id),
        )
        def _mock_vendor_users_update(req):
            return mockserver.make_response(
                status=200,
                json={
                    'isSuccess': True,
                    'payload': {
                        'id': partner_id,
                        'name': 'Name',
                        'email': email,
                        'restaurants': [],
                        'isFastFood': False,
                        'timezone': 'Europe/Moscow',
                        'roles': [],
                    },
                },
            )

    cursor = pgsql['eats_partners'].cursor()
    response = await taxi_eats_partners.post(
        '/4.0/restapp-front/partners/v1/password/request-reset',
        json={'email': email},
    )
    assert response.status_code == 200
    assert response.json() == {'is_success': True}
    cursor.execute(
        'SELECT token '
        'FROM eats_partners.action_tokens '
        'WHERE partner_id = {}'.format(partner_id),
    )
    res = list(cursor)
    count = 1
    assert len(res) == count

    (token,) = res[0]
    response = await taxi_eats_partners.post(
        '/4.0/restapp-front/partners/v1/password/reset',
        json={'email': email, 'token': token},
    )
    assert response.status_code == 200
