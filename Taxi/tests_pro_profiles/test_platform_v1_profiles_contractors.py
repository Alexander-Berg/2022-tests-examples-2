import pytest

# Generated via `tvmknife unittest service -s 111 -d 2345`
MOCK_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgUIbxCpEg:Ra-ZL'
    'U9qXIBFfH0vUxQNVJYpEC5DXkfCtKQleLpMjjPJq'
    'DoDtKB8lZPrxvA-MVMUH2IjFAqw1M_-ezidnX20O'
    'LPuQVoD-0ZHd6viUaEGmgkk41d5akfgDZMW_avuV'
    'dnFsdYEMpbkTUsRx_1b0chDe9wEju9xOW8RJ3lVpDAEMdk'
)

# Generated via `tvmknife unittest service -s 2345 -d 2345`
OWN_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgYIqRIQqRI:Imidx'
    'JYTfEcSgxUEGJR1uyz3fGO9kDO6GVZUorMSHaaWQf'
    '7VtZev3yEEFQKuoqvENz2qrX9V5xRftUtKXVBLh2y'
    'QloNlybvfyq_hQaB7d8wprge0hRKuaOOcv5wa50MG'
    'CNBb40zc5idx5dCIHYOhoR8JxaMlqpfR-qdK5d78Qp0'
)

HEADERS = {
    'X-Idempotency-Token': 'some_unique_string',
    'X-Platform-Consumer': 'market',
    'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET,
}


@pytest.fixture(name='driver_profiles')
def _driver_profiles(mockserver):
    class Context:
        def __init__(self):
            self.provider = None
            self.error = None
            self.work_status = ''

        def set_provider(self, provider):
            self.provider = provider

        def set_error(self, status, code, text):
            self.error = {'status': status, 'code': code, 'text': text}

    context = Context()

    @mockserver.json_handler('/driver-profiles/v2/profile/orders-provider')
    def _orders_provider(request):
        if context.error:
            return mockserver.make_response(
                status=context.error['status'],
                json={
                    'code': context.error['code'],
                    'message': context.error['text'],
                },
            )
        if context.provider:
            assert request.json['orders_providers'] == [context.provider]
        return {}

    setattr(context, 'orders_provider', _orders_provider)
    return context


@pytest.fixture(name='parks')
def _parks(mockserver):
    class Context:
        def __init__(self):
            self.create_error = None
            self.update_error = None
            self.work_status: str = None

        def set_create_error(self, status, code, text):
            self.create_error = {'status': status, 'code': code, 'text': text}

        def set_update_error(self, status, code, text):
            self.update_error = {'status': status, 'code': code, 'text': text}

        def set_work_status(self, work_status: str):
            self.work_status = work_status

    context = Context()

    @mockserver.json_handler('/parks/internal/driver-profiles/create')
    def _create(request):
        if context.create_error:
            return mockserver.make_response(
                status=context.create_error['status'],
                json={
                    'error': {
                        'code': context.create_error['code'],
                        'text': context.create_error['text'],
                    },
                },
            )
        return {
            'driver_profile': {
                'id': 'driver-profile-id',
                'park_id': 'park-id',
                'first_name': 'First',
                'last_name': 'Last',
                'phones': ['+70006660001'],
                'hire_date': '2022-01-04T00:00:00+0000',
                'providers': [],
                'work_status': 'working',
            },
        }

    @mockserver.json_handler('/parks/internal/driver-profiles/personal')
    def _personal(request):
        if context.update_error:
            return mockserver.make_response(
                status=context.update_error['status'],
                json={
                    'error': {
                        'code': context.update_error['code'],
                        'text': context.update_error['text'],
                    },
                },
            )
        return {
            'driver_profile': {
                'id': 'driver-profile-id',
                'park_id': 'park-id',
                'first_name': 'First',
                'last_name': 'Last',
                'phones': ['+70006660001'],
            },
        }

    @mockserver.json_handler('/parks/internal/driver-profiles/profile')
    def _profile(request):
        assert (
            request.json['driver_profile']['set']['work_status']
            == context.work_status
        )
        return {
            'driver_profile': {
                'id': 'driver-profile-id',
                'park_id': 'park-id',
                'work_status': context.work_status,
            },
        }

    setattr(context, 'create', _create)
    setattr(context, 'personal', _personal)
    setattr(context, 'profile', _profile)
    return context


