# pylint: disable=too-many-lines
# TODO: split into test_delete.py and test_status.py
import datetime
import json
import operator
from typing import Any, Dict, List, Optional  # noqa: IS001

import pytest
import ticket_parser2

from taxi import config
from taxi.pytest_plugins import core as pytest_core


TVM_KEYS_URL = (
    f'{config.Config.TVM_API_URL}/2/keys?lib_version'
    f'={ticket_parser2.__version__.decode()}'
)

TAKEOUT_DELETE_COOLDOWNS_CONFIG = [
    {'category_name': 'taxi', 'delete_cooldown_seconds': 86400},
]

TAKEOUT_SERVICES_CONFIG = [
    {
        'name': 'safety-center',
        'data_category': 'taxi',
        'host': 'http://safety-center.tst.yandex.net',
        'endpoints': {
            'status': {'path': '/safety-center/status'},
            'delete_async': {'path': '/safety-center/delete'},
        },
    },
    {
        'name': 'user-api',
        'data_category': 'taxi',
        'host': 'http://user-api.tst.yandex.net',
        'endpoints': {
            'status': {'path': '/user-api/status'},
            'delete_async': {'path': '/user-api/delete'},
        },
    },
    {
        'name': 'eats-service',
        'data_category': 'eats',
        'host': 'http://eats-service.tst.yandex.net',
        'endpoints': {'status': {'path': '/eats/status'}},
    },
    {
        'name': 'grocery-service',
        'data_category': 'grocery',
        'host': 'http://grocery-service.tst.yandex.net',
        'endpoints': {
            'status': {'path': '/grocery/status'},
            'delete_async': {'path': '/grocery/delete'},
        },
    },
    {
        'name': 'grocery-service_second',
        'data_category': 'grocery',
        'host': 'http://grocery-service_second.tst.yandex.net',
        'endpoints': {'status': {'path': '/grocery_second/status'}},
    },
    {
        'name': 'some-service',
        'data_category': 'not_relevant',
        'host': 'http://some-service.tst.yandex.net',
        'endpoints': {'delete_async': {'path': '/some-service/delete'}},
    },
    {
        'name': 'order-core',
        'data_category': 'taxi',
        'host': 'http://order-core.taxi.tst.yandex.net',
        'endpoints': {
            'check_entities': {
                'path': '/v1/tc/active-orders',
                'method': 'GET',
                'headers': [{'name': 'X-Yandex-UID', 'entity': 'yandex_uid'}],
                'query': [{'name': 'phone_id', 'entity': 'phone_id'}],
                'response_rules': [
                    {
                        'path': 'orders',
                        'error_code': 'TAXI_TAKEOUT_ACTIVE_ORDER_ERROR',
                        'reason': 'user has active orders!',
                        'predicate': 'is_empty',
                    },
                ],
            },
        },
    },
    {
        'name': 'debts',
        'data_category': 'taxi',
        'host': 'http://debts-l7.taxi.tst.yandex.net',
        'endpoints': {
            'check_entities': {
                'path': '/internal/debts/list',
                'method': 'GET',
                'query': [
                    {'name': 'phone_id', 'entity': 'phone_id'},
                    {'name': 'yandex_uid', 'entity': 'yandex_uid'},
                    {
                        'name': 'application',
                        'entity': 'application',
                        'default_value': 'takeout-service',
                    },
                ],
                'response_rules': [
                    {
                        'path': 'debts',
                        'error_code': 'TAXI_TAKEOUT_DEBT_ERROR',
                        'reason': 'user has debts!',
                        'predicate': 'is_empty',
                    },
                ],
            },
        },
    },
]

TAKEOUT_DATA_CATEGORIES_CONFIG = [
    {'data_category': 'taxi', 'data_slug': 'common_taxi_data'},
    {'data_category': 'eats', 'data_slug': 'common_eats_data'},
    {'data_category': 'grocery', 'data_slug': 'common_grocery_data'},
    {
        'data_category': 'disabled_category',
        'data_slug': 'disabled_category_slug',
        'is_disabled': True,
    },
]

YANDEX_UID = '12345'
BOUND_PHONISH = '23456'
EMAIL_IDS = ['emailid1', 'emailid2']
PHONE_IDS = ['phoneid1', 'phoneid2']

