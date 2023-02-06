import pytest


@pytest.mark.pgsql('grocery_depots', files=['in_effect_zones.sql'])
async def test_limited(taxi_grocery_depots):
    # Tins from pg_overlord_catalog.sql
    # personal.add_tins(['tin-for-franchise', 'tin-11111111'])

    await taxi_grocery_depots.invalidate_caches()

    response = await taxi_grocery_depots.post(
        '/internal/v1/depots/v1/depots', json={'legacy_depot_ids': ['2021']},
    )
    one_depot = response.json()['depots']
    assert len(one_depot) == 1
    depot = one_depot[0]
    assert depot['depot_id'] == 'ddb8a6fbcee34b38b5281d8ea6ef749a000100012021'
    assert depot['company_type'] == 'yandex'
    assert (
        depot['company_id'] == '6490c0508a8c4370be75096d9f0ef615000200010001'
    )
    assert depot['short_address'] == 'Мир Дошиков'
    assert depot['timetable'] == [
        {
            'day_type': 'Everyday',
            'working_hours': {
                'from': {'hour': 8, 'minute': 0},
                'to': {'hour': 23, 'minute': 0},
            },
        },
    ]


@pytest.mark.pgsql('grocery_depots', files=['in_effect_zones.sql'])
async def test_basic(taxi_grocery_depots):
    # Tins from pg_overlord_catalog.sql
    # personal.add_tins(['tin-for-franchise', 'tin-11111111'])

    await taxi_grocery_depots.invalidate_caches()

    response = await taxi_grocery_depots.post(
        '/internal/v1/depots/v1/depots', json={'legacy_depot_ids': []},
    )
    depots = {x['depot_id']: x for x in response.json()['depots']}
    assert 'ddb8a6fbcee34b38b5281d8ea6ef749a000100012020' in depots
    assert 'ddb8a6fbcee34b38b5281d8ea6ef749a000100012021' in depots
    assert 'e8756eee278742e99624399f81841c07000300010000' in depots
    depot = depots['ddb8a6fbcee34b38b5281d8ea6ef749a000100012021']
    assert depot['oebs_depot_id'] == 'oebs-depot-id-for-test_lavka_1'
    assert depot['company_title'] == 'ООО Рога и Копыта'
    depot = depots['e8756eee278742e99624399f81841c07000300010000']
    assert depot['country_iso3'] == 'ISR'
    assert depot['country_iso2'] == 'IL'
    assert depot['region_id'] == 131
    assert (
        depot['root_category_id']
        == 'a04e2ecb54344fc0945a623e14e2617c000200010001'
    )
    assert (
        depot['assortment_id']
        == 'afa1095fbcee462dafe65632e095fca9000200010001'
    )
    assert (
        depot['price_list_id']
        == '21477d99cd9b40068e797daa49faf801000300010000'
    )
    depot = depots['c3df22637dc341d9a21cdc00774a241a000100010001']
    assert depot['country_iso3'] == 'RUS'
    assert depot['country_iso2'] == 'RU'
    assert depot['region_id'] == 2
    assert (
        depot['root_category_id']
        == '8f4cf8acbf2c4fe5876f20fb12f01a51000100010001'
    )
    assert (
        depot['assortment_id']
        == 'dc464bea93294d6da9b1727eb12c1073000200010000'
    )
    assert (
        depot['price_list_id']
        == '4cdfbe900cdb4a92aa2545d711b311c7000200010000'
    )
    assert depot['timetable'] == [
        {
            'day_type': 'Everyday',
            'working_hours': {
                'from': {'hour': 8, 'minute': 0},
                'to': {'hour': 23, 'minute': 0},
            },
        },
    ]