@pytest.fixture(name='tags')
def _tags(mockserver):
    class Context:
        def __init__(self):
            self.tags = {}
            self.error = None

        def add_tags(self, dbid_uuid, tags):
            self.tags[dbid_uuid] = tags

        def set_error(self, status: int):
            self.error = {'status': status}

    context = Context()

    @mockserver.json_handler('/tags/v1/assign')
    def _assign(request):
        if context.error:
            return mockserver.make_response(
                status=context.error['status'], json={},
            )
        if context.tags:
            tags = [
                {'name': dbid_uuid, 'type': 'dbid_uuid', 'tags': tags}
                for dbid_uuid, tags in context.tags.items()
            ]
            assert tags == request.json['entities']
        return {}

    setattr(context, 'assign', _assign)
    return context


def _build_tvm_settings():
    return dict(
        TVM_ENABLED=True,
        TVM_RULES=[{'src': 'developers', 'dst': 'pro-profiles'}],
        TVM_SERVICES={
            'pro-profiles': 2345,
            'developers': 111,
            'taxi_exp': 112,
            'experiments3-proxy': 113,
            'statistics': 114,
            'contractor-transport': 115,
            'driver-authorizer': 116,
            'driver-profiles': 117,
            'driver-tags': 118,
            'parks': 119,
            'selfreg': 120,
            'tags': 121,
            'personal': 122,
        },
    )


def _build_config3(external_consumer, name, value):
    return dict(
        name=f'pro-profiles-contractors-{external_consumer}-{name}',
        consumers=['pro-profiles-contractors'],
        default_value={name: value},
        is_config=True,
    )