DATA_STATE_EXISTS = 'ready_to_delete'
DATA_STATE_EMPTY = 'empty'
DATA_STATE_IN_PROGRESS = 'delete_in_progress'


class MockUserTicket:
    default_uid = YANDEX_UID


class UserContextMock:
    def __init__(self, tvm_env, tvm_keys):
        pass

    def check(self, x_ya_user_ticket):
        return MockUserTicket()


@pytest.fixture(name='mock_tvm_keys')
def mock_tvm_keys_fixture(patch_aiohttp_session, response_mock):
    @patch_aiohttp_session(TVM_KEYS_URL, 'GET')
    def _patch_get_keys(method, url, **kwargs):
        return response_mock(text='tvm-keys')


@pytest.fixture(name='mock_status')
def mock_status_fixture(patch_aiohttp_session, response_mock, load_json):
    """
    WARNING:
        незамоканные ендпойнты вернут то же самое,
        что вернёт последний замоканный ендпойнт
    """

    def _mock_status(service_name, data_state, has_errors=False):
        host_url = f'http://{service_name}.tst.yandex.net'

        @patch_aiohttp_session(host_url, 'POST')
        def _mock_api(method, url, *args, **kwargs):
            if has_errors:
                raise Exception('something bad happened')

            _mock_api.times_called += 1
            assert kwargs['json']['yandex_uids'] == [
                {'uid': YANDEX_UID, 'is_portal': True},
                {'uid': BOUND_PHONISH, 'is_portal': False},
            ]
            assert kwargs['json']['personal_email_ids'] == EMAIL_IDS
            return response_mock(
                status=200, json={'data_state': data_state}, url=url,
            )

        _mock_api.times_called = 0
        return _mock_api

    return _mock_status


@pytest.fixture(name='mock_zalogin')
def mock_zalogin_service(mockserver):
    @mockserver.json_handler('/zalogin/v1/internal/uid-info')
    def _uid_info(request):
        assert request.query['yandex_uid'] == YANDEX_UID
        return {
            'yandex_uid': YANDEX_UID,
            'bound_phonishes': [BOUND_PHONISH],
            'type': 'portal',
        }


@pytest.fixture(name='mock_user_api')
def mock_user_api_service(mockserver):
    @mockserver.json_handler('/user-api/users/search')
    def _user_api_search(request):
        yandex_uids = request.json['yandex_uids']
        assert yandex_uids == [YANDEX_UID, BOUND_PHONISH]
        user_objects = [
            {'yandex_uid': yandex_uid, 'id': '1', 'phone_id': phone_id}
            for yandex_uid, phone_id in zip(yandex_uids, PHONE_IDS)
        ]
        return {'items': user_objects}

    @mockserver.json_handler('/user-api/user_phones/get_bulk')
    def _user_api_get_phones_bulk(request):
        assert request.json['ids'] == PHONE_IDS
        return {'items': []}

    @mockserver.json_handler('/user-api/user_emails/get')
    def _user_api_get_emails(request):
        assert request.json['yandex_uids'] == [YANDEX_UID, BOUND_PHONISH]
        email_objects = [
            {'id': '1', 'personal_email_id': email_id}
            for email_id in EMAIL_IDS
        ]
        return {'items': email_objects}


def check_data_status(
        data_status: Dict,
        expected_state: str,
        expected_category: str,
        expected_slug: str,
        expected_update_date: Optional[str] = None,
):
    assert data_status['state'] == expected_state
    assert data_status['id'] == expected_category
    assert data_status['slug'] == expected_slug
    assert data_status.get('update_date') == expected_update_date


def check_stq(stq_data, expected_data_categories, task_id_path='id'):
    assert (
        stq_data[task_id_path]
        == YANDEX_UID + stq_data['kwargs']['data_category']
    )
    assert stq_data['kwargs']['data_category'] in expected_data_categories
    assert stq_data['kwargs']['yandex_uid'] == YANDEX_UID


TAKEOUT_SERVICES_CONFIG_WITH_DISABLED_CATEGORY = [
    {
        'name': 'disabled_service',
        'data_category': 'disabled_category',
        'host': 'http://disabled-service.tst.yandex.net',
        'endpoints': {
            'status': {'path': '/disabled-service/status'},
            'delete': {'path': '/disabled-service/delete'},
        },
    },
]


