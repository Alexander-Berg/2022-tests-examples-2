import pytest

from tests_effrat_employees import time_utils


@pytest.mark.now(time_utils.NOW.isoformat('T'))
async def test_add(taxi_effrat_employees):
    await taxi_effrat_employees.put(
        '/admin/v1/tags?name=test_taxi_1',
        headers={'X-WFM-Domain': 'taxi'},
        json={'description': 'taxi tag'},
    )
    await taxi_effrat_employees.put(
        '/admin/v1/tags?name=test_taxi_2',
        headers={'X-WFM-Domain': 'taxi'},
        json={'color': 'red', 'description': 'taxi tag'},
    )
    await taxi_effrat_employees.put(
        '/admin/v1/tags?name=test_eats_1',
        headers={'X-WFM-Domain': 'eats'},
        json={'color': 'blue', 'description': 'eats tag'},
    )
    await taxi_effrat_employees.put(
        '/admin/v1/tags?name=test_lavka_1',
        headers={'X-WFM-Domain': 'lavka'},
        json={'color': 'black', 'description': 'lavka tag'},
    )
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


@pytest.mark.now(time_utils.NOW.isoformat('T'))
async def test_update(taxi_effrat_employees):
    await taxi_effrat_employees.put(
        '/admin/v1/tags?name=test_taxi_1',
        headers={'X-WFM-Domain': 'taxi'},
        json={'description': 'taxi tag'},
    )
    await taxi_effrat_employees.put(
        '/admin/v1/tags?name=test_taxi_2',
        headers={'X-WFM-Domain': 'taxi'},
        json={'color': 'red', 'description': 'taxi tag'},
    )
    await taxi_effrat_employees.put(
        '/admin/v1/tags?name=test_taxi_1',
        headers={'X-WFM-Domain': 'taxi'},
        json={'color': 'blue', 'description': 'new taxi tag'},
    )
    response = await taxi_effrat_employees.get(
        '/admin/v1/tags', headers={'X-WFM-Domain': 'taxi'},
    )
    assert response.status_code == 200
    assert response.json()['tags'] == [
        {'name': 'test_taxi_2', 'color': 'red', 'description': 'taxi tag'},
        {
            'name': 'test_taxi_1',
            'color': 'blue',
            'description': 'new taxi tag',
        },
    ]


@pytest.mark.now(time_utils.NOW.isoformat('T'))
async def test_delete(taxi_effrat_employees):
    await taxi_effrat_employees.put(
        '/admin/v1/tags?name=test_taxi_1',
        headers={'X-WFM-Domain': 'taxi'},
        json={'description': 'taxi tag'},
    )
    await taxi_effrat_employees.put(
        '/admin/v1/tags?name=test_taxi_2',
        headers={'X-WFM-Domain': 'taxi'},
        json={'color': 'red', 'description': 'taxi tag'},
    )
    response = await taxi_effrat_employees.get(
        '/admin/v1/tags', headers={'X-WFM-Domain': 'taxi'},
    )
    assert response.status_code == 200
    assert response.json()['tags'] == [
        {'name': 'test_taxi_1', 'description': 'taxi tag'},
        {'name': 'test_taxi_2', 'color': 'red', 'description': 'taxi tag'},
    ]
    await taxi_effrat_employees.delete(
        '/admin/v1/tags?name=test_taxi_2', headers={'X-WFM-Domain': 'taxi'},
    )
    response = await taxi_effrat_employees.get(
        '/admin/v1/tags', headers={'X-WFM-Domain': 'taxi'},
    )
    assert response.status_code == 200
    assert response.json()['tags'] == [
        {'name': 'test_taxi_1', 'description': 'taxi tag'},
    ]


@pytest.mark.now(time_utils.NOW.isoformat('T'))
async def test_delete_nonexistent_tag(taxi_effrat_employees):
    await taxi_effrat_employees.put(
        '/admin/v1/tags?name=test_taxi_1',
        headers={'X-WFM-Domain': 'taxi'},
        json={'description': 'taxi tag'},
    )
    await taxi_effrat_employees.delete(
        '/admin/v1/tags?name=test_taxi_2', headers={'X-WFM-Domain': 'taxi'},
    )
    response = await taxi_effrat_employees.get(
        '/admin/v1/tags', headers={'X-WFM-Domain': 'taxi'},
    )
    assert response.status_code == 200
    assert response.json()['tags'] == [
        {'name': 'test_taxi_1', 'description': 'taxi tag'},
    ]
