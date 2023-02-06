import datetime
import json
import random
import string

import pytest

ERROR_RESPONSE = {'message': 'Invalid'}
IDENTIFIER_LENGTH = 32
HEADERS = {'X-External-Service': 'Gpartner', 'Accept-Language': 'ru'}
EXPECTED_INT_API_REQUEST_HEADERS = {
    'User-Agent': 'agent_Gpartner',
    'Accept-Language': 'ru',
}


def execute_query(query, pgsql):
    pg_cursor = pgsql['partner_orders_api'].cursor()
    pg_cursor.execute(query)
    return list(pg_cursor)


@pytest.fixture(name='mock_profile')
def _mock_profile(mockserver):
    @mockserver.json_handler('/integration-api/v1/profile')
    def _profile(request):
        return {'user_id': '1233456789'}


@pytest.fixture(name='mock_user_phones')
def _mock_user_phones(mockserver):
    @mockserver.json_handler('/user-api/user_phones')
    def _user_phones(request):
        return {
            'stat': {
                'big_first_discounts': 0,
                'complete': 0,
                'complete_card': 0,
                'complete_apple': 0,
                'complete_google': 0,
                'fake': 0,
                'total': 0,
            },
            'is_loyal': False,
            'is_yandex_staff': False,
            'is_taxi_staff': False,
            'id': 'new_phone_id',
            'type': 'yandex',
            'phone': '+70001112233',
        }


@pytest.fixture(name='mock_users_search')
def _mock_users_search(mockserver):
    @mockserver.json_handler('/user-api/users/search')
    def _users_search(_):
        return {'items': []}


@pytest.fixture(name='mock_users_update')
def _mock_users_update(mockserver):
    @mockserver.json_handler('/user-api/users/integration/update')
    def _update_phone(request):
        assert request.json == {
            'authorized': True,
            'phone_id': 'new_phone_id',
            'application': 'agent_Gpartner',
            'user_id': '1233456789',
        }
        return {}


@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.experiments3(filename='experiments3.json')
async def test_order_draft_headers(
        taxi_partner_orders_api,
        mockserver,
        mock_profile,
        mock_user_phones,
        mock_users_search,
        load_json,
):
    await taxi_partner_orders_api.invalidate_caches()

    request = load_json('request.json')

    @mockserver.json_handler('/integration-api/v1/orders/draft')
    def _order_draft(request):
        assert request.json == load_json('int_api_request.json')
        for key, value in EXPECTED_INT_API_REQUEST_HEADERS.items():
            assert request.headers.get(key) == value
        return load_json('int_api_response.json')

    response = await taxi_partner_orders_api.post(
        'agent/partner-orders-api/v1/order/draft',
        headers=HEADERS,
        json=request,
    )
    assert response.status_code == 200
    assert response.json() == load_json('response.json')

    response = await taxi_partner_orders_api.post(
        'agent/partner-orders-api/v1/order/draft', json=request,
    )
    assert response.status_code == 400


@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.parametrize(
    'overrides, code, response_json, int_api_request_overrides',
    [
        (
            {
                'route': [
                    {
                        'country': 'Россия',
                        'fullname': 'Россия, Москва, Новосущевская, 1',
                        'geopoint': [100, 100],
                    },
                ],
            },
            404,
            {
                'code': 'ZONE_NOT_FOUND',
                'message': 'Can not find geozone for point [100, 100]',
            },
            {},
        ),
        (
            {'due': '2021-01-01T08:29:16+0000', 'is_delayed': True},
            200,
            {'order_id': 'a88b3d49a8c24681bbf8d93cd158d8df'},
            {'due': '2021-01-01T08:29:16+00:00', 'is_delayed': True},
        ),
        (
            {
                'user': {
                    'agent_user_id': '241406a0972b4c4abbf5187e684f0061',
                    'phone': '+70001112233',
                    'type': 'individual',
                },
            },
            403,
            {
                'code': 'UNKNOWN_PHONE',
                'message': 'Phone +70001112233 not found',
            },
            {},
        ),
        (
            {'class': 'comfort'},
            404,
            {
                'code': 'CLASS_NOT_FOUND',
                'message': 'Class comfort not found for zone moscow',
            },
            {},
        ),
        (
            {'requirements': [{'name': 'unknown', 'unknown type': {}}]},
            404,
            {
                'code': 'WRONG_REQUIREMENTS',
                'message': 'Can\'t handle following requirements: {unknown}',
            },
            {},
        ),
        (
            {'comment': 'some comment'},
            200,
            {'order_id': 'a88b3d49a8c24681bbf8d93cd158d8df'},
            {'comment': 'some comment'},
        ),
    ],
)
async def test_order_draft_requests_format(
        taxi_partner_orders_api,
        mockserver,
        mock_profile,
        mock_user_phones,
        mock_users_search,
        load_json,
        overrides,
        code,
        response_json,
        int_api_request_overrides,
):
    request = load_json('request.json')
    request.update(overrides)

    @mockserver.json_handler('/integration-api/v1/orders/draft')
    def _order_draft(request):
        int_api_request = load_json('int_api_request.json')
        int_api_request.update(int_api_request_overrides)
        assert request.json == int_api_request
        return load_json('int_api_response.json')

    response = await taxi_partner_orders_api.post(
        'agent/partner-orders-api/v1/order/draft',
        headers=HEADERS,
        json=request,
    )
    assert response.status_code == code
    assert response.json() == response_json