@pytest.mark.parametrize(
    ['expect_number_categories', 'expect_disabled_service_called'],
    [
        pytest.param(
            2,  # default pg state has eats service in progress
            1,
            marks=[
                pytest.mark.config(
                    TAKEOUT_DATA_CATEGORIES=[
                        {
                            'data_category': 'disabled_category',
                            'data_slug': 'disabled_category_slug',
                        },
                    ],
                ),
            ],
            id='no disabled category',
        ),
        pytest.param(
            1,  # default pg state has eats service in progress
            0,
            marks=[
                pytest.mark.config(
                    TAKEOUT_DATA_CATEGORIES=[
                        {
                            'data_category': 'disabled_category',
                            'data_slug': 'disabled_category_slug',
                            'is_disabled': True,
                        },
                    ],
                ),
            ],
            id='category is disabled',
        ),
    ],
)
@pytest.mark.config(
    TAKEOUT_SERVICES_V2=TAKEOUT_SERVICES_CONFIG_WITH_DISABLED_CATEGORY,
)
async def test_takeout_status_disabled_category(
        web_app_client,
        monkeypatch,
        mock_tvm_keys,
        mock_status,
        mock_zalogin,
        mock_user_api,
        expect_number_categories,
        expect_disabled_service_called,
):
    monkeypatch.setattr('ticket_parser2.api.v1.UserContext', UserContextMock)
    mock_disabled_service = mock_status('disabled-service', DATA_STATE_EMPTY)
    response = await web_app_client.get(
        '/1/takeout/status?request_id=123',
        headers={
            'X-Ya-User-Ticket': 'user_ticket',
            'X-Ya-Service-Ticket': 'service_ticket',
        },
    )

    assert mock_disabled_service.times_called == expect_disabled_service_called
    data = await response.json()
    assert response.status == 200
    assert data['status'] == 'ok'
    assert len(data['data']) == expect_number_categories
    sorted_answers = sorted(data['data'], key=operator.itemgetter('id'))
    check_data_status(
        sorted_answers[-1], DATA_STATE_IN_PROGRESS, 'eats', 'eats', None,
    )
    if expect_number_categories == 2:
        check_data_status(
            sorted_answers[0],
            DATA_STATE_EMPTY,
            'disabled_category',
            'disabled_category_slug',
        )


@pytest.mark.config(TAKEOUT_SERVICES_V2=TAKEOUT_SERVICES_CONFIG)
@pytest.mark.config(TAKEOUT_DATA_CATEGORIES=TAKEOUT_DATA_CATEGORIES_CONFIG)
async def test_takeout_status_succeeded(
        web_app_client,
        patch_aiohttp_session,
        response_mock,
        monkeypatch,
        mockserver,
        mock_tvm_keys,
        mock_status,
        mock_zalogin,
        mock_user_api,
):
    monkeypatch.setattr('ticket_parser2.api.v1.UserContext', UserContextMock)

    mock_safety_center = mock_status('safety-center', DATA_STATE_EMPTY)
    mock_user_api = mock_status('user-api', DATA_STATE_EXISTS)
    mock_eats_service = mock_status('eats-service', DATA_STATE_EXISTS)
    mock_grocery_service = mock_status('grocery-service', DATA_STATE_EMPTY)
    mock_grocery_service_second = mock_status(
        'grocery-service_second', DATA_STATE_IN_PROGRESS,
    )

    response = await web_app_client.get(
        '/1/takeout/status?request_id=123',
        headers={
            'X-Ya-User-Ticket': 'user_ticket',
            'X-Ya-Service-Ticket': 'service_ticket',
        },
    )

    assert mock_safety_center.times_called == 1
    assert mock_user_api.times_called == 1
    assert mock_grocery_service.times_called == 1
    assert mock_grocery_service_second.times_called == 1
    # eats data status is "deleting"
    assert mock_eats_service.times_called == 0

    data = await response.json()
    assert response.status == 200
    assert data['status'] == 'ok'
    assert len(data['data']) == 3

    sorted_answers = sorted(data['data'], key=operator.itemgetter('id'))
    check_data_status(
        sorted_answers[0],
        DATA_STATE_IN_PROGRESS,
        'eats',
        'common_eats_data',
        None,
    )
    check_data_status(
        sorted_answers[1],
        DATA_STATE_IN_PROGRESS,  # 'delete_in_progress' status is forwarded
        'grocery',
        'common_grocery_data',
        '2018-01-01 07:00:00+00:00',
    )
    check_data_status(
        sorted_answers[2], DATA_STATE_EXISTS, 'taxi', 'common_taxi_data',
    )


