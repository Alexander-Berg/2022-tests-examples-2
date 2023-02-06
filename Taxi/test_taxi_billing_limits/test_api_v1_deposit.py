# pylint: disable=redefined-outer-name
import datetime
import decimal

import pytest


@pytest.fixture
def url():
    return '/v1/deposit'


@pytest.mark.pgsql(
    'billing_limits@0', files=['limits.limits.sql', 'limits.windows.sql'],
)
@pytest.mark.now('2019-08-08T18:00:00+00:00')
async def test_deposit_response(web_app_client, url, headers, load_json):
    request = load_json('request.json')
    response = await web_app_client.post(url, json=request, headers=headers)
    assert response.status == 200
    data = await response.json()
    assert data == load_json('response_ok.json')


@pytest.mark.pgsql(
    'billing_limits@0', files=['limits.limits.sql', 'limits.windows.sql'],
)
@pytest.mark.now('2019-08-08T18:00:00+00:00')
@pytest.mark.config(BILLING_LIMITS_PAYMENTS_BACKEND={'deposit': 'mirroring'})
async def test_deposit_saves_payment_to_db(
        web_app_client, url, headers, load_json, web_context, pgsql,
):
    # pylint: disable=unused-argument
    request = load_json('request.json')
    await web_app_client.post(url, json=request, headers=headers)
    with pgsql['billing_limits@0'].cursor() as cursor:
        cursor.execute('select * from payments.payments;')
        fields = [column.name for column in cursor.description]
        saved = [dict(zip(fields, row)) for row in cursor.fetchall()]
    assert saved == [
        {
            'ref': 'payment_ref',
            'limit_ref': 'tumbling',
            'event_at': datetime.datetime(
                2019, 8, 8, 17, 0, 0, tzinfo=datetime.timezone.utc,
            ),
            'amount': decimal.Decimal(10),
        },
    ]


@pytest.mark.pgsql(
    'billing_limits@0', files=['limits.limits.sql', 'limits.windows.sql'],
)
@pytest.mark.now('2019-08-08T18:00:00+00:00')
@pytest.mark.parametrize(
    'deposit_request_json, expected_payment_doc',
    (
        ('request.json', 'payment_doc.json'),
        ('request_for_account_id.json', 'payment_doc_for_account_id.json'),
    ),
)
async def test_deposit_creates_payment_doc(
        deposit_request_json,
        expected_payment_doc,
        web_app_client,
        url,
        headers,
        load_json,
        billing_docs,
):
    request = load_json(deposit_request_json)

    await web_app_client.post(url, json=request, headers=headers)
    assert load_json(expected_payment_doc) in billing_docs


@pytest.mark.pgsql(
    'billing_limits@0', files=['limits.limits.sql', 'limits.windows.sql'],
)
@pytest.mark.now('2019-08-08T18:00:00+00:00')
@pytest.mark.parametrize(
    'req,limit_ref',
    (('request.json', 'tumbling'), ('request_sliding.json', 'sliding')),
)
async def test_deposit_creates_task_for_checking(
        web_app_client, url, headers, load_json, stq, req, limit_ref,
):
    await web_app_client.post(url, json=load_json(req), headers=headers)
    task = stq.billing_limit_checker.next_call()
    assert task['queue'] == 'billing_limit_checker'
    assert task['args'] == [{'limit': {'ref': limit_ref}}]
    assert task['eta'].isoformat() == '2019-08-08T18:00:05'
    assert stq.is_empty


@pytest.mark.pgsql(
    'billing_limits@0', files=['limits.limits.sql', 'limits.windows.sql'],
)
@pytest.mark.now('2019-08-08T18:00:00+00:00')
async def test_deposit_post_twice(
        web_app_client, url, headers, load_json, billing_docs,
):
    request = load_json('request.json')
    _ = await web_app_client.post(url, json=request, headers=headers)
    response = await web_app_client.post(url, json=request, headers=headers)
    assert response.status == 200


