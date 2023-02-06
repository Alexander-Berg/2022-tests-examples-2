import json

import pytest


@pytest.mark.parametrize(
    'select_id, status, expected_code, expected_status',
    [
        ('yandex_birthday', 'rollback', 200, 'rollback'),
        ('yandex_birthday', 'active', 200, 'active'),
        ('new_year', 'active', 409, None),
        ('new_year', 'rollback', 200, 'rollback'),
    ],
)
@pytest.mark.pgsql('personal_goals', files=['basic_personal_goals.sql'])
async def test_change_selection_status(
        taxi_personal_goals_web,
        select_id,
        status,
        expected_code,
        expected_status,
        pg_goals,
):
    data = {'selection_id': select_id, 'status': status}
    response = await taxi_personal_goals_web.post(
        '/internal/admin/selections/update', data=json.dumps(data),
    )
    assert response.status == expected_code

    if expected_status:
        selections = await pg_goals.selections.by_ids([select_id])
        assert selections[0]['status'] == expected_status


async def test_uknow_selection_id(taxi_personal_goals_web, pg_goals):
    data = {'selection_id': 'random', 'status': 'active'}
    response = await taxi_personal_goals_web.post(
        '/internal/admin/selections/update', data=json.dumps(data),
    )
    assert response.status == 200
    selections = await pg_goals.selections.all()
    assert not selections