@pytest.mark.config(TAKEOUT_SERVICES_V2=TAKEOUT_SERVICES_CONFIG)
@pytest.mark.config(TAKEOUT_DATA_CATEGORIES=TAKEOUT_DATA_CATEGORIES_CONFIG)
@pytest.mark.pgsql(
    'taxi_takeout', files=['pg_taxi_takeout_delete_grocery.sql'],
)
async def test_takeout_status_succeeded_no_update_date(
        web_app_client,
        patch_aiohttp_session,
        response_mock,
        monkeypatch,
        mockserver,
        mock_tvm_keys,
        mock_status,
        mock_zalogin,
        mock_user_api,
):
    monkeypatch.setattr('ticket_parser2.api.v1.UserContext', UserContextMock)

    mock_grocery_service = mock_status('grocery-service', DATA_STATE_EMPTY)

    response = await web_app_client.get(
        '/1/takeout/status?request_id=123',
        headers={
            'X-Ya-User-Ticket': 'user_ticket',
            'X-Ya-Service-Ticket': 'service_ticket',
        },
    )
    assert response.status == 200

    assert mock_grocery_service.times_called >= 1

    data = await response.json()
    assert data['status'] == 'ok'
    assert len(data['data']) == 3

    sorted_answers = sorted(data['data'], key=operator.itemgetter('id'))
    check_data_status(
        sorted_answers[1], DATA_STATE_EMPTY, 'grocery', 'common_grocery_data',
    )


@pytest.mark.config(TAKEOUT_DELETE_COOLDOWNS=TAKEOUT_DELETE_COOLDOWNS_CONFIG)
@pytest.mark.config(TAKEOUT_SERVICES_V2=TAKEOUT_SERVICES_CONFIG)
@pytest.mark.config(TAKEOUT_DATA_CATEGORIES=TAKEOUT_DATA_CATEGORIES_CONFIG)
@pytest.mark.pgsql('taxi_takeout', files=['pg_taxi_takeout_cooldowns.sql'])
@pytest.mark.parametrize(
    'expect_cooldown',
    (
        pytest.param(
            False,
            marks=[pytest.mark.now('2018-01-02T07:00:00Z')],
            id='No cooldowns',
        ),
        pytest.param(
            True,
            marks=[pytest.mark.now('2018-01-02T05:00:00Z')],
            id='taxi on cooldown',
        ),
    ),
)
async def test_takeout_status_cooldowns(
        web_app_client,
        monkeypatch,
        mock_tvm_keys,
        mock_zalogin,
        mock_user_api,
        mock_status,
        expect_cooldown,
):
    monkeypatch.setattr('ticket_parser2.api.v1.UserContext', UserContextMock)
    mock_status('safety-center', DATA_STATE_EMPTY)
    mock_status('user-api', DATA_STATE_EMPTY)
    mock_status('eats-service', DATA_STATE_EMPTY)
    mock_status('grocery-service', DATA_STATE_EMPTY)
    response = await web_app_client.get(
        '/1/takeout/status?request_id=123',
        headers={
            'X-Ya-User-Ticket': 'user_ticket',
            'X-Ya-Service-Ticket': 'service_ticket',
        },
    )
    data = await response.json()
    taxi_data = (
        {
            'id': 'taxi',
            'slug': 'common_taxi_data',
            'state': 'empty',
            'update_date': '2018-01-01 07:00:00+00:00',
        }
        if expect_cooldown
        else {
            'id': 'taxi',
            'slug': 'common_taxi_data',
            'state': 'delete_in_progress',
        }
    )
    assert sorted(data) == sorted(
        {
            'status': 'ok',
            'data': [
                taxi_data,
                {'id': 'eats', 'slug': 'common_eats_data', 'state': 'empty'},
                {
                    'id': 'grocery',
                    'slug': 'common_grocery_data',
                    'state': 'empty',
                },
            ],
        },
    )


