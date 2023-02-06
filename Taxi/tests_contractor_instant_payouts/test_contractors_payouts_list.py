PAYOUT1 = {
    'id': '00000000-0001-0001-0001-000000000000',
    'created_at': '2020-01-01T12:00:00+00:00',
    'amount': '100.01',
    'status': 'succeeded',
}

PAYOUT2 = {
    'id': '00000000-0001-0001-0002-000000000000',
    'created_at': '2020-01-02T12:00:00+00:00',
    'amount': '200.02',
    'status': 'failed',
}

PAYOUT3 = {
    'id': '00000000-0001-0001-0003-000000000000',
    'created_at': '2020-01-03T12:00:00+00:00',
    'amount': '300.03',
    'status': 'in_progress',
}


async def test_default(contractors_payouts_list):
    response = await contractors_payouts_list()
    assert response.status_code == 200, response.text
    assert response.json() == {'payouts': [PAYOUT3, PAYOUT2, PAYOUT1]}


async def test_another_park(contractors_payouts_list):
    response = await contractors_payouts_list(
        park_id='48b7b5d81559460fb1766938f94009c2',
    )
    assert response.status_code == 200, response.text
    assert response.json() == {'payouts': []}


async def test_another_contractor(contractors_payouts_list):
    response = await contractors_payouts_list(
        contractor_id='48b7b5d81559460fb176693800000002',
    )
    assert response.status_code == 200, response.text
    assert response.json() == {'payouts': []}


async def test_cursor_limit1(contractors_payouts_list):
    response = await contractors_payouts_list(limit=1)
    assert response.status_code == 200, response.text
    json = response.json()
    assert json['payouts'] == [PAYOUT3]
    assert 'next_cursor' in json
    cursor = json['next_cursor']

    response = await contractors_payouts_list(limit=1, cursor=cursor)
    assert response.status_code == 200, response.text
    json = response.json()
    assert json['payouts'] == [PAYOUT2]
    assert 'next_cursor' in json
    cursor = json['next_cursor']

    response = await contractors_payouts_list(limit=1, cursor=cursor)
    assert response.status_code == 200, response.text
    json = response.json()
    assert json['payouts'] == [PAYOUT1]
    assert 'next_cursor' not in json


async def test_cursor_limit2(contractors_payouts_list):
    response = await contractors_payouts_list(limit=2)
    assert response.status_code == 200, response.text
    json = response.json()
    assert json['payouts'] == [PAYOUT3, PAYOUT2]
    assert 'next_cursor' in json
    cursor = json['next_cursor']

    response = await contractors_payouts_list(limit=2, cursor=cursor)
    assert response.status_code == 200, response.text
    json = response.json()
    assert json['payouts'] == [PAYOUT1]
    assert 'next_cursor' not in json
