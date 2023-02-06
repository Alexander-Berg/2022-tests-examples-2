import pytest

_REQUEST = {'passport_uid': 'passport_uid1', 'admin_type': 'tariff_editor'}
_AL_HANDLERS_CHECK = {
    'rules': [
        {
            'admin_type': 'tariff_editor',
            'enabled': True,
            'fields': [
                {'location': 'body', 'path': 'oid', 'pd_type': 'order_id'},
            ],
            'finalizer': {'type': 'finalizer1'},
            'name': 'rule1',
            'processors': [
                {'enabled': True, 'type': 'chatterbox_check_support_data'},
            ],
            'url': '/v1/user/check_fake',
        },
    ],
}


async def test_base(taxi_antileak, testpoint):
    @testpoint('al_rule_not_found')
    def _al_rule_not_found(_):
        pass

    resp = await taxi_antileak.post(
        '/v1/handler/personal_data/check', {**_REQUEST, **{'url': ''}},
    )

    assert resp.status_code == 200
    assert resp.json() == {'status': 'allow'}

    assert await _al_rule_not_found.wait_call()


@pytest.mark.parametrize(
    'req,found,exp_missing_paths,exp_missing_locations',
    [
        (
            {
                'body': {'a': {'b': {'user_phone': '+79161112233'}}},
                'query_args': {'q': {'w': {'license': 'lic1'}}},
                'url': '/v1/user/check_fake',
            },
            {'phone': '+79161112233', 'license': 'lic1'},
            ['a.b.c.license'],
            ['header'],
        ),
        (
            {
                'body': {'user_phone': '+79100000000'},
                'headers': {'b': {'license': 'lic2'}},
                'url': '/v2/order/112233/block/?a=b&c=d',
            },
            {'phone': '+79100000000'},
            ['p.license'],
            ['query_arg'],
        ),
        (
            {
                'body': {'user_phone': '+79100000000'},
                'headers': {'b': {'license': 'lic2'}},
                'url': '/v2/order/112233/block/?a=b&c=d',
                'admin_type': 'unknown',
            },
            None,
            [],
            [],
        ),
    ],
)
@pytest.mark.config(
    AL_HANDLERS_CHECK={
        'rules': [
            {
                'admin_type': 'tariff_editor',
                'enabled': True,
                'fields': [
                    {
                        'location': 'body',
                        'path': 'a.b.user_phone',
                        'pd_type': 'phone',
                    },
                    {
                        'location': 'body',
                        'path': 'a.b.c.license',
                        'pd_type': 'license',
                    },
                    {
                        'location': 'header',
                        'path': 'q.license',
                        'pd_type': 'license',
                    },
                    {
                        'location': 'query_arg',
                        'path': 'q.w.license',
                        'pd_type': 'license',
                    },
                ],
                'finalizer': {'type': 'finalizer1'},
                'name': 'rule1',
                'processors': [{'enabled': False, 'type': 'processor1'}],
                'url': '/v1/user/check_fake',
            },
            {
                'admin_type': 'tariff_editor',
                'enabled': True,
                'fields': [
                    {
                        'location': 'body',
                        'path': 'user_phone',
                        'pd_type': 'phone',
                    },
                    {
                        'location': 'header',
                        'path': 'p.license',
                        'pd_type': 'license',
                    },
                    {
                        'location': 'query_arg',
                        'path': 'arg1',
                        'pd_type': 'license',
                    },
                ],
                'finalizer': {'type': 'finalizer1'},
                'name': 'rule1',
                'processors': [{'enabled': False, 'type': 'processor1'}],
                'url': '^/v2/order/\\d+/block\\/?\\?[abcd=&]+',
            },
        ],
    },
)
async def test_fields_parsing(
        taxi_antileak,
        testpoint,
        req,
        found,
        exp_missing_paths,
        exp_missing_locations,
):
    missing_paths = []
    missing_locations = []

    @testpoint('al_pd_type_map_ready')
    def _al_pd_type_map_ready(data):
        if found is not None:
            assert found == data

    @testpoint('al_field_null_or_missing')
    def _al_field_null_or_missing(data):
        missing_paths.append(data['path'])

    @testpoint('al_handler_location_empty')
    def _al_handler_location_empty(data):
        missing_locations.append(data['location'])

    resp = await taxi_antileak.post(
        '/v1/handler/personal_data/check', {**_REQUEST, **req},
    )

    assert resp.status_code == 200
    assert resp.json() == {'status': 'allow'}

    if exp_missing_paths is not None:
        assert sorted(missing_paths) == sorted(exp_missing_paths)

    if exp_missing_locations is not None:
        assert sorted(missing_locations) == sorted(exp_missing_locations)

    if found is not None:
        assert await _al_pd_type_map_ready.wait_call()
    else:
        assert not _al_pd_type_map_ready.has_calls


@pytest.mark.parametrize(
    'order_id,status', [('good_order', 'allow'), ('bad_order', 'deny')],
)
@pytest.mark.config(AL_HANDLERS_CHECK=_AL_HANDLERS_CHECK)
async def test_chatterbox_processor_request_to_chatterbox(
        taxi_antileak, mockserver, order_id, status,
):
    @mockserver.json_handler('/chatterbox/v1/user/get_support_tasks_data')
    def _mock_chatterbox(req):
        assert req.json == {'login': 'login1', 'only_active': True}
        return {
            'data': [
                {
                    'task_id': 'task_id1',
                    'metadata': {'order_id': ['order_id1', 'order_id2']},
                },
                {
                    'task_id': 'task_id2',
                    'metadata': {
                        'order_id': [
                            'order_id3',
                            'order_id4',
                            'good_order',
                            'order_id5',
                        ],
                    },
                },
            ],
        }

    resp = await taxi_antileak.post(
        '/v1/handler/personal_data/check',
        {
            **_REQUEST,
            **{
                'url': '/v1/user/check_fake',
                'body': {'oid': order_id},
                'additional_params': {'login': 'login1'},
            },
        },
    )

    assert resp.status_code == 200
    assert resp.json() == {'status': status}

    assert await _mock_chatterbox.wait_call()


@pytest.mark.config(AL_HANDLERS_CHECK=_AL_HANDLERS_CHECK)
async def test_chatterbox_processor_missing_additional_params(taxi_antileak):
    resp = await taxi_antileak.post(
        '/v1/handler/personal_data/check',
        {
            **_REQUEST,
            **{'url': '/v1/user/check_fake', 'body': {'oid': 'order_id1'}},
        },
    )

    assert resp.status_code == 200
    assert resp.json() == {'status': 'deny'}


@pytest.mark.config(AL_HANDLERS_CHECK=_AL_HANDLERS_CHECK)
async def test_chatterbox_processor_missing_login(taxi_antileak):
    resp = await taxi_antileak.post(
        '/v1/handler/personal_data/check',
        {
            **_REQUEST,
            **{
                'url': '/v1/user/check_fake',
                'body': {'oid': 'order_id1'},
                'additional_params': {'param1': 'param2'},
            },
        },
    )

    assert resp.status_code == 200
    assert resp.json() == {'status': 'deny'}


@pytest.mark.config(AL_HANDLERS_CHECK=_AL_HANDLERS_CHECK)
async def test_chatterbox_processor_missing_order_id(taxi_antileak):
    resp = await taxi_antileak.post(
        '/v1/handler/personal_data/check',
        {
            **_REQUEST,
            **{
                'url': '/v1/user/check_fake',
                'body': {'license': 'license1'},
                'additional_params': {'login': 'login2'},
            },
        },
    )

    assert resp.status_code == 200
    assert resp.json() == {'status': 'allow'}