@pytest.mark.config(TAKEOUT_SERVICES_V2=TAKEOUT_SERVICES_CONFIG)
@pytest.mark.config(TAKEOUT_DATA_CATEGORIES=TAKEOUT_DATA_CATEGORIES_CONFIG)
async def test_takeout_status_succeeded_has_errors(
        web_app_client,
        patch_aiohttp_session,
        response_mock,
        monkeypatch,
        mockserver,
        mock_tvm_keys,
        mock_status,
        mock_zalogin,
        mock_user_api,
):
    monkeypatch.setattr('ticket_parser2.api.v1.UserContext', UserContextMock)

    mock_safety_center = mock_status('safety-center', DATA_STATE_EMPTY, True)
    mock_user_api = mock_status('user-api', DATA_STATE_EXISTS)
    mock_eats_service = mock_status('eats-service', DATA_STATE_EXISTS, True)
    mock_grocery_service = mock_status(
        'grocery-service', DATA_STATE_EMPTY, True,
    )
    mock_grocery_service_second = mock_status(
        'grocery-service_second', DATA_STATE_IN_PROGRESS,
    )

    response = await web_app_client.get(
        '/1/takeout/status?request_id=123',
        headers={
            'X-Ya-User-Ticket': 'user_ticket',
            'X-Ya-Service-Ticket': 'service_ticket',
        },
    )

    assert mock_safety_center.times_called == 0
    assert mock_user_api.times_called == 1
    assert mock_eats_service.times_called == 0
    assert mock_grocery_service.times_called == 0
    assert mock_grocery_service_second.times_called == 1

    data = await response.json()
    assert response.status == 200
    assert data['status'] == 'ok'
    assert len(data['data']) == 1

    sorted_answers = sorted(data['data'], key=operator.itemgetter('id'))

    check_data_status(
        sorted_answers[0],
        DATA_STATE_IN_PROGRESS,
        'eats',
        'common_eats_data',
        None,
    )
    errors = data['errors']
    assert errors == [
        {
            'code': 'INTERNAL_ERROR',
            'message': (
                'Category "taxi": '
                'Internal error occurred while getting data status in '
                'safety-center: something bad happened'
            ),
        },
        {
            'code': 'INTERNAL_ERROR',
            'message': (
                'Category "grocery": '
                'Internal error occurred while getting data status in '
                'grocery-service: something bad happened'
            ),
        },
    ]


@pytest.mark.config(
    TAKEOUT_SERVICES_V2=[
        {
            'name': 'safety-center',
            'data_category': 'taxi',
            'host': 'http://safety-center.tst.yandex.net',
            'endpoints': {'status': {'path': '/safety-center/status'}},
        },
        {
            'name': 'user-api',
            'data_category': 'taxi',
            'host': 'http://user-api.tst.yandex.net',
            'endpoints': {'status': {'path': '/user-api/status'}},
        },
        {
            'name': 'grocery-service',
            'data_category': 'grocery',
            'host': 'http://grocery-service.tst.yandex.net',
            'endpoints': {'status': {'path': '/grocery/status'}},
        },
    ],
)
@pytest.mark.config(TAKEOUT_DATA_CATEGORIES=TAKEOUT_DATA_CATEGORIES_CONFIG)
@pytest.mark.pgsql('taxi_takeout', files=['pg_taxi_takeout_failed.sql'])
async def test_takeout_status_failed(
        web_app_client,
        patch_aiohttp_session,
        response_mock,
        monkeypatch,
        mockserver,
        mock_tvm_keys,
        mock_status,
        mock_zalogin,
        mock_user_api,
):
    monkeypatch.setattr('ticket_parser2.api.v1.UserContext', UserContextMock)

    mock_status('safety-center', DATA_STATE_EXISTS, True)
    mock_status('user-api', DATA_STATE_EMPTY, True)
    mock_status('grocery-service', DATA_STATE_EMPTY, True)

    response = await web_app_client.get(
        '/1/takeout/status?request_id=123',
        headers={
            'X-Ya-User-Ticket': 'user_ticket',
            'X-Ya-Service-Ticket': 'service_ticket',
        },
    )

    data = await response.json()
    assert response.status == 200
    assert data['status'] == 'error'
    assert len(data['errors']) == 3
    for error in data['errors']:
        assert error['code'] == 'INTERNAL_ERROR'


