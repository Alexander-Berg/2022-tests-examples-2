import pytest


SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgcIgAgQ-YB7:Jl7sTExZFB0ap_5UUk6BhrFBYTphEwJIJBK'
    'c2YszfKX5QzoNmYqU1EtVvGoZMQZPJE4tHF0ODA0_4ozSk3PsJoTkRqSq6c843RWoYINNJg'
    'uT_bPGogM47VfOUw14ORrIEsLtJ5YRWvrAdy_hFNraNac1M08xl0ujuA8W5OIbrcY'
)


@pytest.mark.config(RATING_CALCULATION_PADDING_VALUE=4.5, TVM_ENABLED=True)
async def test_driver_rating_batch_ok(taxi_driver_ratings):
    response = await taxi_driver_ratings.post(
        '/v2/driver/rating/batch-retrieve',
        json={
            'unique_driver_ids': [
                'unique_driver_id5',
                'unique_driver_id6',
                'unique_driver_id1',
                'unique_driver_id_round1',
                'unique_driver_id_round2',
            ],
        },
        headers={
            'X-Ya-Service-Ticket': SERVICE_TICKET,
            'X-Ya-Service-Name': 'test',
        },
    )
    assert response.status_code == 200, response.text
    assert response.json() == {
        'ratings': [
            {'rating': '5.000', 'unique_driver_id': 'unique_driver_id1'},
            {'rating': '4.500', 'unique_driver_id': 'unique_driver_id5'},
            {'rating': '4.500', 'unique_driver_id': 'unique_driver_id6'},
            {'rating': '4.444', 'unique_driver_id': 'unique_driver_id_round1'},
            {'rating': '4.999', 'unique_driver_id': 'unique_driver_id_round2'},
        ],
    }


@pytest.mark.config(RATING_CALCULATION_PADDING_VALUE=4.5, TVM_ENABLED=False)
async def test_driver_rating_batch_ok_no_tvm(taxi_driver_ratings):
    response = await taxi_driver_ratings.post(
        '/v2/driver/rating/batch-retrieve',
        json={
            'unique_driver_ids': [
                'unique_driver_id5',
                'unique_driver_id6',
                'unique_driver_id1',
                'unique_driver_id_round1',
                'unique_driver_id_round2',
            ],
        },
        headers={
            'X-Ya-Service-Ticket': SERVICE_TICKET,
            'X-Ya-Service-Name': 'everything_is_ok',
        },
    )
    assert response.status_code == 200, response.text
    assert response.json() == {
        'ratings': [
            {'rating': '5.000', 'unique_driver_id': 'unique_driver_id1'},
            {'rating': '4.500', 'unique_driver_id': 'unique_driver_id5'},
            {'rating': '4.500', 'unique_driver_id': 'unique_driver_id6'},
            {'rating': '4.444', 'unique_driver_id': 'unique_driver_id_round1'},
            {'rating': '4.999', 'unique_driver_id': 'unique_driver_id_round2'},
        ],
    }


@pytest.mark.config(TVM_ENABLED=True)
async def test_invalid_service_name(taxi_driver_ratings):
    response = await taxi_driver_ratings.post(
        '/v2/driver/rating/batch-retrieve',
        json={
            'unique_driver_ids': [
                'unique_driver_id1',
                'unique_driver_id5',
                'unique_driver_id6',
            ],
        },
        headers={
            'X-Ya-Service-Ticket': SERVICE_TICKET,
            'X-Ya-Service-Name': 'invalid-service',
        },
    )
    assert response.status_code == 403, response.text


@pytest.mark.config(RATING_CALCULATION_PADDING_VALUE=4.5, TVM_ENABLED=True)
async def test_driver_rating_batch_duplicate(taxi_driver_ratings):
    response = await taxi_driver_ratings.post(
        '/v2/driver/rating/batch-retrieve',
        json={
            'unique_driver_ids': [
                'unique_driver_id5',
                'unique_driver_id6',
                'unique_driver_id1',
                'unique_driver_id5',
            ],
        },
        headers={
            'X-Ya-Service-Ticket': SERVICE_TICKET,
            'X-Ya-Service-Name': 'test',
        },
    )
    assert response.status_code == 400, response.text
