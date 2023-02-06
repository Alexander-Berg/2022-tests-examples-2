from tests_bank_topup import common


def get_headers():
    return {
        'X-Yandex-BUID': 'bank_uid',
        'X-Yandex-UID': 'uid',
        'X-YaBank-PhoneID': 'phone_id',
        'X-YaBank-SessionUUID': 'session_uuid',
        'X-Ya-User-Ticket': 'user_ticket',
    }


EXPECTED_PAYMENTS_STATUS = [
    ['aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa12', 'PROCESSING'],
    ['aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa11', 'PROCESSING'],
    ['aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa10', 'PROCESSING'],
    ['aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa04', 'PROCESSING'],
    ['aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa03', 'PROCESSING'],
    ['aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa02', 'PROCESSING'],
    ['aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa01', 'PROCESSING'],
]


async def test_ok(taxi_bank_topup):
    response = await taxi_bank_topup.post(
        '/v1/topup/v1/get_pending_payments/', headers=get_headers(), json={},
    )
    json = response.json()
    assert response.status_code == 200
    assert 'cursor' not in json
    assert (
        common.get_pending_payments_status(json['payments'])
        == EXPECTED_PAYMENTS_STATUS
    )
    assert all(
        payment['payment_info']['image'] == 'image_url'
        for payment in json['payments']
    )


async def test_pagination(taxi_bank_topup):
    response = await taxi_bank_topup.post(
        '/v1/topup/v1/get_pending_payments/', headers=get_headers(), json={},
    )
    full = response.json()['payments']
    assert len(full) == 7

    for page_size in range(1, 7):
        body = {'page_size': page_size}
        response = await taxi_bank_topup.post(
            '/v1/topup/v1/get_pending_payments/',
            headers=get_headers(),
            json=body,
        )
        assert response.status_code == 200
        page = response.json()['payments']
        cursor = (
            response.json()['cursor'] if 'cursor' in response.json() else None
        )
        assert (cursor and len(page) == page_size) or (
            not cursor and (len(page) < page_size)
        )
        paginated = page
        while cursor is not None:
            body = {'cursor': cursor}
            response = await taxi_bank_topup.post(
                '/v1/topup/v1/get_pending_payments/',
                headers=get_headers(),
                json=body,
            )
            assert response.status_code == 200
            page = response.json()['payments']
            cursor = (
                response.json()['cursor']
                if 'cursor' in response.json()
                else None
            )
            assert (cursor and len(page) == page_size) or (
                not cursor and (len(page) <= page_size)
            )
            paginated.extend(page)

        assert full == paginated


async def test_nothing(taxi_bank_topup):
    headers = get_headers()
    headers.update({'X-Yandex-BUID': 'unknown'})
    response = await taxi_bank_topup.post(
        '/v1/topup/v1/get_pending_payments/', headers=headers, json={},
    )
    json = response.json()
    assert response.status_code == 200
    assert not json['payments']
    assert 'cursor' not in json


async def test_no_succeeded_status(taxi_bank_topup):
    headers = get_headers()
    headers.update({'X-Yandex-BUID': 'bank_uid_succeeded'})
    response = await taxi_bank_topup.post(
        '/v1/topup/v1/get_pending_payments/', headers=headers, json={},
    )
    json = response.json()
    assert response.status_code == 200
    assert len(json['payments']) == 1
    assert json['payments'][0]['status'] == 'PROCESSING'
