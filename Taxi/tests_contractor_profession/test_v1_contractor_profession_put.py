import pytest

from tests_contractor_profession import utils_db

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


@pytest.mark.config(
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
)
@pytest.mark.tvm2_ticket({111: MOCK_SERVICE_TICKET, 2345: OWN_SERVICE_TICKET})
@pytest.mark.experiments3(filename='profession_switch_config.json')
@pytest.mark.experiments3(filename='orders_provider_configs.json')
@pytest.mark.parametrize(
    'contractor_profile_id, is_from_dbdrivers',
    [
        pytest.param(
            'contractor_profile_id', True, id='orders_provider_from_dbdrivers',
        ),
        pytest.param('exp_driver1', False, id='orders_provider_from_exp'),
    ],
)
@pytest.mark.parametrize('profession_id', ['taxi-driver', 'grocery-courier'])
async def test_contractor_put(
        taxi_contractor_profession,
        driver_profiles,
        pgsql,
        mockserver,
        contractor_profile_id,
        is_from_dbdrivers,
        profession_id,
):
    @mockserver.json_handler('/driver-profiles/v2/profile/orders-provider')
    def _orders_provider(request):
        return {}

    utils_db.insert_professions(
        pgsql,
        park_id='park_id',
        driver_profile_id=contractor_profile_id,
        profession_id='eats-courier',
    )

    if is_from_dbdrivers:
        driver_profiles.set_orders_provider(
            park_id='park_id',
            contractor_profile_id=contractor_profile_id,
            orders_provider='eda',
        )

    response = await taxi_contractor_profession.put(
        '/internal/v1/contractors/profession',
        headers={'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET},
        params={
            'consumer': 'test_consumer',
            'contractor_profile_id': contractor_profile_id,
            'park_id': 'park_id',
        },
        json={'profession_id': profession_id},
    )

    assert driver_profiles.retrieve_profiles.times_called == is_from_dbdrivers

    if profession_id == 'grocery-courier':
        result = utils_db.select_professions(
            pgsql, park_id='park_id', driver_profile_id=contractor_profile_id,
        )
        assert result == [
            (3, 'park_id', contractor_profile_id, 'grocery-courier'),
        ]
        assert response.status_code == 200
        assert _orders_provider.times_called == 1
    else:
        assert response.status_code == 400


@pytest.mark.config(
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
)
@pytest.mark.tvm2_ticket({111: MOCK_SERVICE_TICKET, 2345: OWN_SERVICE_TICKET})
@pytest.mark.parametrize(
    'contractor_profile_id',
    [
        pytest.param('uuid1', id='orders_provider_from_dbdrivers'),
        pytest.param('exp_driver1', id='orders_provider_from_exp'),
    ],
)
@pytest.mark.experiments3(filename='orders_provider_configs.json')
async def test_switch_not_init_profession_from_exp(
        taxi_contractor_profession, contractor_profile_id,
):
    response = await taxi_contractor_profession.put(
        '/internal/v1/contractors/profession',
        headers={'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET},
        params={
            'consumer': 'test_consumer',
            'contractor_profile_id': contractor_profile_id,
            'park_id': 'park_id',
        },
        json={'profession_id': 'grocery-courier'},
    )

    assert response.status_code == 500
    assert response.json() == {
        'code': 'BAD_REQUEST',
        'message': 'Old profession absence',
    }
