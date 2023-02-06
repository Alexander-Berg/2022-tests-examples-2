import pytest


@pytest.mark.pgsql('personal_goals', files=['basic_personal_goals.sql'])
async def test_selections_list(taxi_personal_goals_web):
    response = await taxi_personal_goals_web.post(
        '/internal/admin/selections/list',
    )
    assert response.status == 200
    response_body = await response.json()
    assert response_body == [
        {'selection_id': 'new_year', 'status': 'rollback', 'goals_count': 1},
        {
            'selection_id': 'yandex_birthday',
            'status': 'active',
            'goals_count': 7,
        },
    ]


async def test_empty_selections_list(taxi_personal_goals_web):
    response = await taxi_personal_goals_web.post(
        '/internal/admin/selections/list',
    )
    assert response.status == 200
    response_body = await response.json()
    assert not response_body
