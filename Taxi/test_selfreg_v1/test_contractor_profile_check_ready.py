import pytest

TAXIMETER_USER_AGENT = 'Taximeter 9.61 (1234)'

SELFREG_DELAY_IN_PROFILE_CREATION = {'time_s': 30}
SELFREG_DELAY_IN_PROFILE_CREATION_0 = {'time_s': 0}


@pytest.mark.config(
    SELFREG_DELAY_IN_PROFILE_CREATION=SELFREG_DELAY_IN_PROFILE_CREATION_0,
)
async def test_contractor_profile_check_ready(taxi_selfreg, mockserver):
    @mockserver.json_handler('/hiring-candidates-py3/v1/leads/list')
    def _leads(request):
        assert request.json['external_ids'] == ['externalID']
        return {
            'is_bounded_by_limit': False,
            'leads': [
                {
                    'lead_id': 'id',
                    'fields': [{'name': 'courier_id', 'value': '1000'}],
                },
            ],
        }

    @mockserver.json_handler(
        '/driver-profiles/v1/courier/profiles/retrieve_by_eats_id',
    )
    async def _retrieve_by_eats_id(request):
        eats_courier_id_in_set = request.json['eats_courier_id_in_set']
        assert eats_courier_id_in_set == ['1000']
        return {
            'courier_by_eats_id': [
                {
                    'eats_courier_id': courier_id,
                    'profiles': [
                        {
                            'park_driver_profile_id': 'park_uuid',
                            'data': {'park_id': 'park', 'uuid': 'uuid'},
                        },
                    ],
                }
                for courier_id in eats_courier_id_in_set
            ],
        }

    response = await taxi_selfreg.get(
        '/selfreg/v1/contractor-profile/check-ready',
        headers={'User-Agent': TAXIMETER_USER_AGENT},
        params={'token': 'token1'},
    )

    assert response.status == 200
    content = await response.json()
    assert content == {
        'status': 'success',
        'park_id': 'park',
        'driver_profile_id': 'uuid',
    }


@pytest.mark.config(
    SELFREG_DELAY_IN_PROFILE_CREATION=SELFREG_DELAY_IN_PROFILE_CREATION_0,
)
async def test_contractor_profile_check_ready_for_native_courier_creation(
        taxi_selfreg, mockserver,
):
    @mockserver.json_handler('/hiring-candidates-py3/v1/leads/list')
    def _leads(request):
        assert request.json['external_ids'] == ['externalID']
        return {'is_bounded_by_limit': False, 'leads': []}

    @mockserver.json_handler(
        '/driver-profiles/v1/courier/profiles/retrieve_by_eats_id',
    )
    async def _retrieve_by_eats_id(request):
        eats_courier_id_in_set = request.json['eats_courier_id_in_set']
        assert eats_courier_id_in_set == ['123']
        return {
            'courier_by_eats_id': [
                {
                    'eats_courier_id': courier_id,
                    'profiles': [
                        {
                            'park_driver_profile_id': 'park_uuid',
                            'data': {
                                'park_id': 'some-park',
                                'uuid': 'some-uuid',
                            },
                        },
                    ],
                }
                for courier_id in eats_courier_id_in_set
            ],
        }

    response = await taxi_selfreg.get(
        '/selfreg/v1/contractor-profile/check-ready',
        headers={'User-Agent': TAXIMETER_USER_AGENT},
        params={'token': 'token2'},
    )

    assert response.status == 200
    content = await response.json()
    assert content == {
        'status': 'success',
        'park_id': 'some-park',
        'driver_profile_id': 'some-uuid',
    }


def mark_now(condition):
    if condition == 'too_early':
        return pytest.mark.now('2022-04-12T10:10:20+0000')
    return pytest.mark.now('2022-04-12T10:10:50+0000')


@pytest.mark.config(
    SELFREG_DELAY_IN_PROFILE_CREATION=SELFREG_DELAY_IN_PROFILE_CREATION,
)
@pytest.mark.parametrize(
    'expected_response',
    [
        pytest.param(
            {'status': 'pending'}, marks=mark_now('too_early'), id='too_early',
        ),
        pytest.param(
            {
                'status': 'success',
                'park_id': 'park_id_test',
                'driver_profile_id': 'driver_profile_id_test',
            },
            marks=mark_now('time'),
            id='time',
        ),
    ],
)
async def test_contractor_profile_is_committed_native_courier_creation(
        taxi_selfreg, mockserver, expected_response,
):
    @mockserver.json_handler('/hiring-candidates-py3/v1/leads/list')
    def _leads(request):
        assert request.json['external_ids'] == ['externalID']
        return {'is_bounded_by_limit': False, 'leads': []}

    @mockserver.json_handler(
        '/driver-profiles/v1/courier/profiles/retrieve_by_eats_id',
    )
    async def _retrieve_by_eats_id(request):
        eats_courier_id_in_set = request.json['eats_courier_id_in_set']
        assert eats_courier_id_in_set == ['123']
        return {
            'courier_by_eats_id': [
                {
                    'eats_courier_id': courier_id,
                    'profiles': [
                        {
                            'park_driver_profile_id': 'park_uuid',
                            'data': {
                                'park_id': 'some-park',
                                'uuid': 'some-uuid',
                            },
                        },
                    ],
                }
                for courier_id in eats_courier_id_in_set
            ],
        }

    response = await taxi_selfreg.get(
        '/selfreg/v1/contractor-profile/check-ready',
        headers={'User-Agent': TAXIMETER_USER_AGENT},
        params={'token': 'token73'},
    )

    assert response.status == 200
    content = await response.json()
    assert content == expected_response
