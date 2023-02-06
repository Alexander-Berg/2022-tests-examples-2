# pylint: disable=redefined-outer-name
import uuid

import pytest


@pytest.fixture
def url():
    return '/v1/create'


async def test_create_response_with_required_only(
        web_app_client, url, load_json,
):
    request = load_json('request_minimal.json')
    response = await web_app_client.post(url, json=request)
    assert response.status == 200


@pytest.mark.parametrize(
    'limit_request_json, expected_response_json',
    [
        ('request.json', 'response_ok.json'),
        ('request_with_account_id.json', 'response_with_account_id.json'),
        (
            'request_with_notifications.json',
            'response_with_notifications.json',
        ),
        ('request_for_eats_stq.json', 'response_for_eats_stq.json'),
    ],
)
async def test_create_response(
        limit_request_json,
        expected_response_json,
        web_app_client,
        url,
        load_json,
):
    request = load_json(limit_request_json)
    response = await web_app_client.post(url, json=request)
    assert response.status == 200
    data = await response.json()
    assert data == load_json(expected_response_json)


async def test_create_inserts_new_limit(
        web_app_client, url, load_json, web_context, pgsql,
):
    request = load_json('request.json')
    await web_app_client.post(url, json=request)
    with pgsql['billing_limits@0'].cursor() as cursor:
        cursor.execute(
            'select count(*) from limits.limits where ref=\'limit_id\';',
        )
        assert cursor.fetchone()[0] == 1


async def test_create_twice_returns_200(web_app_client, url, load_json):
    request = load_json('request.json')
    await web_app_client.post(url, json=request)
    response = await web_app_client.post(url, json=request)
    assert response.status == 200


async def test_create_twice_inserts_once(
        web_app_client, url, load_json, pgsql,
):
    request = load_json('request.json')
    await web_app_client.post(url, json=request)
    await web_app_client.post(url, json=request)
    with pgsql['billing_limits@0'].cursor() as cursor:
        cursor.execute('select count(*) from limits.limits;')
        assert cursor.fetchone()[0] == 1
        cursor.execute('select count(*) from limits.windows;')
        assert cursor.fetchone()[0] == 2


async def test_create_generates_ref_if_absent(
        web_app_client, url, load_json, patch,
):
    @patch('taxi_billing_limits.generators.uuid.uuid4')
    def _uuid4():
        return uuid.UUID(int=0x0123456789ABCDEF)

    request = load_json('request.json')
    del request['ref']
    response = await web_app_client.post(url, json=request)
    assert response.status == 200
    data = await response.json()
    expected = load_json('response_ok.json')
    expected['ref'] = '00000000-0000-0000-0123-456789abcdef'
    expected['account_id'] = 'budget/' + expected['ref']
    assert data == expected


async def test_create_invalid_request(web_app_client, url, load_json):
    request = load_json('request_invalid.json')
    response = await web_app_client.post(url, json=request)
    assert response.status == 400
    data = await response.json()
    assert data == load_json('response_bad_request.json')
