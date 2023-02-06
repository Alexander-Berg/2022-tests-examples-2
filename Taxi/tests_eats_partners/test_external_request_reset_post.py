import pytest


@pytest.mark.pgsql('eats_partners', files=['insert_partner_data.sql'])
@pytest.mark.parametrize(
    'email, is_success, partner_id',
    [
        ('partner1@partner.com', True, 1),
        ('PARTNER1@PARTNER.COM', True, 1),
        ('partner2@partner.com', True, 2),
        ('PARTNER2@PARTNER.COM', True, 2),
        ('partner3@partner.com', False, None),
        ('PARTNER3@PARTNER.COM', False, None),
    ],
)
async def test_external_request_reset_password(
        taxi_eats_partners,
        email,
        is_success,
        partner_id,
        pgsql,
        mock_sender_request_reset,
        mock_vendor_users_empty_search,
        mock_communications_sender,
        mockserver,
        mock_personal_retrieve,
):
    @mockserver.json_handler(
        '/eats-restapp-authorizer/internal/partner/search',
    )
    def _mock_search_by_login(request):
        assert request.json == {'logins': [email]}
        partners = []
        if partner_id:
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

    cursor = pgsql['eats_partners'].cursor()
    cursor.execute(
        'SELECT partner_id,token,created_at,updated_at'
        ' FROM eats_partners.action_tokens',
    )
    assert list(cursor) == []

    response = await taxi_eats_partners.post(
        '/4.0/restapp-front/partners/v1/password/request-reset',
        json={'email': email},
    )
    assert response.status_code == 200
    assert response.json() == {'is_success': True}
    cursor.execute(
        'SELECT partner_id,token,created_at,updated_at'
        ' FROM eats_partners.action_tokens',
    )
    res = list(cursor)
    count = 0
    if is_success:
        count = 1
    assert len(res) == count
    # repeat request
    response = await taxi_eats_partners.post(
        '/4.0/restapp-front/partners/v1/password/request-reset',
        json={'email': email},
    )
    assert response.status_code == 200
    assert response.json() == {'is_success': True}

    cursor.execute(
        'SELECT partner_id,token,created_at,updated_at'
        ' FROM eats_partners.action_tokens',
    )
    if is_success:
        old = res[0]
        new = list(cursor)[0]
        (partner_id_l, token, created_at, updated_at) = old
        (partner_id_l_n, token_n, created_at_n, updated_at_n) = new
        assert partner_id_l == partner_id_l_n
        assert token == token_n
        assert created_at == created_at_n
        assert updated_at != updated_at_n


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
@pytest.mark.parametrize(
    'email, partner_id, is_update_in_vendor',
    [
        pytest.param(
            'partner3@partner.com',
            42,
            True,
            marks=(get_update_in_vendor_experiment(False)),
        ),
    ],
)
async def test_request_reset_creates_partner(
        taxi_eats_partners,
        email,
        partner_id,
        is_update_in_vendor,
        pgsql,
        mockserver,
        mock_sender_request_reset,
        mock_communications_sender,
        mock_personal_retrieve,
):
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
        '/eats-restapp-authorizer/internal/partner/search',
    )
    def _mock_search_by_login(request):
        assert request.json == {'logins': [email]}
        return mockserver.make_response(
            status=200,
            json={'partners': [{'partner_id': partner_id, 'login': email}]},
        )

    @mockserver.json_handler('/personal/v1/emails/find')
    def _personal_find_email(request):
        assert request.json == {'value': email, 'primary_replica': False}
        return {
            'id': request.json['value'] + '_id',
            'value': request.json['value'],
        }

    cursor = pgsql['eats_partners'].cursor()
    cursor.execute(
        """
        SELECT partner_id
        FROM eats_partners.action_tokens
    """,
    )
    assert list(cursor) == []

    cursor.execute(
        """
        SELECT partner_id
        FROM eats_partners.partners
        WHERE personal_email_id = '{}'
    """.format(
            email + '_id',
        ),
    )
    assert list(cursor) == []

    @mockserver.json_handler('/eats-vendor/api/v1/server/users/search')
    def _mock_vendor_users_search(req):
        return mockserver.make_response(
            status=200,
            json={
                'isSuccess': True,
                'payload': [
                    {
                        'id': partner_id,
                        'name': 'nananuna',
                        'email': email,
                        'restaurants': [343, 454],
                        'isFastFood': True,
                        'timezone': 'utc',
                        'roles': [
                            {
                                'id': 1,
                                'title': 'operator',
                                'role': 'ROLE_OPERATOR',
                            },
                        ],
                    },
                ],
                'meta': {'count': 1},
            },
        )

    response = await taxi_eats_partners.post(
        '/4.0/restapp-front/partners/v1/password/request-reset',
        json={'email': email},
    )
    assert response.status_code == 200
    assert response.json() == {'is_success': True}
    cursor.execute(
        """
        SELECT partner_id
        FROM eats_partners.action_tokens
    """,
    )
    assert list(cursor) == [(partner_id,)]

    cursor.execute(
        """
        SELECT partner_id
        FROM eats_partners.partners
        WHERE personal_email_id = '{}'
    """.format(
            email + '_id',
        ),
    )
    assert list(cursor) == [(partner_id,)]