@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.parametrize(
    'int_api_status, partner_status, response_json',
    [
        (
            400,
            400,
            {'code': 'BAD_REQUEST', 'message': 'Invalid request parameters'},
        ),
        (
            401,
            500,
            {'code': 'INTERNAL_ERROR', 'message': 'Internal server error'},
        ),
        (403, 403, {'code': 'FORBIDDEN', 'message': 'Forbidden'}),
        (406, 406, {'code': 'NOT_ACCEPTABLE', 'message': 'Not acceptable'}),
        (
            429,
            429,
            {'code': 'TOO_MANY_REQUESTS', 'message': 'Too many requests'},
        ),
        (
            500,
            500,
            {'code': 'INTERNAL_ERROR', 'message': 'Internal server error'},
        ),
    ],
)
async def test_order_draft_forwarding_error_response(
        taxi_partner_orders_api,
        mockserver,
        mock_profile,
        mock_user_phones,
        mock_users_search,
        load_json,
        int_api_status,
        partner_status,
        response_json,
):
    request = load_json('request.json')

    @mockserver.json_handler('/integration-api/v1/orders/draft')
    def _order_draft(request):
        int_api_request = load_json('int_api_request.json')
        assert request.json == int_api_request
        return mockserver.make_response(
            json.dumps(ERROR_RESPONSE), status=int_api_status,
        )

    response = await taxi_partner_orders_api.post(
        'agent/partner-orders-api/v1/order/draft',
        headers=HEADERS,
        json=request,
    )
    assert response.status_code == partner_status
    assert response.json() == response_json


@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.config(
    PARTNER_ORDERS_API_AGENTS_WITH_MASKED_PHONES=[
        'gepard',
        'Npartner',
        'Gpartner',
    ],
)
async def test_create_user(
        taxi_partner_orders_api,
        mockserver,
        mock_user_phones,
        mock_users_search,
        load_json,
        pgsql,
        taxi_config,
):
    taxi_config.set(
        PARTNER_ORDERS_API_AGENTS_WITH_MASKED_PHONES=[
            'gepard',
            'Npartner',
            'Gpartner',
        ],
    )
    await taxi_partner_orders_api.invalidate_caches()

    request = load_json('request.json')
    profile_requests = []
    agent_id = 'Gpartner'
    user_id = '1233456789'

    @mockserver.json_handler('/integration-api/v1/orders/draft')
    def _order_draft(request):
        int_api_request = load_json('int_api_request.json')
        int_api_request['agent'].update({'agent_id': agent_id})
        int_api_request.update({'id': user_id})
        assert request.json == int_api_request
        return load_json('int_api_response.json')

    @mockserver.json_handler('/integration-api/v1/profile')
    def _profile(request):
        profile_requests.append(
            {
                'User-Agent': request.headers['User-Agent'],
                'body': request.json,
            },
        )
        return {'user_id': user_id}

    table_name = 'agent_users_new'
    db_users_data = execute_query(
        'SELECT * FROM partner_orders_api.{}'.format(table_name), pgsql,
    )
    assert db_users_data == []

    response = await taxi_partner_orders_api.post(
        'agent/partner-orders-api/v1/order/draft',
        headers={'X-External-Service': agent_id},
        json=request,
    )
    assert response.status_code == 200
    assert profile_requests == [
        {
            'User-Agent': 'agent_' + agent_id,
            'body': {'user': {'phone': '+79179991122'}},
        },
    ]
    db_users_data = execute_query(
        'SELECT * FROM partner_orders_api.{}'.format(table_name), pgsql,
    )

    assert db_users_data == [
        ('241406a0972b4c4abbf5187e684f0061', '1233456789', 'Gpartner'),
    ]


def select_by_user_id(user_id, pgsql):
    return execute_query(
        'SELECT * FROM partner_orders_api.agent_users_new'
        ' WHERE user_id = \'{}\''.format(user_id),
        pgsql,
    )


