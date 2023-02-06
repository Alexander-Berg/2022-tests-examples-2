import json

import pytest

from tests_geoareas import common


def setup_webhooks_mongo(mongodb, mockserver):
    urls_dicts = mongodb.geoareas_webhooks.find({}, {'url': 1})
    for url_dict in urls_dicts:
        url = url_dict['url']
        mongodb.geoareas_webhooks.update(
            {'url': url}, {'$set': {'url': mockserver.url(url)}},
        )


@pytest.mark.now('2020-02-02T02:02:02.000000Z')
@pytest.mark.parametrize(
    'request_json, expected_code, expected_db_json',
    [
        (
            'create_new_request.json',
            200,
            'expected_geoareas_webhooks_with_new.json',
        ),
        ('create_same_request.json', 409, 'db_geoareas_webhooks.json'),
    ],
)
async def test_create_webhook(
        taxi_geoareas,
        load_json,
        mongodb,
        bson_hook,
        request_json,
        expected_code,
        expected_db_json,
):
    req_body = load_json(request_json)
    res = await taxi_geoareas.put(
        '/admin/v1/subvention-geoareas/dependencies', req_body,
    )

    assert res.status_code == expected_code
    db_content = list(getattr(mongodb, 'geoareas_webhooks').find())
    expected_db_content = load_json(expected_db_json, object_hook=bson_hook)

    for db_webhook in db_content:
        del db_webhook['_id']
    assert db_content == common.deep_approx(expected_db_content)


@pytest.mark.now('2020-02-02T02:02:02.000000Z')
@pytest.mark.parametrize(
    'tvm_service_name, url, expected_code, expected_db_json',
    [
        ('billing-subventions-x', '/v1/subvention_geoarea/check', 200, None),
        (
            'dummy_not_existing_service',
            'dummy_not_existing_url',
            409,
            'db_geoareas_webhooks.json',
        ),
    ],
)
async def test_delete_webhook(
        taxi_geoareas,
        load_json,
        mongodb,
        bson_hook,
        tvm_service_name,
        url,
        expected_code,
        expected_db_json,
):
    res = await taxi_geoareas.delete(
        '/admin/v1/subvention-geoareas/dependencies',
        params={'tvm_service_name': tvm_service_name, 'url': url},
    )

    assert res.status_code == expected_code
    db_content = list(getattr(mongodb, 'geoareas_webhooks').find())

    expected_db_content = []
    if expected_db_json:
        expected_db_content = load_json(
            expected_db_json, object_hook=bson_hook,
        )

    for db_webhook in db_content:
        del db_webhook['_id']
    assert db_content == common.deep_approx(expected_db_content)


@pytest.mark.now('2020-02-02T02:02:02.000000Z')
@pytest.mark.filldb(subvention_geoareas='msk1')
@pytest.mark.parametrize(
    'geoarea_name, timestamp_from, timestamp_to, bsx_response_json,'
    'expected_code, expected_bsx_calls, expected_bsx_request_json,'
    'expected_response_json',
    [
        (
            'not_existing_geoarea',
            '2021-01-01T01:01:01.000000Z',
            '2021-01-01T01:01:01.000000Z',
            None,
            404,
            0,
            None,
            None,
        ),
        (
            'msk',
            '2021-01-01T01:01:01.000000Z',
            '2021-01-01T01:01:01.000000Z',
            'bsx_single_dependency_response.json',
            200,
            1,
            'expected_bsx_request_same.json',
            'expected_single_dependency_response.json',
        ),
        (
            'msk',
            '2021-01-01T01:01:01.000000Z',
            '2021-10-01T01:01:01.000000Z',
            'bsx_single_dependency_response.json',
            200,
            1,
            'expected_bsx_request_different.json',
            'expected_single_dependency_response.json',
        ),
        (
            'msk',
            '2021-01-01T01:01:01.000000Z',
            '2021-01-01T01:01:01.000000Z',
            'bsx_multiple_dependencies_response.json',
            200,
            1,
            'expected_bsx_request_same.json',
            'expected_multiple_dependencies_response.json',
        ),
        (
            'msk',
            '2021-01-01T01:01:01.000000Z',
            '2021-01-01T01:01:01.000000Z',
            'bsx_empty_dependencies_response.json',
            200,
            1,
            'expected_bsx_request_same.json',
            'expected_empty_dependencies_response.json',
        ),
    ],
)
async def test_check_dependencies(
        taxi_geoareas,
        mongodb,
        mockserver,
        load_json,
        bson_hook,
        geoarea_name,
        timestamp_from,
        timestamp_to,
        bsx_response_json,
        expected_code,
        expected_bsx_calls,
        expected_bsx_request_json,
        expected_response_json,
):
    @mockserver.json_handler('/v1/subvention_geoarea/check')
    async def _mock_bsx_check(request_json):
        _mock_bsx_check.calls += 1

        expected_request = load_json(expected_bsx_request_json)
        request = json.loads(request_json.get_data())
        assert request == expected_request

        response = load_json(bsx_response_json)
        return response

    _mock_bsx_check.calls = 0

    setup_webhooks_mongo(mongodb, mockserver)

    request = {
        'geoarea_name': geoarea_name,
        'timestamp_from': timestamp_from,
        'timestamp_to': timestamp_to,
    }
    res = await taxi_geoareas.post(
        '/admin/v1/subvention-geoareas/dependencies', request,
    )

    assert res.status_code == expected_code
    response = res.json()

    assert _mock_bsx_check.calls == expected_bsx_calls

    if expected_response_json:
        expected_response = load_json(
            expected_response_json, object_hook=bson_hook,
        )

        for dependency in expected_response['dependencies']:
            url = dependency['webhook_info']['url']

            dependency['webhook_info']['url'] = mockserver.url(url)

        assert response == common.deep_approx(expected_response)


