import pytest


@pytest.mark.pgsql('classifier', files=['cars_first_order_date.sql'])
async def test_get_all(taxi_classifier):
    response = await taxi_classifier.post(
        '/v1/cars-first-order-date/updates', json={'limit': 100},
    )

    assert response.status_code == 200
    assert response.json() == {
        'car_number_cursor': '444DD61',
        'cars_first_order_date': [
            {
                'car_number': '111AA750',
                'first_order_date': '2017-12-27T00:00:00+00:00',
            },
            {
                'car_number': '222BB777',
                'first_order_date': '2018-12-27T00:00:00+00:00',
            },
            {
                'car_number': '333CC32',
                'first_order_date': '2019-12-27T00:00:00+00:00',
            },
            {
                'car_number': '444DD61',
                'first_order_date': '2020-12-27T00:00:00+00:00',
            },
        ],
        'limit': 100,
    }


@pytest.mark.pgsql('classifier', files=['cars_first_order_date.sql'])
async def test_limit_one(taxi_classifier):
    response = await taxi_classifier.post(
        '/v1/cars-first-order-date/updates', json={'limit': 1},
    )
    assert response.status_code == 200

    r_json = response.json()
    cars_first_order_date = r_json['cars_first_order_date']
    expected_first_sign = 1

    assert len(cars_first_order_date) == 1
    assert (
        int(cars_first_order_date[0]['car_number'][0]) == expected_first_sign
    )

    cursor = r_json['car_number_cursor']

    while len(cars_first_order_date) == 1:
        response = await taxi_classifier.post(
            '/v1/cars-first-order-date/updates',
            json={'limit': 1, 'car_number_cursor': cursor},
        )

        assert response.status_code == 200
        r_json = response.json()
        cars_first_order_date = r_json['cars_first_order_date']
        if not cars_first_order_date:
            break

        assert len(cars_first_order_date) == 1
        expected_first_sign += 1
        assert (
            int(cars_first_order_date[0]['car_number'][0])
            == expected_first_sign
        )
        cursor = r_json['car_number_cursor']
    assert expected_first_sign == 4