@pytest.mark.pgsql(
    'billing_limits@0', files=['limits.limits.sql', 'limits.windows.sql'],
)
async def test_deposit_limit_not_found(
        web_app_client, url, headers, load_json,
):
    request = load_json('request_not_found.json')
    response = await web_app_client.post(url, json=request, headers=headers)
    assert response.status == 200
    assert await response.json() == load_json('response_not_found.json')


@pytest.mark.pgsql(
    'billing_limits@0', files=['limits.limits.sql', 'limits.windows.sql'],
)
async def test_deposit_invalid_currency(
        web_app_client, url, headers, load_json,
):
    request = load_json('request.json')
    request['currency'] = 'USD'
    response = await web_app_client.post(url, json=request, headers=headers)
    assert response.status == 400
    assert await response.json() == load_json('response_bad_request.json')


async def test_deposit_broken_payment(web_app_client, url, headers, load_json):
    request = load_json('request.json')
    request['event_at'] = 'garbage'
    response = await web_app_client.post(url, json=request, headers=headers)
    assert response.status == 400
    assert await response.json() == load_json(
        'response_bad_request_unexpected.json',
    )


@pytest.mark.pgsql(
    'billing_limits@0', files=['limits.limits.sql', 'limits.windows.sql'],
)
@pytest.mark.now('2020-02-02T19:00:00+00:00')
async def test_deposit_dry_payment(web_app_client, url, headers, load_json):
    request = load_json('request_dry.json')
    response = await web_app_client.post(url, json=request, headers=headers)
    assert response.status == 200
    data = await response.json()
    assert data == load_json('response_ok.json')


@pytest.mark.pgsql(
    'billing_limits@0', files=['limits.limits.sql', 'limits.windows.sql'],
)
@pytest.mark.now('2020-02-02T19:00:00+00:00')
async def test_deposit_dry_does_not_create_task_for_checking(
        web_app_client, url, headers, load_json, stq,
):
    request = load_json('request_dry.json')
    await web_app_client.post(url, json=request, headers=headers)
    assert stq.is_empty


@pytest.mark.pgsql(
    'billing_limits@0', files=['limits.limits.sql', 'limits.windows.sql'],
)
@pytest.mark.now('2020-02-02T19:00:00+00:00')
async def test_deposit_dry_use_dry_account(
        billing_docs, web_app_client, url, headers, load_json,
):
    request = load_json('request_dry.json')
    await web_app_client.post(url, json=request, headers=headers)
    assert billing_docs == [load_json('payment_doc_dry.json')]


@pytest.mark.now('2020-02-02T19:00:00+00:00')
@pytest.mark.pgsql('billing_limits@0', files=['discount.sql'])
async def test_deposit_ignores_wrong_currency_for_discount_limit(
        web_app_client, url, headers, load_json,
):
    request = load_json('request_discount_wrong_currency.json')
    response = await web_app_client.post(url, json=request, headers=headers)
    assert response.status == 200


@pytest.mark.now('2020-02-02T19:00:00+00:00')
async def test_deposit_ignores_absent_discount_limit(
        web_app_client, url, headers, load_json,
):
    request = load_json('request_discount_absent.json')
    response = await web_app_client.post(url, json=request, headers=headers)
    assert response.status == 200


@pytest.mark.now('2020-11-01T19:00:00+00:00')
@pytest.mark.pgsql(
    'billing_limits@0', files=['limits.limits.sql', 'limits.windows.sql'],
)
async def test_deposit_creates_account_when_not_found(
        web_app_client, url, headers, load_json, billing_accounts,
):
    request = load_json('request_no_account.json')
    response = await web_app_client.post(url, json=request, headers=headers)
    assert response.status == 200
    assert billing_accounts.entities_create.times_called == 1
    assert billing_accounts.accounts_create.times_called == 1


@pytest.fixture(scope='module', name='headers')
def make_headers():
    return {'X-Idempotency-Token': 'payment_ref'}
