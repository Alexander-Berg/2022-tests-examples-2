import pytest


async def test_hold_picker_supply_204(
        taxi_eats_picker_supply, create_picker, get_picker,
):
    picker_id = create_picker(picker_id='12')
    response = await taxi_eats_picker_supply.post(
        '/api/v1/picker/hold-supply', json={'picker_id': '12', 'seconds': 600},
    )
    assert response.status_code == 204
    assert get_picker(picker_id)['excluded_until'] is not None


@pytest.mark.now('2020-09-29T10:20:00+03:00')
@pytest.mark.parametrize(
    'create_excluded_until,expected_excluded_until',
    [
        [None, '2020-09-29 10:30:00+03:00'],
        ['2020-09-29 10:25:00+03:00', '2020-09-29 10:30:00+03:00'],
        ['2020-09-29 10:35:00+03:00', '2020-09-29 10:35:00+03:00'],
    ],
)
async def test_hold_picker_supply_204_marknow(
        taxi_eats_picker_supply,
        create_picker,
        get_picker,
        create_excluded_until,
        expected_excluded_until,
):
    picker_id = create_picker(
        picker_id='12', excluded_until=create_excluded_until,
    )
    response = await taxi_eats_picker_supply.post(
        '/api/v1/picker/hold-supply', json={'picker_id': '12', 'seconds': 600},
    )
    # TODO write test with good now processing
    assert response.status_code == 204
    assert (
        str(get_picker(picker_id)['excluded_until']) == expected_excluded_until
    )


async def test_hold_picker_supply_404(
        taxi_eats_picker_supply, create_picker, get_picker,
):
    picker_id = create_picker(picker_id='11')
    response = await taxi_eats_picker_supply.post(
        '/api/v1/picker/hold-supply', json={'picker_id': '12', 'seconds': 600},
    )
    assert response.status_code == 404
    assert get_picker(picker_id)['excluded_until'] is None
