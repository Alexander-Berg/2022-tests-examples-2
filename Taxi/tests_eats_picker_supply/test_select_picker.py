import pytest


@pytest.mark.parametrize(
    'data,expected_code,expected_data',
    [
        (
            {'place_id': 1, 'picking_duration': 300},
            200,
            {
                #  picker 2 has more priority but already assigned
                'picker_id': '3',
                'requisite_type': 'TinkoffCard',
                'requisite_value': '345',
                'picker_name': 'Пайкер Курьерович',
                'picker_phone_id': '123456',
            },
        ),
        (
            {'place_id': 2, 'picking_duration': 300},
            200,
            {
                'picker_id': '4',
                'requisite_type': 'TinkoffCard',
                'requisite_value': '456',
                'picker_name': 'Пайкер Курьерович',
                'picker_phone_id': '123456',
            },
        ),
        (
            {'place_id': 2, 'picking_duration': 32701},
            404,
            {
                # picking_duration is to big to find available picker
                'code': 'AVAILABLE_PICKER_IS_NOT_FOUND',
                'message': 'available picker is not found',
            },
        ),
        (
            {'place_id': 3, 'picking_duration': 300},
            200,
            {
                # picker 6 has more priority, but excluded
                'picker_id': '5',
                'requisite_type': 'TinkoffCard',
                'requisite_value': '567',
                'picker_name': 'Пайкер Курьерович',
                'picker_phone_id': '123456',
            },
        ),
    ],
)
@pytest.mark.now('2020-10-14T15:00:00+0000')
async def test_select_picker(
        mockserver,
        load_json,
        taxi_eats_picker_supply,
        data,
        expected_code,
        expected_data,
        create_picker,
):
    kwargs = {
        'available_until': '2020-10-15T00:00:00+0000',
        'places_ids': [1],
        'priority': 0,
        'requisite_type': 'TinkoffCard',
    }
    create_picker(**{**kwargs, 'picker_id': '1', 'requisite_value': '123'})
    create_picker(
        **{
            **kwargs,
            'picker_id': '2',
            'priority': 10,
            'requisite_value': '234',
        },
    )
    create_picker(
        **{
            **kwargs,
            'picker_id': '3',
            'priority': 9,
            'requisite_value': '345',
        },
    )
    create_picker(
        **{
            **kwargs,
            'picker_id': '4',
            'places_ids': [1, 2],
            'requisite_value': '456',
        },
    )
    create_picker(
        **{
            **kwargs,
            'picker_id': '5',
            'places_ids': [3],
            'requisite_value': '567',
        },
    )
    create_picker(
        **{
            **kwargs,
            'picker_id': '6',
            'places_ids': [3],
            'priority': 1,
            'excluded_until': '2020-10-15T00:00:00+0000',
            'requisite_value': '678',
        },
    )
    response = await taxi_eats_picker_supply.post(
        '/api/v1/select-picker', json=data,
    )
    assert response.status == expected_code
    assert response.json() == expected_data


@pytest.mark.parametrize(
    'available_until,expected_picker',
    [
        # picker 7 is of higher priority than 4
        ('2020-10-14T16:00:00+0000', '7'),
        # picker 7 has more priority, but stops being available in 30s
        ('2020-10-14T15:00:30+0000', '4'),
    ],
)
@pytest.mark.now('2020-10-14T15:00:00+0000')
async def test_exclude_picker_shortly_before_end(
        taxi_config,
        taxi_eats_picker_supply,
        available_until,
        expected_picker,
        create_picker,
):
    create_picker(
        picker_id=4,
        places_ids=[2],
        priority=0,
        available_until='2020-10-14T20:00:00+0000',
    )
    create_picker(
        picker_id=7,
        places_ids=[2],
        priority=1,
        available_until=available_until,
    )
    taxi_config.set_values(
        {'EATS_PICKER_SUPPLY_SKIP_BEFORE_AVAILABLE_UNTIL': 60},
    )
    response = await taxi_eats_picker_supply.post(
        '/api/v1/select-picker', json={'place_id': 2, 'picking_duration': 300},
    )
    assert response.status == 200
    assert response.json()['picker_id'] == expected_picker
