def check_values(request, response):
    assert len(response.json()['pin']) == len(request['eta_formula'])
    assert len(response.json()['alt_pins']) == len(request['alt_pins'])

    request_pins = set(pin['class'] for pin in request['eta_formula'])
    response_pins = set(pin['class'] for pin in response.json()['pin'])
    assert len(request_pins.intersection(response_pins)) == len(
        request_pins.union(response_pins),
    )

    assert all(abs(pin['value']) <= 20 * 60 for pin in response.json()['pin'])


async def test_ml_eta_bulk_ok_without_candidates(taxi_umlaas, load_json):
    request = load_json('request_without_candidates.json')
    response = await taxi_umlaas.post('eta/v1', json=request)
    assert response.status_code == 200
    check_values(request, response)


async def test_ml_eta_bulk_ok_with_candidates(taxi_umlaas, load_json):
    request = load_json('request_with_candidates.json')
    response = await taxi_umlaas.post('eta/v1', json=request)
    assert response.status_code == 200
    check_values(request, response)


async def test_ml_eta_bad_request(taxi_umlaas, load_json):
    request = load_json('request_bad.json')
    response = await taxi_umlaas.post('eta/v1', json=request)
    assert response.status_code == 400
