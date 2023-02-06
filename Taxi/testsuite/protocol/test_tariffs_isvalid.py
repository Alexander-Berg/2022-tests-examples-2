SVO_POINT = [37.413673, 55.971204]

TEST_ROUTE = [
    {'p': [42.715358, 43.897531], 't': 3000000000},
    {'p': [42.714864, 43.896686], 't': 3000000000},
]


# tests based on data that could be found in
# backend-cpp/testsuite/tests/protocol/static/test_tariffs_isvalid

# moscow zone is mutialted: it has 1 inversed interval (25,5) so
# it should not be loaded into cache and should not be found
def test_invalid_tariff_is_not_loaded(taxi_protocol):
    request = {'zone_name': 'moscow'}
    response = taxi_protocol.post('3.0/zonaltariffdescription', request)
    assert response.status_code == 404


# almaty is OK and should be found in tariff's cache
def test_valid_tariff_is_loaded(taxi_protocol):
    request = {'zone_name': 'almaty'}
    response = taxi_protocol.post('3.0/zonaltariffdescription', request)
    assert response.status_code == 200
