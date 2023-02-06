async def test_lab_labs_db(taxi_persey_labs, load_json, fill_labs):
    fill_labs.load_lab_entities(load_json('labs.json'))
    fill_labs.load_employees(
        ['citilab_1', 'citilab_2'], load_json('employees.json'),
    )

    response = await taxi_persey_labs.get(
        '/lab/v1/labs', headers={'X-External-Service': 'citilab'},
    )
    # Status code must be checked for every request
    assert response.status_code == 200
    assert response.json() == {
        'labs': [
            {
                'id': 'citilab_1',
                'name': 'Ситилаб1',
                'address': {'position': [35.5, 55.5], 'text': 'Somewhere'},
                'bucket_owners': [
                    {
                        'login': 'citilab_1_emp1',
                        'fullname': 'Кеков Кек Кекович',
                    },
                    {'login': 'citilab_1_emp2', 'fullname': 'Каков Как'},
                ],
            },
            {
                'id': 'citilab_2',
                'name': 'Ситилаб2',
                'address': {
                    'position': [35.5, 55.5],
                    'text': 'Somewhere else',
                },
                'bucket_owners': [
                    {
                        'login': 'citilab_2_emp1',
                        'fullname': 'Кеков Кек Кекович',
                    },
                    {'login': 'citilab_2_emp2', 'fullname': 'Каков Как'},
                ],
            },
        ],
    }
