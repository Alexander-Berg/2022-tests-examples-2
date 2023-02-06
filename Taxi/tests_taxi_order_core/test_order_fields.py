import pytest


ORDER_ID = '71e78aa6276c38c08f12def2af04799e'
ALIAS_ID = 'cdf9d0ded62a3c93a58a6ef084c00e2f'
REORDER_ID = '82e78aa6276c38c08f12def2af04790f'
USER_ID = 'c066912d9e6410fe516c4af3f948a882'
BAD_USER_ID = 'd166912d9e6410fe516c4af3f948a893'

MOCK_TICKET = (
    '3:serv:CBAQ__________9_IgYIbxDWuwM:OwG'
    'nMpS24mNzXDygjrgc-UeSpAmmVXaDl5v8GY_OS'
    'Oo0UpdtomG4fLG5zM0E3l0H02d0NJ_KSmR8Gwz'
    '12Nrsad-iv9YWO7mIm_RLoVbWYNSRRQ02123-7'
    'vZXNcnLK6ZGNEe-PSvuglO2RIIaLUSgOcSDVDp'
    'ASuCL3AcwkyT5lpk'
)


@pytest.mark.parametrize(
    'order_id,lookup_flags',
    [
        (ORDER_ID, 'none'),
        (ALIAS_ID, 'allow_alias'),
        (REORDER_ID, 'allow_reorder'),
    ],
)
async def test_order_fields_request_id(
        taxi_order_core, mongodb, order_id, lookup_flags,
):
    request_params = {'fields': ['_id']}
    request_params['order_id'] = order_id
    request_params['lookup_flags'] = lookup_flags
    response = await taxi_order_core.post(
        '/v1/tc/order-fields', json=request_params,
    )
    assert response.status_code == 200
    response = response.json()
    assert response['order_id'] == ORDER_ID


@pytest.mark.parametrize(
    'fields,status',
    [
        (['_id'], 200),
        (['order.user_ready'], 200),
        ([], 400),
        (['order'], 400),
        (['order.experiments'], 400),
        (['order.user_experiments'], 400),
        (['candidates'], 400),
        (['candidates.driver_experiments'], 400),
    ],
)
async def test_order_fields_request_fields(
        taxi_order_core, taxi_config, mongodb, fields, status,
):
    taxi_config.set_values(
        {
            'ORDER_CORE_PROHIBITED_FIELDS': [
                'order.experiments',
                'order.user_experiments',
                'candidates.driver_experiments',
            ],
        },
    )
    request_params = {'order_id': ORDER_ID, 'fields': fields}
    response = await taxi_order_core.post(
        '/v1/tc/order-fields', json=request_params,
    )
    assert response.status_code == status


@pytest.mark.parametrize(
    'require_latest,search_archive,replica,status',
    [
        (False, False, 'secondary', 200),
        (False, True, 'secondary', 200),
        (True, False, 'master', 200),
        (True, True, '', 400),
    ],
)
async def test_order_fields_latest_vs_archive(
        taxi_order_core,
        mongodb,
        require_latest,
        search_archive,
        replica,
        status,
):
    request_params = {
        'order_id': ORDER_ID,
        'fields': ['_id'],
        'require_latest': require_latest,
        'search_archive': search_archive,
    }
    response = await taxi_order_core.post(
        '/v1/tc/order-fields', json=request_params,
    )
    assert response.status_code == status
    response = response.json()
    if status != 400:
        assert response['replica'] == replica


@pytest.mark.parametrize(
    'user_id,status', [(USER_ID, 200), (BAD_USER_ID, 404)],
)
async def test_order_fields_user_id(taxi_order_core, mongodb, user_id, status):
    request_params = {
        'order_id': ORDER_ID,
        'fields': ['_id'],
        'user_id': user_id,
    }
    response = await taxi_order_core.post(
        '/v1/tc/order-fields', json=request_params,
    )
    assert response.status_code == status


