import pytest


@pytest.mark.pgsql('fleet_rent', files=['init_db_data.sql'])
@pytest.mark.parametrize('record_or_serial', ['record_id', 'serial_id'])
@pytest.mark.parametrize(
    'id_of_record, expected_response', [(1, 'processing'), (2, 'available')],
)
async def test_debt_cancellation_status(
        web_app_client, record_or_serial, id_of_record, expected_response,
):
    if record_or_serial == 'record_id':
        selector = {'record_id': f'record_id{id_of_record}'}
    else:
        selector = {'serial_id': id_of_record}
    response1 = await web_app_client.get(
        '/v1/park/rents/external-debt-cancellation',
        params={'park_id': 'park_id', 'user_id': 'user', **selector},
    )
    assert response1.status == 200
    data = await response1.json()
    assert data['status'] == expected_response


@pytest.mark.pgsql('fleet_rent', files=['init_db_data.sql'])
@pytest.mark.parametrize('record_or_serial', ['record_id', 'serial_id'])
async def test_debt_cancellation_status_no_record(
        web_app_client, record_or_serial,
):
    if record_or_serial == 'record_id':
        selector = {'record_id': f'record_id3'}
    else:
        selector = {'serial_id': 3}
    response1 = await web_app_client.get(
        '/v1/park/rents/external-debt-cancellation',
        params={'park_id': 'park_id', 'user_id': 'user', **selector},
    )
    assert response1.status == 404


@pytest.mark.pgsql('fleet_rent', files=['init_db_data.sql'])
@pytest.mark.parametrize('record_or_serial', ['record_id', 'serial_id'])
@pytest.mark.parametrize('id_of_record', [1, 2])
async def test_debt_cancellation_start(
        web_app_client, record_or_serial, id_of_record, pgsql,
):
    if record_or_serial == 'record_id':
        selector = {'record_id': f'record_id{id_of_record}'}
    else:
        selector = {'serial_id': id_of_record}
    response = await web_app_client.post(
        '/v1/park/rents/external-debt-cancellation',
        params={'park_id': 'park_id', 'user_id': 'user', **selector},
    )
    assert response.status == 200

    with pgsql['fleet_rent'].cursor() as cursor:
        cursor.execute(
            f"""
        SELECT record_id, payment_doc_ids FROM rent.external_debt_cancellations
        WHERE record_id = 'record_id{id_of_record}'
        """,
        )
        if id_of_record == 2:
            expected = []
        else:
            expected = [15, 17, 18]
        assert [(f'record_id{id_of_record}', expected)] == list(cursor)


@pytest.mark.pgsql('fleet_rent', files=['init_db_data.sql'])
@pytest.mark.parametrize('id_of_record', [1, 2])
async def test_debt_cancellation_double_request(web_app_client, id_of_record):
    response = await web_app_client.post(
        '/v1/park/rents/external-debt-cancellation',
        params={
            'park_id': 'park_id',
            'user_id': 'user',
            'serial_id': id_of_record,
        },
    )
    assert response.status == 200

    response = await web_app_client.post(
        '/v1/park/rents/external-debt-cancellation',
        params={
            'park_id': 'park_id',
            'user_id': 'user',
            'serial_id': id_of_record,
        },
    )
    assert response.status == 200


@pytest.mark.pgsql('fleet_rent', files=['init_db_data.sql'])
async def test_debt_cancellation_start_second(web_app_client, pgsql):
    response = await web_app_client.post(
        '/v1/park/rents/external-debt-cancellation',
        params={'park_id': 'park_id', 'user_id': 'user', 'serial_id': 4},
    )
    assert response.status == 200

    with pgsql['fleet_rent'].cursor() as cursor:
        cursor.execute(
            f"""
        SELECT record_id, payment_doc_ids FROM rent.external_debt_cancellations
        WHERE record_id = 'record_id4' ORDER BY created_at ASC
        """,
        )
        expected = [('record_id4', [20, 21, 22]), ('record_id4', [])]
        assert expected == list(cursor)


@pytest.mark.pgsql('fleet_rent', files=['init_db_data.sql'])
@pytest.mark.parametrize('record_or_serial', ['record_id', 'serial_id'])
async def test_debt_cancellation_start_no_record(
        web_app_client, record_or_serial,
):
    if record_or_serial == 'record_id':
        selector = {'record_id': f'record_id3'}
    else:
        selector = {'serial_id': 3}
    response1 = await web_app_client.post(
        '/v1/park/rents/external-debt-cancellation',
        params={'park_id': 'park_id', 'user_id': 'user', **selector},
    )
    assert response1.status == 404