@pytest.mark.parametrize(
    ['data_status', 'broken_category', 'times_called'],
    [
        pytest.param('ok', None, 2, id='ok'),
        pytest.param(
            'error', 'disabled_category', 0, id='has disabled category',
        ),
        pytest.param(
            'error',
            'stq_forbidden_service_caller',
            3,
            id='stq_forbidden_service_caller',
        ),
        pytest.param('error', 'stq_agent_fails', 5, id='stq_agent_fails'),
    ],
)
@pytest.mark.now('2022-01-01T01:00:00Z')
@pytest.mark.config(TAKEOUT_DATA_CATEGORIES=TAKEOUT_DATA_CATEGORIES_CONFIG)
async def test_takeout_delete_endpoint(
        web_context,
        web_app_client,
        pgsql,
        patch_aiohttp_session,
        response_mock,
        monkeypatch,
        mockserver,
        mock_tvm_keys,
        mock_status,
        mock_zalogin,
        mock_user_api,
        data_status,
        broken_category,
        times_called,
):
    monkeypatch.setattr('ticket_parser2.api.v1.UserContext', UserContextMock)
    data_categories = ['1', '2']
    old_dt = datetime.datetime.fromisoformat('2018-01-01T10:00:00+03:00')
    new_dt = datetime.datetime.fromisoformat('2022-01-01T01:00:00+00:00')
    expected_deletions = [
        ('12345', '1', 'deleting', 'takeout', new_dt),
        ('12345', '2', 'deleting', 'takeout', new_dt),
        ('12345', 'eats', 'deleting', 'takeout', old_dt),
        ('12345', 'grocery', 'deleted', 'takeout', old_dt),
    ]
    if broken_category:
        data_categories.append(broken_category)

    @mockserver.json_handler(
        '/stq-agent/queues/api/add/takeout_delete_user_data',
    )
    def takeout_delete_user_data(request):
        kwargs = request.json['kwargs']
        status = 200
        if kwargs.get('data_category') == 'stq_forbidden_service_caller':
            status = 403
        if kwargs.get('data_category') == 'stq_agent_fails':
            status = 500
        return mockserver.make_response(
            json.dumps({}),
            status=status,
            headers={'Content-Type': 'application/json'},
        )

    response = await web_app_client.post(
        '/1/takeout/delete?request_id=123',
        headers={
            'X-Ya-User-Ticket': 'user_ticket',
            'X-Ya-Service-Ticket': 'service_ticket',
        },
        json={'id': data_categories},
    )

    data = await response.json()

    assert response.status == 200
    assert data['status'] == data_status
    if data_status == 'error':
        has_error_by_broken_category = False
        for error in data['errors']:
            if broken_category in error['message']:
                has_error_by_broken_category = True
        assert has_error_by_broken_category
    assert takeout_delete_user_data.times_called == times_called
    if times_called == 0:
        return
    for _ in range(0, times_called):
        check_stq(
            takeout_delete_user_data.next_call()['request'].json,
            data_categories,
            task_id_path='task_id',
        )

    db = pgsql['taxi_takeout']
    cursor = db.cursor()
    cursor.execute(
        'SELECT yandex_uid, data_category, status, service_name, '
        'last_deletion_request_at FROM takeout.deletions '
        'ORDER BY (yandex_uid, data_category, status, service_name)',
    )
    assert sorted(cursor) == sorted(expected_deletions)


@pytest.fixture(name='mock_services')
def mock_services_fixture(
        patch_aiohttp_session, response_mock: pytest_core.Response, load_json,
):
    """
    WARNING:
        незамоканные ендпойнты вернут то же самое,
        что вернёт последний замоканный ендпойнт
    """

    def _mock_services(
            service_name,
            host_url,
            method='POST',
            request_data=None,
            response_status=200,
            response_json=None,
    ):
        @patch_aiohttp_session(host_url, method)
        def _mock_api(method, url, *args, **kwargs):
            _mock_api.times_called += 1
            if request_data is not None:
                assert kwargs['json'] == request_data
            return response_mock(status=response_status, json=response_json)

        _mock_api.times_called = 0
        return _mock_api

    return _mock_services


