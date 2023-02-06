import pytest

from tests_effrat_employees import time_utils


@pytest.mark.now(time_utils.NOW.isoformat('T'))
@pytest.mark.pgsql('effrat_employees', files=['add_tags.sql'])
async def test_get(taxi_effrat_employees, mock_staff_groups):
    response = await taxi_effrat_employees.get(
        '/admin/v1/tags', headers={'X-WFM-Domain': 'taxi'},
    )
    assert response.status_code == 200
    assert response.json()['tags'] == [
        {'name': 'test_taxi_1', 'description': 'taxi tag'},
        {'name': 'test_taxi_2', 'color': 'red', 'description': 'taxi tag'},
    ]

    response = await taxi_effrat_employees.get(
        '/admin/v1/tags', headers={'X-WFM-Domain': 'eats'},
    )
    assert response.status_code == 200
    assert response.json()['tags'] == [
        {'name': 'test_eats_1', 'color': 'blue', 'description': 'eats tag'},
    ]

    response = await taxi_effrat_employees.get(
        '/admin/v1/tags', headers={'X-WFM-Domain': 'lavka'},
    )
    assert response.status_code == 200
    assert response.json()['tags'] == [
        {'name': 'test_lavka_1', 'color': 'black', 'description': 'lavka tag'},
    ]
