from qc_invites.generated.cron import run_cron
from test_qc_invites import conftest


def get_invited_entities(pgsql):
    cursor = pgsql['qc_invites'].cursor()
    cursor.execute(
        'SELECT invite_id, ARRAY_AGG(entity_id)'
        'FROM invites.entities GROUP BY invite_id',
    )
    return dict(row for row in cursor)


async def test_prepare_invites_driver(
        fleet_vehicles: conftest.MockContext,
        driver_profiles: conftest.MockContext,
        load_json,
        pgsql,
):
    """
    Базовая проверка: 3 машины в 4 парках (4-ый пустой).
    Парк 1: 3 рабочих водителя на первой машине, 1 рабочий водитель на второй
    Парк 2: 2 рабочих водителя на первый машине
    Парк 3: 1 рабочий водитель на третьей машине
    По первому инвайту идёт первая машина. И того по первому инвайту
    должно быть 5 водителей и т.д.
    Дополнительно проверяется работа с дубликатами:
    - номеров машин (car_number2) во 2-ом инвайте (Парк 1)
    - ВУ (license-1) в 4-ом инвайте (Парк 4)
    """
    json_prefix = 'fleet_vehicles_by_number_with_normalization_car_number_'
    for i in range(1, 4):
        fleet_vehicles.set_response(
            f'retrieve_by_number_with_normalization_car_number-{i}',
            load_json(f'{json_prefix}{i}.json'),
        )
    driver_profiles.set_response(
        'retrieve_by_park_id_car_id',
        load_json('driver_profiles_by_park_id_car_id.json'),
    )
    driver_profiles.set_response(
        'profiles_retrieve_by_license',
        load_json('driver_profiles_by_license.json'),
    )
    await run_cron.main(
        ['qc_invites.crontasks.prepare_invites_driver', '-t', '0'],
    )
    cursor = pgsql['qc_invites'].cursor()
    cursor.execute(
        'SELECT invite_id, ARRAY_AGG(entity_id)'
        'FROM invites.entities GROUP BY invite_id',
    )
    invited_entities = dict(row for row in cursor)
    should_be_invited = load_json('should_be_invited.json')
    assert set(invited_entities.keys()) == set(should_be_invited.keys())
    for invite_id, entities in invited_entities.items():
        assert set(should_be_invited[invite_id]) == set(entities)


async def test_prepare_invites_wrong_park(
        fleet_vehicles: conftest.MockContext,
        driver_profiles: conftest.MockContext,
        load_json,
        pgsql,
):
    """
    Проверка ситуации, когда в одном из инвайтов указали неправильный парк.
    Мы должны вызвать только одного водителя, поскольку указан фильтр
    указан фильтр: 'park_id': 'park-1'.
    Водителя в другом парке не вызываем, так как его парк указали с ошибкой:
    'park_id': 'non_existent_park'
    """
    fleet_vehicles.set_response(
        'retrieve_by_number_with_normalization',
        load_json('fleet_vehicles_by_number_with_normalization.json'),
    )
    driver_profiles.set_response(
        'retrieve_by_park_id_car_id',
        load_json('driver_profiles_by_park_id_car_id.json'),
    )
    await run_cron.main(
        ['qc_invites.crontasks.prepare_invites_driver', '-t', '0'],
    )
    assert len(get_invited_entities(pgsql)) == 1


async def test_prepare_invites_no_entities(
        fleet_vehicles: conftest.MockContext,
        driver_profiles: conftest.MockContext,
        load_json,
        pgsql,
):
    """
    Проверка перевода инвайтов без сущностей в статус no_entities.
    Для первого инвайта просто по номеру тс
    (т.е. по всем фильтрам, кроме park_id) не найдется сущностей.
    Для второго инвайта только по номеру тс находились сущности,
    а вот с park_id нашлось 0 сущностей.
    Для третьего инвайта все ок, и он должен перевестись в prepared.
    """
    json_prefix = 'fleet_vehicles_by_number_with_normalization_car_number_'
    for i in range(1, 4):
        fleet_vehicles.set_response(
            f'retrieve_by_number_with_normalization_car_number-{i}',
            load_json(f'{json_prefix}{i}.json'),
        )

    await run_cron.main(
        ['qc_invites.crontasks.prepare_invites_car', '-t', '0'],
    )

    cursor = pgsql['qc_invites'].cursor()
    cursor.execute('SELECT id, status FROM invites.invites')

    invites_status = dict(row for row in cursor)

    expected_invites_status = load_json('expected_invites_status.json')
    assert set(invites_status.keys()) == set(expected_invites_status.keys())
    for invite_id, status in invites_status.items():
        assert expected_invites_status[invite_id] == status
