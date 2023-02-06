import copy

import pytest


async def test_add_simple(pgsql, taxi_blocklist, predicate_request, headers):
    # remember predicate number
    cursor = pgsql['blocklist'].cursor()
    cursor.execute('SELECT * FROM blocklist.predicates')
    predicate_count = len(list(cursor))

    res = await taxi_blocklist.post(
        '/admin/blocklist/v1/predicates/add',
        json=predicate_request,
        headers=headers,
    )
    assert res.status_code == 200
    cursor = pgsql['blocklist'].cursor()
    cursor.execute('SELECT * FROM blocklist.predicates')
    assert len(list(cursor)) == predicate_count + 1


async def test_kwarg_keys_retrieving(
        pgsql, taxi_blocklist, predicate_request, headers,
):
    # check for correct filling of kwarg_keys column in blocklist.predicates
    request = copy.deepcopy(predicate_request)
    res = await taxi_blocklist.post(
        '/admin/blocklist/v1/predicates/add', json=request, headers=headers,
    )
    assert res.status_code == 200
    predicate_id = res.json()['predicate_id']
    cursor = pgsql['blocklist'].cursor()
    command = 'SELECT predicates.kwarg_keys FROM blocklist.predicates '
    command += f'WHERE predicates.id = \'{predicate_id}\''
    cursor.execute(command)
    kwarg_keys = list(cursor)[0][0]
    assert 'park_id' in kwarg_keys
    assert 'car_number' in kwarg_keys


# check predicate json value correctness
async def test_add_incorrect_value(
        pgsql, taxi_blocklist, predicate_request, headers,
):
    # remember predicate number
    cursor = pgsql['blocklist'].cursor()
    cursor.execute('SELECT * FROM blocklist.predicates')
    predicate_count = len(list(cursor))

    # check for unsupported predicate type
    request = copy.deepcopy(predicate_request)
    request['predicate']['value']['type'] = 'unsupported_predicate_type'
    res = await taxi_blocklist.post(
        '/admin/blocklist/v1/predicates/add', json=request, headers=headers,
    )
    assert res.status_code == 400
    assert res.json()['code'] == 'INCORRECT_PREDICATE_VALUE'

    # check for typy absence
    request = copy.deepcopy(predicate_request)
    del request['predicate']['value']['type']
    res = await taxi_blocklist.post(
        '/admin/blocklist/v1/predicates/add', json=request, headers=headers,
    )
    assert res.status_code == 400
    assert res.json()['code'] == 'INCORRECT_PREDICATE_VALUE'

    # check for value absence
    request = copy.deepcopy(predicate_request)
    del request['predicate']['value']['value']
    res = await taxi_blocklist.post(
        '/admin/blocklist/v1/predicates/add', json=request, headers=headers,
    )
    assert res.status_code == 400
    assert res.json()['code'] == 'INCORRECT_PREDICATE_VALUE'

    # check for predicates number changings
    cursor = pgsql['blocklist'].cursor()
    cursor.execute('SELECT * FROM blocklist.predicates')
    assert len(list(cursor)) == predicate_count


# check for kwargs matching
async def test_kwargs_mismatching(
        pgsql, taxi_blocklist, predicate_request, headers,
):
    # remember predicate number
    cursor = pgsql['blocklist'].cursor()
    cursor.execute('SELECT * FROM blocklist.predicates')
    predicate_count = len(list(cursor))

    # check for predicates number changings
    cursor = pgsql['blocklist'].cursor()
    cursor.execute('SELECT * FROM blocklist.predicates')
    assert len(list(cursor)) == predicate_count


# check for a new block addition after new predicate insertion
async def test_add_predicate_blocking(
        taxi_blocklist, predicate_request, add_request, headers,
):
    predicate_res = await taxi_blocklist.post(
        '/admin/blocklist/v1/predicates/add',
        json=predicate_request,
        headers=headers,
    )
    assert predicate_res.status_code == 200

    predicate_request['predicate_id'] = predicate_res.json()['predicate_id']
    add_res = await taxi_blocklist.post(
        '/admin/blocklist/v1/add', json=add_request, headers=headers,
    )
    assert add_res.status_code == 200


# check for the settings handle after new predicate insertion
@pytest.mark.usefixtures('predicate_request')
async def test_add_predicate_setting(
        taxi_blocklist, predicate_request, headers,
):
    # add new predicate
    predicate_res = await taxi_blocklist.post(
        '/admin/blocklist/v1/predicates/add',
        json=predicate_request,
        headers=headers,
    )
    assert predicate_res.status_code == 200
    predicate_id = predicate_res.json()['predicate_id']

    # get new predicate setting
    settings_res = await taxi_blocklist.get(
        '/admin/blocklist/v1/settings', headers={'Accept-Language': 'ru'},
    )
    assert settings_res.status_code == 200

    predicate_info = settings_res.json()['predicates'][-1]
    assert predicate_info['id'] == predicate_id
    assert {'code': 'park_id', 'name': 'park_id'} in predicate_info['kwargs']
    assert {'code': 'car_number', 'name': 'car_number'} in predicate_info[
        'kwargs'
    ]


# check for the internal predicate_get handle after new predicate insertion
@pytest.mark.usefixtures('predicate_request')
async def test_add_predicate_list(taxi_blocklist, predicate_request, headers):
    # add new predicate
    predicate_res = await taxi_blocklist.post(
        '/admin/blocklist/v1/predicates/add',
        json=predicate_request,
        headers=headers,
    )
    assert predicate_res.status_code == 200
    predicate_id = predicate_res.json()['predicate_id']

    # get predicates list
    predicates_res = await taxi_blocklist.get(
        '/internal/blocklist/v1/predicates', headers={'Accept-Language': 'ru'},
    )
    assert predicates_res.status_code == 200

    predicate_info = predicates_res.json()['predicates'][-1]
    assert predicate_info['predicate_id'] == predicate_id
    assert predicate_info['value'] == predicate_request['predicate']['value']
