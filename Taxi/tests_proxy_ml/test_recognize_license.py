import pytest


@pytest.fixture(name='ml_mock', autouse=True)
def _ml_mock(mockserver):
    @mockserver.json_handler('/pyml/parse_driver_license')
    def _parse_driver_license_handler(request):
        return {
            'first_name': {'confidence': 0.01585803584, 'value': 'Роман'},
            'country': 'rus',
            'birth_date': {'confidence': 0.4337495923, 'value': '1986-09-19'},
            'series': {'confidence': 0.8297998905, 'value': '2202'},
            'number': {'confidence': 0.8297998905, 'value': '813919'},
        }


@pytest.mark.config(PARSE_DRIVER_LICENSE_POLLING_DELAY=500)
async def test_recognize_license(
        taxi_proxy_ml, pgsql, mockserver, load_binary,
):
    data = load_binary('test_image.jpg')
    token = '1234567'
    country = 'RU'
    params = {'country': country, 'token': token}

    @mockserver.json_handler('/selfreg/validate_token')
    def _validate_token_handler(request):
        valid = False
        if request.json['token'] == token:
            valid = True
        return {'valid': valid}

    def select():
        cursor = pgsql['proxy_ml'].cursor()
        cursor.execute('SELECT * FROM driver_license_queue.requests')
        result = list(row for row in cursor)
        cursor.close()
        return result

    response = await taxi_proxy_ml.post(
        'selfreg/recognize_license',
        data=data,
        params=params,
        headers={'Content-Type': 'image/jpeg'},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert len(response_json) == 2
    assert response_json['polling_delay_ms'] == 500
    fetched_data = select()
    assert fetched_data[0][1] == token
    assert fetched_data[0][2] == 'rus'
    assert fetched_data[0][3].tobytes() == data
