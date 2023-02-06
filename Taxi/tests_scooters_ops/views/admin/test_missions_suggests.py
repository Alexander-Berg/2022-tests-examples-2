import pytest

HANDLER = '/scooters-ops/v1/admin/missions/suggests'


@pytest.mark.config(
    SCOOTERS_REGIONS=[
        {'id': 'region_1', 'name': 'Region 1'},
        {'id': 'region_2', 'name': 'Region 2'},
        {'id': 'region_3', 'name': 'Region 3'},
    ],
)
@pytest.mark.translations(
    client_messages={
        'scooters.mission.status.created': {'ru': 'Создана'},
        'scooters.mission.status.preparing': {'ru': 'Подготовлена'},
        'scooters.mission.status.assigning': {'ru': 'Назначена'},
        'scooters.mission.status.performing': {'ru': 'Исполняется'},
        'scooters.mission.status.completed': {'ru': 'Завершена'},
        'scooters.mission.status.cancelling': {'ru': 'Отменена'},
        'scooters.mission.status.failed': {'ru': 'Провалена'},
        'scooters.mission.type.recharge': {'ru': 'Перезарядка'},
        'scooters.mission.type.resurrect': {'ru': 'Воскрешение'},
        'scooters.mission.type.relocation': {'ru': 'Релокация'},
    },
)
async def test_handler(taxi_scooters_ops):
    response = await taxi_scooters_ops.get(
        HANDLER, headers={'Accept-Language': 'ru-ru'},
    )

    assert response.status == 200
    assert response.json() == {
        'mission_statuses': [
            {'status': 'created', 'title': 'Создана'},
            {'status': 'preparing', 'title': 'Подготовлена'},
            {'status': 'assigning', 'title': 'Назначена'},
            {'status': 'performing', 'title': 'Исполняется'},
            {'status': 'completed', 'title': 'Завершена'},
            {'status': 'cancelling', 'title': 'Отменена'},
            {'status': 'failed', 'title': 'Провалена'},
        ],
        'mission_types': [
            {'type': 'recharge', 'hint': 'Перезарядка'},
            {'type': 'resurrect', 'hint': 'Воскрешение'},
            {'type': 'relocation', 'hint': 'Релокация'},
        ],
        'regions': [
            {'id': 'region_1', 'name': 'Region 1'},
            {'id': 'region_2', 'name': 'Region 2'},
            {'id': 'region_3', 'name': 'Region 3'},
        ],
    }
