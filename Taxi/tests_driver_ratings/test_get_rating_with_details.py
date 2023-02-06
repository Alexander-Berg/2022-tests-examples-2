import pytest


SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgcIgAgQ-YB7:Jl7sTExZFB0ap_5UUk6BhrFBYTphEwJIJBK'
    'c2YszfKX5QzoNmYqU1EtVvGoZMQZPJE4tHF0ODA0_4ozSk3PsJoTkRqSq6c843RWoYINNJg'
    'uT_bPGogM47VfOUw14ORrIEsLtJ5YRWvrAdy_hFNraNac1M08xl0ujuA8W5OIbrcY'
)


@pytest.mark.config(TVM_ENABLED=True)
async def test_driver_rating_get_ok(taxi_driver_ratings):
    response = await taxi_driver_ratings.get(
        '/v2/driver/rating/with-details',
        params={'unique_driver_id': 'unique_driver_id1'},
        headers={
            'X-Ya-Service-Ticket': SERVICE_TICKET,
            'X-Ya-Service-Name': 'test',
        },
    )
    assert response.status_code == 200, response.text
    assert response.json() == {
        'unique_driver_id': 'unique_driver_id1',
        'calc_at': '2019-01-01T10:00:00+00:00',
        'rating': '5.000',
        'previous_rating': '4.983',
        'used_scores_num': 175,
        'details': {
            'scores': [
                {
                    'scored_at': '2020-09-02T11:46:11+00:00',
                    'score': 5,
                    'weight': 1.0,
                },
                {
                    'scored_at': '2020-09-02T11:57:51+00:00',
                    'score': 4,
                    'weight': 2.0,
                },
            ],
        },
    }


@pytest.mark.config(TVM_ENABLED=False)
async def test_driver_rating_get_ok_no_tvm(taxi_driver_ratings):
    response = await taxi_driver_ratings.get(
        '/v2/driver/rating/with-details',
        params={'unique_driver_id': 'unique_driver_id1'},
        headers={
            'X-Ya-Service-Ticket': SERVICE_TICKET,
            'X-Ya-Service-Name': 'everything_is_valid',
        },
    )
    assert response.status_code == 200, response.text
    assert response.json() == {
        'unique_driver_id': 'unique_driver_id1',
        'calc_at': '2019-01-01T10:00:00+00:00',
        'rating': '5.000',
        'previous_rating': '4.983',
        'used_scores_num': 175,
        'details': {
            'scores': [
                {
                    'scored_at': '2020-09-02T11:46:11+00:00',
                    'score': 5,
                    'weight': 1.0,
                },
                {
                    'scored_at': '2020-09-02T11:57:51+00:00',
                    'score': 4,
                    'weight': 2.0,
                },
            ],
        },
    }


@pytest.mark.config(RATING_CALCULATION_PADDING_VALUE=4.5, TVM_ENABLED=True)
async def test_driver_rating_get_fallback(taxi_driver_ratings):
    response = await taxi_driver_ratings.get(
        '/v2/driver/rating/with-details',
        params={'unique_driver_id': 'not_found_id'},
        headers={
            'X-Ya-Service-Ticket': SERVICE_TICKET,
            'X-Ya-Service-Name': 'test',
        },
    )
    assert response.status_code == 200, response.text
    assert response.json() == {
        'unique_driver_id': 'not_found_id',
        'rating': '4.500',
    }


@pytest.mark.config(TVM_ENABLED=True)
async def test_invalid_service_name(taxi_driver_ratings):
    response = await taxi_driver_ratings.get(
        '/v2/driver/rating/with-details',
        params={'unique_driver_id': 'unique_driver_id1'},
        headers={
            'X-Ya-Service-Ticket': SERVICE_TICKET,
            'X-Ya-Service-Name': 'invalid-service-name',
        },
    )
    assert response.status_code == 403, response.text
