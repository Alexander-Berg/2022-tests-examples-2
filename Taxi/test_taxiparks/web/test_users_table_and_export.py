import pytest
import csv
import io

ROUTE_EXPORT = '/users/export'
ROUTE_SHOW = '/users_dyn'
PASSPORT_USER_FIELDS_ALLOWED = [
    'personal_yandex_login_id',
    'is_passport_user',
    'awaits_activation',
]
FIELDS_DISALLOWED = ['yandex_login']


@pytest.fixture
def parse_requests(load_json):
    return load_json('requests.json')


@pytest.fixture
def parse_request(parse_requests):
    all_requests_data = parse_requests
    default = all_requests_data['default']
    def func(request_name=None):
        data = dict(**default)
        data.update(all_requests_data[request_name])
        requst_data = data['request']
        status_code = data['status_code']
        return requst_data, status_code
    return func


def parse_csv_str(string):
    si = io.StringIO(string)
    reader = csv.DictReader(si, delimiter=';')
    return [dict(row) for row in reader]


@pytest.mark.usefixtures('log_in')
def test_users_export(
        taxiparks_client,
        csrf_token_session,
        parse_requests,
        parse_request
):
    all_requests = parse_requests
    for request_name in all_requests:
        request_data, status_code = parse_request(request_name)
        request_data['csrf_token'] = csrf_token_session()
        response = taxiparks_client.post(
            ROUTE_EXPORT,
            json=request_data,
        )

        assert response.status_code == status_code
        if response.status_code != 200:
            return


def test_users_export_count(
        taxiparks_client,
        csrf_token_session,
        parse_request
):
    request_data, status_code = parse_request('request_2')
    request_data['csrf_token'] = csrf_token_session()
    response = taxiparks_client.post(
        ROUTE_EXPORT,
        json=request_data,
    )
    csv_data = response.data.decode('utf8')
    data = parse_csv_str(csv_data)

    resp_count = len(data)
    request_data.pop('count')
    request_data['csrf_token'] = csrf_token_session()
    response = taxiparks_client.post(
        ROUTE_EXPORT,
        json=request_data,
    )
    csv_data = response.data.decode('utf8')
    data = parse_csv_str(csv_data)

    assert len(data) == resp_count


@pytest.mark.usefixtures('log_in')
def test_users_table(
        taxiparks_client,
        parse_requests,
        parse_request
):
    all_requests = parse_requests
    for request_name in all_requests:
        request_data, status_code = parse_request(request_name)
        response = taxiparks_client.get(
            ROUTE_SHOW,
            query_string=request_data,
        )

        assert response.status_code == status_code
        if response.status_code != 200:
            return
        data = response.json['data']
        assert len(data) <= request_data.get('count', 30)
        fields = set(key for user in data for key in user)
        for field in PASSPORT_USER_FIELDS_ALLOWED:
            assert field in fields
        for field in FIELDS_DISALLOWED:
            assert field not in fields