async def test_order_fields_basic(taxi_order_core, mongodb):
    fields = [
        'commit_state',
        'created',
        'lookup.state.wave',
        'lookup.params',
        'candidates.subvention_geoareas.name',
        'lookup.nonexistent_field',
    ]
    request_params = {'order_id': ORDER_ID, 'fields': fields}
    response = await taxi_order_core.post(
        '/v1/tc/order-fields', json=request_params,
    )
    assert response.status_code == 200
    response = response.json()
    assert response == {
        'fields': {
            '_id': '71e78aa6276c38c08f12def2af04799e',
            'candidates': [
                {
                    'subvention_geoareas': [
                        {'name': 'msk-polygon-5'},
                        {'name': 'msk-polyinpoly-test'},
                        {'name': 'moscow_center'},
                        {'name': 'msk-iter2-polygon-5'},
                        {'name': 'msk-iter3-polygon5'},
                        {'name': 'paveletskaya'},
                        {'name': 'msk-tlbr'},
                        {'name': 'msk-iter1-polygon-test'},
                    ],
                },
            ],
            'commit_state': 'done',
            'created': '2020-01-24T14:06:55.077+00:00',
            'lookup': {'params': {}, 'state': {'wave': 2}},
        },
        'order_id': '71e78aa6276c38c08f12def2af04799e',
        'replica': 'secondary',
        'version': 'DAAAAAAABgAMAAQABgAAAKmG6NdvAQAA',
    }


@pytest.mark.parametrize(
    'version, fetch_result_tag, mongo_requests_count',
    [
        (None, 'ok', 1),
        ('blah', 'ok', 1),
        # version taken from order_proc
        ('DAAAAAAABgAMAAQABgAAAKmG6NdvAQAA', 'ok', 1),
        # version taken from prod for 2019-01-29
        ('DAAAAAAABgAMAAQABgAAALbeUvJvAQAA', 'laggy_secondary', 2),
    ],
)
async def test_order_fields_secondary(
        taxi_order_core,
        testpoint,
        version,
        fetch_result_tag,
        mongo_requests_count,
):
    @testpoint('fetch-fields-result')
    def _testpoint_fetch_result(data):
        assert data == fetch_result_tag

    @testpoint('fetch-fields')
    def testpoint_mongo_call(data):
        pass

    params = {'order_id': ORDER_ID, 'fields': ['_id']}
    if version is not None:
        params['version'] = version
    result = await taxi_order_core.post('/v1/tc/order-fields', json=params)
    assert result.status_code == 200
    assert testpoint_mongo_call.times_called == mongo_requests_count


@pytest.mark.config(TVM_ENABLED=True)
async def test_order_fields_archive(taxi_order_core, archive):
    archive_order_patch = {'_id': 'default_order_id'}
    archive.set_order_proc_patches([archive_order_patch])

    headers = {'X-Ya-Service-Ticket': MOCK_TICKET}
    params = {
        'order_id': 'default_order_id',
        'fields': ['_id'],
        'search_archive': True,
    }
    response = await taxi_order_core.post(
        '/v1/tc/order-fields', json=params, headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == {
        'fields': {
            '_id': 'default_order_id',
            'order': {
                '_id': 'default_order_id',
                'excluded_parks': [],
                'experiments': [],
                'nz': 'moscow',
                'request': {
                    'class': ['econom'],
                    'destinations': [{'geopoint': [33.333333, 44.444444]}],
                    'due': '2019-03-18T00:00:00+00:00',
                    'payment': {'payment_method_id': None, 'type': 'cash'},
                    'requirements': {
                        'animaltransport': True,
                        'capacity': [1],
                        'cargo_loaders': [1, 1],
                        'childchair_moscow': 7,
                        'creditcard': True,
                        'passengers_count': 1,
                    },
                    'source': {'geopoint': [11.111111, 22.222222]},
                },
                'status': 'pending',
                'user_id': 'default_user_id',
            },
            'updated': '2019-01-29T00:00:00+00:00',
        },
        'order_id': 'default_order_id',
        'replica': 'archive',
        'version': 'DAAAAAAABgAMAAQABgAAAADM55ZoAQAA',
    }