ORDER_CORE_HAS_ORDERS_RESPONSE = {
    'orders': [
        {
            'orderid': 'd278531afe9a32f38a387c101e7a02db',
            'status': 'transporting',
            'due': '2021-11-29T14:37:17+0000',
            'service_level': 0,
            'pending_changes': [],
        },
    ],
}
ORDER_CORE_NO_ORDERS_RESPONSE: Dict[str, List[Dict[str, Any]]] = {'orders': []}

DEBTS_HAS_DEBTS_RESPONSE = {
    'debts': [
        {'order_id': 'k9_order_id', 'currency': 'RUB', 'value': '3.1415'},
    ],
}
DEBTS_NO_DEBTS_RESPONSE: Dict[str, List[Dict[str, Any]]] = {'debts': []}


@pytest.mark.config(TAKEOUT_DELETE_COOLDOWNS=TAKEOUT_DELETE_COOLDOWNS_CONFIG)
@pytest.mark.config(TAKEOUT_SERVICES_V2=TAKEOUT_SERVICES_CONFIG)
@pytest.mark.config(TAKEOUT_DATA_CATEGORIES=TAKEOUT_DATA_CATEGORIES_CONFIG)
@pytest.mark.pgsql('taxi_takeout', files=['pg_taxi_takeout_cooldowns.sql'])
@pytest.mark.parametrize(
    [
        'data_status',
        'debts_response_json',
        'orders_core_json',
        'expect_cooldown',
    ],
    [
        pytest.param(
            'error',
            DEBTS_HAS_DEBTS_RESPONSE,
            ORDER_CORE_HAS_ORDERS_RESPONSE,
            False,
        ),
        pytest.param(
            'ok',
            DEBTS_NO_DEBTS_RESPONSE,
            ORDER_CORE_NO_ORDERS_RESPONSE,
            False,
        ),
        pytest.param(
            'error',
            DEBTS_NO_DEBTS_RESPONSE,
            ORDER_CORE_NO_ORDERS_RESPONSE,
            True,
            marks=[pytest.mark.now('2018-01-02T05:00:00Z')],
            id='taxi on cooldown',
        ),
    ],
)
async def test_takeout_delete_async(
        web_context,
        web_app_client,
        pgsql,
        patch_aiohttp_session,
        response_mock,
        monkeypatch,
        mockserver,
        mock_tvm_keys,
        mock_status,
        mock_zalogin,
        mock_user_api,
        mock_services,
        stq,
        data_status,
        debts_response_json,
        orders_core_json,
        expect_cooldown,
):
    mock_order_core_ = mock_services(
        'order-core',
        'http://order-core.taxi.tst.yandex.net',
        method='GET',
        response_json=orders_core_json,
    )
    mock_debts_ = mock_services(
        'debts',
        'http://debts-l7.taxi.tst.yandex.net',
        method='GET',
        response_json=debts_response_json,
    )
    mock_safety_center_ = mock_services(
        'safety-center', 'http://safety-center.tst.yandex.net',
    )
    mock_user_api_ = mock_services(
        'user-api', 'http://user-api.tst.yandex.net',
    )
    mock_grocery_ = mock_services(
        'grocery', 'http://grocery-service.tst.yandex.net',
    )
    mock_some_service_ = mock_services(
        'some-service', 'http://some-service.tst.yandex.net',
    )
    monkeypatch.setattr('ticket_parser2.api.v1.UserContext', UserContextMock)
    response = await web_app_client.post(
        '/1/takeout/delete?request_id=123',
        headers={
            'X-Ya-User-Ticket': 'user_ticket',
            'X-Ya-Service-Ticket': 'service_ticket',
        },
        json={'id': ['taxi', 'grocery']},
    )

    data = await response.json()

    assert response.status == 200
    assert data['status'] == data_status
    if data_status == 'error':
        if expect_cooldown:
            assert data == {
                'status': 'error',
                'errors': [
                    {
                        'code': 'CATEGORIES_ON_COOLDOWN_ERROR',
                        'message': (
                            'Deletion is not allowed because of '
                            'following categories are on cooldown:{\'taxi\'}'
                        ),
                    },
                ],
            }
        else:
            assert data['errors'] == [
                {
                    'code': 'TAXI_TAKEOUT_ACTIVE_ORDER_ERROR',
                    'message': (
                        'Deletion is not allowed because of user has active '
                        'orders!'
                    ),
                },
                {
                    'code': 'TAXI_TAKEOUT_DEBT_ERROR',
                    'message': (
                        'Deletion is not allowed because of user has debts!'
                    ),
                },
            ]
        return
    assert mock_order_core_.times_called == 2
    assert mock_debts_.times_called == 2

    expected_data_categories = ['taxi', 'grocery']
    assert stq.takeout_delete_user_data.times_called == 2
    check_stq(
        stq.takeout_delete_user_data.next_call(), expected_data_categories,
    )
    check_stq(
        stq.takeout_delete_user_data.next_call(), expected_data_categories,
    )

    assert mock_safety_center_.times_called == 1
    assert mock_user_api_.times_called == 1
    assert mock_grocery_.times_called == 1
    assert mock_some_service_.times_called == 0

    db = pgsql['taxi_takeout']
    cursor = db.cursor()
    cursor.execute(
        'SELECT yandex_uid, data_category, status, '
        'service_name FROM takeout.deletions '
        'ORDER BY (yandex_uid, data_category, status, service_name)',
    )
    deletions = list(cursor)
    assert deletions == [
        ('12345', 'grocery', 'deleting', 'grocery-service'),
        ('12345', 'grocery', 'deleting', 'takeout'),
        ('12345', 'taxi', 'deleting', 'safety-center'),
        ('12345', 'taxi', 'deleting', 'takeout'),
        ('12345', 'taxi', 'deleting', 'user-api'),
    ]