@pytest.mark.config(**_build_tvm_settings())
@pytest.mark.tvm2_ticket(
    {2013636: MOCK_SERVICE_TICKET, 2345: OWN_SERVICE_TICKET},
)
@pytest.mark.experiments3(**_build_config3('market', 'provider', 'market'))
@pytest.mark.experiments3(**_build_config3('market', 'park', 'park-id'))
@pytest.mark.experiments3(
    **_build_config3(
        'market', 'tags', ['market_profile', 'market_magistrali'],
    ),
)
async def test_create_market_profile(taxi_pro_profiles, parks, tags):
    tags.add_tags(
        'park-id_driver-profile-id',
        {'market_profile': {}, 'market_magistrali': {}},
    )
    response = await taxi_pro_profiles.post(
        '/platform/v1/profiles/contractors/v1',
        headers=HEADERS,
        json={
            'contractor': {
                'phone': 'phone',
                'details': {
                    'external_id': 'external_id',
                    'profession': 'test_profession',
                },
                'full_name': {
                    'first_name': 'first_name',
                    'last_name': 'last_name',
                    'middle_name': 'patronymic',
                },
            },
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'partner_id': 'park-id',
        'profile_id': 'driver-profile-id',
    }

    assert tags.assign.times_called == 1
    assert parks.create.times_called == 1
    assert parks.personal.times_called == 0


@pytest.mark.config(**_build_tvm_settings())
@pytest.mark.tvm2_ticket(
    {2013636: MOCK_SERVICE_TICKET, 2345: OWN_SERVICE_TICKET},
)
@pytest.mark.experiments3(**_build_config3('market', 'provider', 'market'))
@pytest.mark.experiments3(**_build_config3('market', 'park', 'park-id'))
@pytest.mark.experiments3(
    **_build_config3(
        'market', 'tags', ['market_profile', 'market_magistrali'],
    ),
)
@pytest.mark.parametrize(
    'status, error_code, error_message',
    [
        (400, 'duplicate_phone', 'Duplicate phone'),
        (401, 'duplicate_driver_license', 'Duplicate Driver License'),
        (403, 'duplicate_employee_number', 'Duplicate Employee Number'),
        (500, 'invalid_driver_license', 'Invalid Driver License'),
    ],
)
async def test_create_market_profile_parks_fail(
        load_json,
        taxi_pro_profiles,
        parks,
        tags,
        status,
        error_code,
        error_message,
):
    tags.add_tags(
        'park-id_driver-profile-id',
        {'market_profile': {}, 'market_magistrali': {}},
    )
    parks.set_create_error(status, error_code, error_message)

    response = await taxi_pro_profiles.post(
        '/platform/v1/profiles/contractors/v1',
        headers=HEADERS,
        json=load_json('request.json'),
    )
    assert (
        response.status_code == (status // 100) * 100
    )  # we send back 400 on all 4xx from parks for simplicity
    if status < 500:  # 500 is not transfered from parks, throw as is
        assert response.json()['code'] == error_code
        assert response.json()['text'] == error_message


@pytest.mark.config(**_build_tvm_settings())
@pytest.mark.tvm2_ticket({111: MOCK_SERVICE_TICKET, 2345: OWN_SERVICE_TICKET})
@pytest.mark.experiments3(**_build_config3('market', 'provider', 'market'))
@pytest.mark.experiments3(**_build_config3('market', 'park', 'park-id'))
@pytest.mark.experiments3(
    **_build_config3(
        'market', 'tags', ['market_profile', 'market_magistrali'],
    ),
)
async def test_update_market_profile(
        load_json, taxi_pro_profiles, driver_profiles, parks, tags,
):
    driver_profiles.set_provider('market')
    tags.add_tags(
        'park-id_driver-profile-id',
        {'market_profile': {}, 'market_magistrali': {}},
    )
    response = await taxi_pro_profiles.put(
        '/platform/v1/profiles/contractors/v1',
        headers=HEADERS,
        params={'contractor_id': 'park-id_driver-profile-id'},
        json=load_json('request.json'),
    )
    assert response.status_code == 200
    assert response.json() == {
        'partner_id': 'park-id',
        'profile_id': 'driver-profile-id',
    }

    assert tags.assign.times_called == 1
    assert parks.create.times_called == 0
    assert parks.personal.times_called == 1
    assert parks.profile.times_called == 0
    assert driver_profiles.orders_provider.times_called == 1


@pytest.mark.config(**_build_tvm_settings())
@pytest.mark.tvm2_ticket({111: MOCK_SERVICE_TICKET, 2345: OWN_SERVICE_TICKET})
@pytest.mark.experiments3(**_build_config3('market', 'provider', 'market'))
@pytest.mark.experiments3(**_build_config3('market', 'park', 'park-id'))
@pytest.mark.experiments3(
    **_build_config3(
        'market', 'tags', ['market_profile', 'market_magistrali'],
    ),
)
@pytest.mark.parametrize('work_status,', ['working', 'not_working', 'fired'])
async def test_update_market_profile_with_work_status(
        load_json,
        taxi_pro_profiles,
        driver_profiles,
        parks,
        tags,
        work_status,
):
    parks.set_work_status(work_status)
    driver_profiles.set_provider('market')
    tags.add_tags(
        'park-id_driver-profile-id',
        {'market_profile': {}, 'market_magistrali': {}},
    )
    request = load_json('request.json')
    request['contractor']['work_status'] = work_status
    response = await taxi_pro_profiles.put(
        '/platform/v1/profiles/contractors/v1',
        headers=HEADERS,
        params={'contractor_id': 'park-id_driver-profile-id'},
        json=request,
    )
    assert response.status_code == 200
    assert response.json() == {
        'partner_id': 'park-id',
        'profile_id': 'driver-profile-id',
    }

    assert tags.assign.times_called == 1
    assert parks.create.times_called == 0
    assert parks.personal.times_called == 1
    assert parks.profile.times_called == 1
    assert driver_profiles.orders_provider.times_called == 1


@pytest.mark.config(**_build_tvm_settings())
@pytest.mark.tvm2_ticket({111: MOCK_SERVICE_TICKET, 2345: OWN_SERVICE_TICKET})
@pytest.mark.experiments3(**_build_config3('market', 'provider', 'market'))
@pytest.mark.experiments3(**_build_config3('market', 'park', 'park-id'))
@pytest.mark.experiments3(
    **_build_config3(
        'market', 'tags', ['market_profile', 'market_magistrali'],
    ),
)
@pytest.mark.parametrize(
    'status, error_code, error_message',
    [
        (400, '400', 'Invalid phone'),
        (401, '401', 'Duplicate Driver License'),
        (403, '403', 'Duplicate Employee Number'),
        (500, '500', 'Invalid Driver License'),
    ],
)
async def test_update_market_profile_parks_fail(
        taxi_pro_profiles,
        parks,
        tags,
        driver_profiles,
        status,
        error_code,
        error_message,
        load_json,
):
    driver_profiles.set_provider('market')
    parks.set_update_error(status, error_code, error_message)

    response = await taxi_pro_profiles.put(
        '/platform/v1/profiles/contractors/v1',
        headers=HEADERS,
        params={'contractor_id': 'park-id_driver-profile-id'},
        json=load_json('request.json'),
    )
    assert response.json()['code'] == error_code
    if status == 500:
        assert response.status_code == 500
    else:
        assert response.status_code == 400
        assert response.json()['text'] == error_message


@pytest.mark.config(**_build_tvm_settings())
@pytest.mark.tvm2_ticket({111: MOCK_SERVICE_TICKET, 2345: OWN_SERVICE_TICKET})
@pytest.mark.experiments3(**_build_config3('market', 'provider', 'market'))
@pytest.mark.experiments3(**_build_config3('market', 'park', 'park-id'))
@pytest.mark.experiments3(
    **_build_config3(
        'market', 'tags', ['market_profile', 'market_magistrali'],
    ),
)
@pytest.mark.parametrize(
    'status, error_code, error_message',
    [
        (400, '400', 'Invalid phone'),
        (401, '401', 'Duplicate Driver License'),
        (404, '404', 'Duplicate Employee Number'),
    ],
)
async def test_update_market_profile_driver_profiles_fail(
        taxi_pro_profiles,
        parks,
        tags,
        driver_profiles,
        status,
        error_code,
        error_message,
        load_json,
):
    driver_profiles.set_error(status, error_code, error_message)

    response = await taxi_pro_profiles.put(
        '/platform/v1/profiles/contractors/v1',
        headers=HEADERS,
        params={'contractor_id': 'park-id_driver-profile-id'},
        json=load_json('request.json'),
    )
    assert response.status_code == status
    assert response.json()['code'] == error_code
    assert response.json()['text'] == error_message


@pytest.mark.config(**_build_tvm_settings())
@pytest.mark.tvm2_ticket({111: MOCK_SERVICE_TICKET, 2345: OWN_SERVICE_TICKET})
@pytest.mark.experiments3(**_build_config3('market', 'provider', 'market'))
@pytest.mark.experiments3(**_build_config3('market', 'park', 'park-id'))
@pytest.mark.experiments3(
    **_build_config3(
        'market', 'tags', ['market_profile', 'market_magistrali'],
    ),
)
@pytest.mark.parametrize('status', [400, 500])
async def test_update_market_profile_tags_fail(
        taxi_pro_profiles, parks, driver_profiles, tags, status, load_json,
):
    tags.set_error(status)

    response = await taxi_pro_profiles.put(
        '/platform/v1/profiles/contractors/v1',
        headers=HEADERS,
        params={'contractor_id': 'park-id_driver-profile-id'},
        json=load_json('request.json'),
    )
    assert response.status_code == 500  # on tags 400 we always return 500
