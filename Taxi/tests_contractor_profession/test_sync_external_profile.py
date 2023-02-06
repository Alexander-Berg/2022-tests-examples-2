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


@pytest.fixture(name='driver_profiles')
def _driver_profiles(mockserver):
    class Context:
        def __init__(self):
            self.provider = None

        def set_provider(self, provider):
            self.provider = provider

    context = Context()

    @mockserver.json_handler('/driver-profiles/v2/profile/orders-provider')
    def _orders_provider(request):
        if context.provider:
            assert request.json['orders_providers'] == [context.provider]
        return {}

    setattr(context, 'orders_provider', _orders_provider)
    return context


@pytest.fixture(name='parks')
def _parks(mockserver):
    class Context:
        pass

    context = Context()

    @mockserver.json_handler('/parks/internal/driver-profiles/create')
    def _create(request):
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
        return {
            'driver_profile': {
                'id': 'driver-profile-id',
                'park_id': 'park-id',
                'first_name': 'First',
                'last_name': 'Last',
                'phones': ['+70006660001'],
            },
        }

    setattr(context, 'create', _create)
    setattr(context, 'personal', _personal)
    return context


@pytest.fixture(name='tags')
def _tags(mockserver):
    class Context:
        def __init__(self):
            self.tags = {}

        def add_tags(self, dbid_uuid, tags):
            self.tags[dbid_uuid] = tags

    context = Context()

    @mockserver.json_handler('/tags/v1/assign')
    def _assign(request):
        if context.tags:
            tags = [
                {'name': dbid_uuid, 'type': 'dbid_uuid', 'tags': tags}
                for dbid_uuid, tags in context.tags.items()
            ]
            assert tags == request.json['entities']
        return {}

    setattr(context, 'assign', _assign)
    return context


def _build_profile(name, value):
    return {
        name: value,
        'profiles': [{'park_driver_profile_id': 'park-id_driver-profile-id'}],
    }


def _build_tvm_settings(external_consumer):
    return dict(
        TVM_ENABLED=True,
        TVM_RULES=[{'src': 'developers', 'dst': 'contractor-profession'}],
        TVM_SERVICES={
            'contractor-profession': 2345,
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
            'fleet-parks': 122,
        },
        CONTRACTOR_PROFESSION_EXTERNAL_CONSUMERS_MAPPING={
            'developers': external_consumer,
        },
    )


def _build_config3(external_consumer, name, value):
    return dict(
        name=f'contractor-profession-sync-{external_consumer}-{name}',
        consumers=['contractor-profession-sync'],
        default_value={name: value},
        is_config=True,
    )


@pytest.mark.config(**_build_tvm_settings('market'))
@pytest.mark.tvm2_ticket({111: MOCK_SERVICE_TICKET, 2345: OWN_SERVICE_TICKET})
@pytest.mark.experiments3(**_build_config3('market', 'provider', 'market'))
@pytest.mark.experiments3(**_build_config3('market', 'park', 'park-id'))
@pytest.mark.experiments3(
    **_build_config3(
        'market', 'tags', ['market_profile', 'market_magistrali'],
    ),
)
async def test_create_market_profile(taxi_contractor_profession, parks, tags):
    tags.add_tags(
        'park-id_driver-profile-id',
        {'market_profile': {}, 'market_magistrali': {}},
    )
    headers = {
        'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET,
        'X-Idempotency-Token': 'some_unique_string',
    }
    response = await taxi_contractor_profession.post(
        '/internal/v1/platform/contractors',
        headers=headers,
        params={'consumer': 'market'},
        json={
            'contractor': {
                'phone': 'phone',
                'details': {'external_id': 'external_id'},
                'full_name': {
                    'first_name': 'first_name',
                    'last_name': 'last_name',
                    'middle_name': 'patronymic',
                },
            },
        },
    )
    assert response.status_code == 200
    assert response.json() == {'contractor_id': 'park-id_driver-profile-id'}

    assert tags.assign.times_called == 1
    assert parks.create.times_called == 1
    assert parks.personal.times_called == 0


@pytest.mark.config(**_build_tvm_settings('market'))
@pytest.mark.tvm2_ticket({111: MOCK_SERVICE_TICKET, 2345: OWN_SERVICE_TICKET})
async def test_bad_consumer(taxi_contractor_profession, parks, tags):
    headers = {
        'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET,
        'X-Idempotency-Token': 'some_unique_string',
    }
    response = await taxi_contractor_profession.post(
        '/internal/v1/platform/contractors',
        headers=headers,
        params={'consumer': 'magistrali'},
        json={
            'contractor': {
                'phone': 'phone',
                'details': {'external_id': 'external_id'},
                'full_name': {
                    'first_name': 'first_name',
                    'last_name': 'last_name',
                    'middle_name': 'patronymic',
                },
            },
        },
    )
    assert response.status_code == 401


@pytest.mark.config(**_build_tvm_settings('market'))
@pytest.mark.tvm2_ticket({111: MOCK_SERVICE_TICKET, 2345: OWN_SERVICE_TICKET})
@pytest.mark.experiments3(**_build_config3('market', 'provider', 'market'))
@pytest.mark.experiments3(**_build_config3('market', 'park', 'park-id'))
@pytest.mark.experiments3(
    **_build_config3(
        'market', 'tags', ['market_profile', 'market_magistrali'],
    ),
)
async def test_update_market_profile(
        taxi_contractor_profession, driver_profiles, parks, tags,
):
    driver_profiles.set_provider('market')
    tags.add_tags(
        'park-id_driver-profile-id',
        {'market_profile': {}, 'market_magistrali': {}},
    )
    headers = {'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET}
    response = await taxi_contractor_profession.put(
        '/internal/v1/platform/contractors',
        headers=headers,
        params={
            'consumer': 'market',
            'contractor_id': 'park-id_driver-profile-id',
        },
        json={
            'contractor': {
                'phone': 'phone',
                'details': {'external_id': 'external_id'},
                'full_name': {
                    'first_name': 'first_name',
                    'last_name': 'last_name',
                    'middle_name': 'patronymic',
                },
            },
        },
    )
    assert response.status_code == 200
    assert response.json() == {'contractor_id': 'park-id_driver-profile-id'}

    assert tags.assign.times_called == 1
    assert parks.create.times_called == 0
    assert parks.personal.times_called == 1
    assert driver_profiles.orders_provider.times_called == 1