def get_current_sg_names(mongodb):
    names = []
    docs = mongodb.subvention_geoareas.find(
        {'removed': {'$in': [None, False]}}, {'name': 1},
    )
    for doc in docs:
        names.append(doc['name'])

    return names


@pytest.mark.now('2020-02-02T02:02:02.000000Z')
@pytest.mark.filldb(subvention_geoareas='msk_spb')
@pytest.mark.parametrize(
    'horizon, expected_removed_names',
    [(90, ['msk', 'spb']), (365, ['spb']), (730, [])],
)
async def test_sg_cleanup_job(
        taxi_geoareas,
        taxi_config,
        mongodb,
        mockserver,
        horizon,
        expected_removed_names,
        load_json,
):
    taxi_config.set_values(
        dict(
            SG_CLEANUP_JOB_SETTINGS={
                'enabled': True,
                'period_hours': 30,
                'left_horizon_days': horizon,
                'right_horizon_days': horizon,
            },
        ),
    )

    @mockserver.json_handler('/v1/subvention_geoarea/check')
    async def _mock_bsx_check(request_json):
        _mock_bsx_check.calls += 1

        request = json.loads(request_json.get_data())
        response_json = (
            'bsx_' + request['name'] + '_' + str(horizon) + '_response.json'
        )
        print('response_json')
        print(response_json)

        response = load_json(response_json)
        return response

    _mock_bsx_check.calls = 0

    setup_webhooks_mongo(mongodb, mockserver)
    starting_names = get_current_sg_names(mongodb)

    await taxi_geoareas.run_distlock_task('clean-up-job')

    not_removed_names = get_current_sg_names(mongodb)
    removed_names = [
        name for name in starting_names if name not in not_removed_names
    ]

    removed_names.sort()
    expected_removed_names.sort()
    assert _mock_bsx_check.calls == 2
    assert removed_names == expected_removed_names


@pytest.mark.now('2020-02-02T02:02:02.000000Z')
@pytest.mark.filldb(subvention_geoareas='msk_spb')
@pytest.mark.filldb(geoareas_webhooks='empty')
@pytest.mark.parametrize(
    'horizon, expected_removed_names', [(90, []), (365, []), (730, [])],
)
async def test_sg_cleanup_job_empty_webhooks(
        taxi_geoareas,
        taxi_config,
        mongodb,
        mockserver,
        horizon,
        expected_removed_names,
        load_json,
):
    taxi_config.set_values(
        dict(
            SG_CLEANUP_JOB_SETTINGS={
                'enabled': True,
                'period_hours': 30,
                'left_horizon_days': horizon,
                'right_horizon_days': horizon,
            },
        ),
    )

    @mockserver.json_handler('/v1/subvention_geoarea/check')
    async def _mock_bsx_check(request_json):
        _mock_bsx_check.calls += 1

        request = json.loads(request_json.get_data())
        response_json = (
            'bsx_' + request['name'] + '_' + str(horizon) + '_response.json'
        )
        print('response_json')
        print(response_json)

        response = load_json(response_json)
        return response

    _mock_bsx_check.calls = 0

    setup_webhooks_mongo(mongodb, mockserver)
    starting_names = get_current_sg_names(mongodb)

    await taxi_geoareas.run_distlock_task('clean-up-job')

    not_removed_names = get_current_sg_names(mongodb)
    removed_names = [
        name for name in starting_names if name not in not_removed_names
    ]

    removed_names.sort()
    expected_removed_names.sort()
    assert _mock_bsx_check.calls == 0
    assert removed_names == expected_removed_names