@pytest.mark.pgsql('partner_orders_api', files=['user.sql'])
@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.config(
    PARTNER_ORDERS_API_AGENTS_WITH_MASKED_PHONES=[
        'gepard',
        'Npartner',
        'Gpartner',
    ],
)
async def test_reuse_user(
        taxi_partner_orders_api,
        mockserver,
        load_json,
        mock_user_phones,
        mock_users_update,
        mock_users_search,
        mocked_time,
):
    await taxi_partner_orders_api.invalidate_caches()

    request = load_json('request.json')
    int_api_expected_user_id = '1233456789'  # user_id from user.sql

    @mockserver.json_handler('/integration-api/v1/orders/draft')
    def _order_draft(request):
        assert request.json['id'] == int_api_expected_user_id
        return load_json('int_api_response.json')

    @mockserver.json_handler('/integration-api/v1/profile')
    def profile(request):
        return {'user_id': 'another_user_id'}

    now = datetime.datetime(2021, 4, 28)
    mocked_time.set(now)
    response = await taxi_partner_orders_api.post(
        'agent/partner-orders-api/v1/order/draft',
        headers={'X-External-Service': 'Gpartner'},
        json=request,
    )
    assert response.status_code == 200
    assert profile.times_called == 0

    # Trying to create another agent user table with new agent_id
    agent_id = 'Npartner'
    int_api_expected_user_id = 'another_user_id'
    response = await taxi_partner_orders_api.post(
        'agent/partner-orders-api/v1/order/draft',
        headers={'X-External-Service': agent_id},
        json=request,
    )
    assert response.status_code == 404
    assert profile.times_called == 0

    mocked_time.set(now + datetime.timedelta(seconds=1))
    # Trying to create another agent user table with new agent_id
    agent_id = 'Npartner'
    int_api_expected_user_id = 'another_user_id'
    response = await taxi_partner_orders_api.post(
        'agent/partner-orders-api/v1/order/draft',
        headers={'X-External-Service': agent_id},
        json=request,
    )
    assert response.status_code == 200
    assert profile.times_called == 1


