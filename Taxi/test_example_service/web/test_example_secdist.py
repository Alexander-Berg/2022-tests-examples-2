import json


async def test_example_secdist(taxi_example_service_web, secdist_path):
    await _check_secdist(taxi_example_service_web, 'foo', '')
    await _update_secdist(taxi_example_service_web, secdist_path, 'foo', 'bar')
    await _check_secdist(taxi_example_service_web, 'foo', 'bar')
    await _update_secdist(taxi_example_service_web, secdist_path, 'foo', None)
    await _check_secdist(taxi_example_service_web, 'foo', '')


async def _check_secdist(taxi_example_service_web, key, value):
    response = await taxi_example_service_web.get(
        '/secdist/example', params={'key': key},
    )
    assert response.status == 200
    data = await response.text()
    assert data == value


async def _update_secdist(taxi_example_service_web, secdist_path, key, value):
    with open(secdist_path) as secdist_file:
        secdist = json.load(secdist_file)
    if value is not None:
        secdist[key] = value
    else:
        secdist.pop(key, None)
    with open(secdist_path, 'w') as secdist_file:
        json.dump(secdist, secdist_file)
    await taxi_example_service_web.tests_control(invalidate_caches=True)
