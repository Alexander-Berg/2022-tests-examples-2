import pytest


NOW = '2021-08-06T10:00:00+0300'


@pytest.fixture(name='get_courier_external_id')
async def _get_courier_from_msk(mockserver):
    @mockserver.json_handler(
        '/driver-profiles/v1/driver/profiles/retrieve_by_phone',
    )
    def _mock_handler(request):
        _id = request.json['driver_phone_in_set'][0][-1]
        if _id in ['1', '2', '3', '4', '5', '6']:
            return {
                'profiles_by_phone': [
                    {
                        'driver_phone': 'DRIVER_PHONE' + _id,
                        'profiles': [
                            {
                                'data': {'external_ids': {'eats': 'ID'}},
                                'park_driver_profile_id': 'EXTERNAL_ID_' + _id,
                            },
                        ],
                    },
                ],
            }
        if _id == '7':
            return {
                'profiles_by_phone': [
                    {
                        'driver_phone': 'DRIVER_PHONE1',
                        'profiles': [
                            {
                                'data': {},
                                'park_driver_profile_id': 'EXTERNAL_ID_1',
                            },
                        ],
                    },
                ],
            }
        if _id == '8':
            return {
                'profiles_by_phone': [
                    {'driver_phone': 'DRIVER_PHONE2', 'profiles': []},
                ],
            }

        return {}


TEST_DEVICE_ID = 'SOME_DEVICE_ID'


@pytest.fixture(name='get_metrica_device_id')
def _get_metrica_device_id(request, mockserver):
    result = {}
    if request is not None and hasattr(request, 'param'):
        result = request.param

    device_id = (
        result['device_id'] if 'device_id' in result else TEST_DEVICE_ID
    )

    @mockserver.json_handler(
        '/driver-profiles/v1/driver/app/profiles/retrieve',
    )
    def _mock_handler(request):
        assert 'projection' in request.json
        assert 'data.metrica_device_id' in request.json['projection']
        assert 'id_in_set' in request.json
        assert len(request.json['id_in_set']) == 1

        return {
            'profiles': [
                {
                    'park_driver_profile_id': request.json['id_in_set'][0],
                    'data': {'metrica_device_id': device_id},
                },
            ],
        }

    return result


@pytest.mark.parametrize(
    ('driver_phone', 'result'),
    [
        ('DRIVER_PHONE1', {'isActive': True, 'shiftService': 'eda'}),
        ('DRIVER_PHONE2', {'isActive': True, 'shiftService': 'eda'}),
        ('DRIVER_PHONE3', {'isActive': False}),
    ],
)
@pytest.mark.parametrize('use_device_id', [True, False])
@pytest.mark.parametrize(
    'get_metrica_device_id',
    [
        {'device_id': TEST_DEVICE_ID},
        {'device_id': ('wrong_' + TEST_DEVICE_ID)},
    ],
    indirect=True,
)
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.pgsql('eda_couriers_schedule', files=['filling_data.sql'])
async def test_found_courier_in_progress(
        taxi_eats_performer_shifts,
        get_courier_external_id,
        driver_phone,
        result,
        use_device_id,
        get_metrica_device_id,
):
    response = await taxi_eats_performer_shifts.get(
        path='/internal/eats-performer-shifts/v1'
        '/courier-shift-states/info/retrieve-by-phone?'
        'personal_phone_id='
        + driver_phone
        + (('&device_id=' + TEST_DEVICE_ID) if use_device_id else ''),
    )
    assert response.status_code == 200

    if use_device_id and 'device_id' in get_metrica_device_id:
        same_devices = get_metrica_device_id['device_id'] == TEST_DEVICE_ID
        if not same_devices:
            result = {'isActive': False}

    assert response.json() == result


@pytest.mark.parametrize(
    ('driver_phone', 'minutes_before_shift', 'result'),
    [
        ('DRIVER_PHONE4', '20', {'isActive': True, 'shiftService': 'eda'}),
        ('DRIVER_PHONE5', '10', {'isActive': False}),
        ('DRIVER_PHONE6', '10', {'isActive': True, 'shiftService': 'eda'}),
        ('DRIVER_PHONE7', '10', {'isActive': False}),
        ('DRIVER_PHONE8', '0', {'isActive': False}),
    ],
)
@pytest.mark.now(NOW)
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.pgsql('eda_couriers_schedule', files=['filling_data.sql'])
async def test_found_courier_planned_with_minutes_before_shifts(
        taxi_eats_performer_shifts,
        get_courier_external_id,
        driver_phone,
        minutes_before_shift,
        result,
):
    response = await taxi_eats_performer_shifts.get(
        path='/internal/eats-performer-shifts/v1'
        '/courier-shift-states/info/retrieve-by-phone?'
        'personal_phone_id='
        + driver_phone
        + '&minutes_before_shift='
        + minutes_before_shift,
    )
    assert response.status_code == 200
    assert response.json() == result