@pytest.mark.parametrize(
    ['json_request', 'expected_deletions', 'expected_status'],
    [
        pytest.param(
            {
                'category_id': 'taxi',
                'service': 'safety-center',
                'yandex_uid': '12346',
                'state': 'deleted',
            },
            [
                ('12345', 'eats', 'deleting', 'takeout'),
                ('12345', 'grocery', 'deleted', 'grocery-service'),
                ('12345', 'taxi', 'deleting', 'user-api'),
                ('12346', 'grocery', 'deleted', 'grocery-service'),
            ],
            500,
        ),
        pytest.param(
            {
                'category_id': 'eats',
                'service': 'takeout',
                'yandex_uid': '12345',
                'state': 'deleted',
            },
            [
                ('12345', 'eats', 'deleted', 'takeout'),
                ('12345', 'grocery', 'deleted', 'grocery-service'),
                ('12345', 'taxi', 'deleting', 'user-api'),
                ('12346', 'grocery', 'deleted', 'grocery-service'),
            ],
            200,
        ),
        pytest.param(
            {
                'category_id': 'eats',
                'service': 'takeout',
                'yandex_uid': '12345',
                'state': 'delete_failed',
            },
            [
                ('12345', 'eats', 'delete_failed', 'takeout'),
                ('12345', 'grocery', 'deleted', 'grocery-service'),
                ('12345', 'taxi', 'deleting', 'user-api'),
                ('12346', 'grocery', 'deleted', 'grocery-service'),
            ],
            200,
        ),
        pytest.param(
            {
                'category_id': 'grocery',
                'service': 'grocery-service',
                'yandex_uid': '12345',
                'state': 'deleted',
            },
            [
                ('12345', 'eats', 'deleting', 'takeout'),
                ('12345', 'grocery', 'deleted', 'grocery-service'),
                ('12345', 'taxi', 'deleting', 'user-api'),
                ('12346', 'grocery', 'deleted', 'grocery-service'),
            ],
            200,
        ),
    ],
)
@pytest.mark.pgsql(
    'taxi_takeout', files=['pg_taxi_takeout_set_data_status.sql'],
)
async def test_takeout_set_data_status(
        web_app_client,
        pgsql,
        json_request,
        expected_deletions,
        expected_status,
):
    response = await web_app_client.post(
        '/takeout/set_data_status', json=json_request,
    )

    assert response.status == expected_status

    db = pgsql['taxi_takeout']
    cursor = db.cursor()
    cursor.execute(
        'SELECT yandex_uid, data_category, status, '
        'service_name FROM takeout.deletions '
        'ORDER BY (yandex_uid, data_category, status, service_name)',
    )
    deletions = list(cursor)
    assert deletions == expected_deletions