def generate_random_string(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.config(PARTNER_ORDERS_API_AGENTS_WITH_MASKED_PHONES=['Gpartner'])
async def test_reuse_phone(
        taxi_partner_orders_api,
        mockserver,
        load_json,
        taxi_config,
        mocked_time,
        pgsql,
):
    await taxi_partner_orders_api.invalidate_caches()

    request = load_json('request.json')
    # dict user_id -> phone_id
    db_users = {}

    # dict phone number -> phone_id
    phones = {}

    @mockserver.json_handler('/integration-api/v1/orders/draft')
    def _order_draft(request):
        return load_json('int_api_response.json')

    @mockserver.json_handler('/integration-api/v1/profile')
    def _profile(request):
        nonlocal db_users
        nonlocal phones
        assert request.json['user']['phone']
        user_phone = request.json['user']['phone']
        phone_id = phones.get(user_phone)
        if phone_id:
            for user_id, user_phone_id in db_users.items():
                if user_phone_id == phone_id:
                    return {'user_id': user_id}
        new_user_id = generate_random_string(IDENTIFIER_LENGTH)
        new_phone_id = generate_random_string(IDENTIFIER_LENGTH)
        db_users[new_user_id] = new_phone_id
        phones[user_phone] = new_phone_id
        return {'user_id': new_user_id}

    @mockserver.json_handler('/user-api/users/integration/update')
    def _update_phone(request):
        nonlocal db_users
        assert request.json['user_id']
        user_id = request.json['user_id']
        assert request.json['phone_id']
        phone_id = request.json['phone_id']
        db_users[user_id] = phone_id
        return {}

    @mockserver.json_handler('/user-api/user_phones')
    def _user_phones(request):
        nonlocal phones
        assert request.json['phone']
        user_phone = request.json['phone']
        user_phone_id = phones.get(user_phone)
        if user_phone_id is None:
            user_phone_id = generate_random_string(IDENTIFIER_LENGTH)
            phones[user_phone] = user_phone_id

        return {
            'stat': {
                'big_first_discounts': 0,
                'complete': 0,
                'complete_card': 0,
                'complete_apple': 0,
                'complete_google': 0,
                'fake': 0,
                'total': 0,
            },
            'is_loyal': False,
            'is_yandex_staff': False,
            'is_taxi_staff': False,
            'id': user_phone_id,
            'type': 'yandex',
            'phone': user_phone,
        }

    @mockserver.json_handler('/user-api/users/search')
    def _users_search(request):
        phone_ids = request.json['phone_ids']
        assert phone_ids
        user_phone_id = phone_ids[0]
        items = []
        for user_id, phone_id in db_users.items():
            if user_phone_id == phone_id:
                items.append({'id': user_id, 'application': 'agent_Gpartner'})
        return {'items': items}

    agent_user_id_1 = 'agent_user_id_1'
    phone_1 = '+70000000001'
    agent_user_id_2 = 'agent_user_id_2'
    phone_2 = '+70000000002'

    now = datetime.datetime(2021, 4, 28)
    mocked_time.set(now)

    request['user'].update(
        {
            'agent_user_id': agent_user_id_1,
            'phone': phone_1,
            'type': 'individual',
        },
    )
    response = await taxi_partner_orders_api.post(
        'agent/partner-orders-api/v1/order/draft',
        headers={'X-External-Service': 'Gpartner'},
        json=request,
    )
    assert response.status_code == 200

    request['user'].update(
        {
            'agent_user_id': agent_user_id_2,
            'phone': phone_2,
            'type': 'individual',
        },
    )
    response = await taxi_partner_orders_api.post(
        'agent/partner-orders-api/v1/order/draft',
        headers={'X-External-Service': 'Gpartner'},
        json=request,
    )
    assert response.status_code == 200

    mocked_time.set(now + datetime.timedelta(seconds=1))
    request['user'].update(
        {
            'agent_user_id': agent_user_id_1,
            'phone': phone_2,
            'type': 'individual',
        },
    )
    response = await taxi_partner_orders_api.post(
        'agent/partner-orders-api/v1/order/draft',
        headers={'X-External-Service': 'Gpartner'},
        json=request,
    )
    assert response.status_code == 200
    table_name = 'agent_users_new'

    user_id_rows = execute_query(
        f"""SELECT user_id FROM partner_orders_api.{table_name}
            WHERE agent_user_id = '{agent_user_id_2}';""",
        pgsql,
    )

    assert db_users.get(user_id_rows[0][0]) == phones.get(
        taxi_config.get('PARTNER_ORDERS_API_MOCK_PHONE'),
    )

    mocked_time.set(now + datetime.timedelta(seconds=2))

    request['user'].update(
        {
            'agent_user_id': 'agent_user_id_3',
            'phone': phone_2,
            'type': 'individual',
        },
    )
    response = await taxi_partner_orders_api.post(
        'agent/partner-orders-api/v1/order/draft',
        headers={'X-External-Service': 'Gpartner'},
        json=request,
    )
    assert response.status_code == 200

    user_id_rows = execute_query(
        f"""SELECT user_id FROM partner_orders_api.{table_name}
            WHERE agent_user_id = '{agent_user_id_1}';""",
        pgsql,
    )
    assert db_users.get(user_id_rows[0][0]) == phones.get(
        taxi_config.get('PARTNER_ORDERS_API_MOCK_PHONE'),
    )


@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.experiments3(filename='experiments3.json')
async def test_agent_payment(
        taxi_partner_orders_api,
        mockserver,
        mock_user_phones,
        mock_users_search,
        load_json,
):
    request = load_json('request.json')
    request['payment']['type'] = 'agent'

    @mockserver.json_handler('/integration-api/v1/orders/draft')
    def _order_draft(request):
        assert request.json['payment']['type'] == 'agent'
        assert request.json['payment']['payment_method_id'] == 'agent_Gpartner'
        return load_json('int_api_response.json')

    @mockserver.json_handler('/integration-api/v1/profile')
    def _profile(request):
        return {'user_id': '1233456789'}

    response = await taxi_partner_orders_api.post(
        'agent/partner-orders-api/v1/order/draft',
        headers={'X-External-Service': 'Gpartner'},
        json=request,
    )
    assert response.status_code == 200


@pytest.mark.pgsql('partner_orders_api', files=['user.sql'])
@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.config(PARTNER_ORDERS_API_AGENTS_WITH_MASKED_PHONES=['Gpartner'])
async def test_fetching_user_id(
        taxi_partner_orders_api,
        mockserver,
        testpoint,
        load_json,
        mock_profile,
        mock_user_phones,
        mock_users_update,
        mock_users_search,
        taxi_config,
):
    @testpoint('fetching-from-old-table')
    def fetching_from_old_table(_):
        pass

    @testpoint('fetching-from-new-table')
    def fetching_from_new_table(_):
        pass

    await taxi_partner_orders_api.invalidate_caches()

    request = load_json('request.json')

    @mockserver.json_handler('/integration-api/v1/orders/draft')
    def _order_draft(request):
        return load_json('int_api_response.json')

    response = await taxi_partner_orders_api.post(
        'agent/partner-orders-api/v1/order/draft',
        headers={'X-External-Service': 'Gpartner'},
        json=request,
    )
    assert fetching_from_old_table.times_called == 0
    assert fetching_from_new_table.times_called == 1
    assert response.status_code == 200
