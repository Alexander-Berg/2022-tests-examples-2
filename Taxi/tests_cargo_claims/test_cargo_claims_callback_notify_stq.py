import datetime

import pytest

TIMESTAMP_FORMAT = '%Y-%m-%dT%H:%M:%SZ'


@pytest.fixture(name='mock_callback_request')
def _mock_callback_request(mockserver):
    def mock(claim_id, updated_ts, headers=None):
        @mockserver.handler('/foobar')
        def _mock_callback_request_send(request, *args, **kwargs):
            if headers:
                for key in headers:
                    assert key in request.headers
                    assert request.headers[key] == headers[key]

            assert request.json == {
                'claim_id': claim_id,
                'updated_ts': updated_ts.replace('Z', '+00:00'),
            }

            return mockserver.make_response('{}', status=204)

        return _mock_callback_request_send

    return mock


async def test_stq(
        stq_runner, mock_callback_request, mockserver, claim_creator,
):
    response = await claim_creator()
    assert response.status_code == 200
    claim_id = response.json()['id']

    now = datetime.datetime.utcnow().strftime(format=TIMESTAMP_FORMAT)
    mock_callback = mock_callback_request(claim_id, now)
    await stq_runner.cargo_claims_callback_notify.call(
        task_id='task_id',
        args=[mockserver.url('/foobar'), claim_id, {'$date': now}],
        expect_fail=False,
    )
    assert mock_callback.times_called == 1
    await mock_callback.wait_call()


@pytest.mark.config(
    CARGO_CLAIMS_CALLBACK_NOTIFY={
        'timeout_ms': 1000,
        'retries': 2,
        'task_ttl_in_minutes': 59,
    },
)
async def test_task_ttl_limit(
        stq_runner, mock_callback_request, mockserver, claim_creator,
):
    response = await claim_creator()
    assert response.status_code == 200
    claim_id = response.json()['id']

    now_without_hour = (
        datetime.datetime.utcnow() - datetime.timedelta(hours=1)
    ).strftime(format=TIMESTAMP_FORMAT)
    mock = mock_callback_request(claim_id, now_without_hour)
    await stq_runner.cargo_claims_callback_notify.call(
        task_id='task_id',
        args=[
            mockserver.url('/foobar'),
            claim_id,
            {'$date': now_without_hour},
        ],
        expect_fail=False,
    )
    assert mock.times_called == 0


@pytest.mark.parametrize(
    'corp_client_id, expected_headers',
    [
        (
            '01234567890123456789012345678912',
            {'key_1': 'value 1', 'key_2': 'value 2'},
        ),
        ('43210567890123456789012345678912', {'key_1': 'value 1'}),
        ('54321567890123456789012345678912', {}),
    ],
)
async def test_extra_headers_by_corp(
        taxi_cargo_claims,
        claim_creator,
        get_default_headers,
        mock_callback_request,
        stq_runner,
        mockserver,
        corp_client_id: str,
        expected_headers: dict,
):
    request_headers = get_default_headers(corp_client_id)

    response = await claim_creator(headers=request_headers)
    assert response.status_code == 200

    claim_id = response.json()['id']

    now = datetime.datetime.utcnow().strftime(TIMESTAMP_FORMAT)
    mock = mock_callback_request(claim_id, now, headers=expected_headers)

    await stq_runner.cargo_claims_callback_notify.call(
        task_id='task_id',
        args=[mockserver.url('/foobar'), claim_id, {'$date': now}],
        expect_fail=False,
    )
    assert mock.times_called == 1
    await mock.wait_call()
