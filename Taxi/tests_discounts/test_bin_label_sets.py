import pytest

from tests_discounts import common


@pytest.mark.parametrize(
    'query,expected_data',
    (
        pytest.param(
            {'limit': 10, 'offset': 0, 'search_string': 'first'},
            {
                'limit': 10,
                'offset': 0,
                'total': 1,
                'items': [
                    {'bin_labels': ['label1', 'label2'], 'name': 'first'},
                ],
            },
            id='Search first',
        ),
        pytest.param(
            {'limit': 10, 'offset': 0, 'search_string': 'not_exist'},
            {'limit': 10, 'offset': 0, 'total': 0, 'items': []},
            id='Search not_exist',
        ),
        pytest.param(
            {'limit': 1, 'offset': 0},
            {
                'limit': 1,
                'offset': 0,
                'total': 3,
                'items': [
                    {'bin_labels': ['label1', 'label2'], 'name': 'first'},
                ],
            },
            id='Check limit',
        ),
        pytest.param(
            {'limit': 10, 'offset': 1},
            {
                'limit': 10,
                'offset': 1,
                'total': 3,
                'items': [
                    {'bin_labels': ['label5', 'label6'], 'name': 'last'},
                    {'bin_labels': ['label3', 'label4'], 'name': 'second'},
                ],
            },
            id='Check offset',
        ),
    ),
)
@pytest.mark.pgsql('discounts', files=['bin_label_sets.sql'])
@pytest.mark.now('2018-12-31T23:58:30Z')
async def test_get_bin_label_sets(taxi_discounts, query, expected_data):
    response = await taxi_discounts.get(
        'v1/admin/bin_label_sets',
        headers=common.DEFAULT_DISCOUNTS_HEADER,
        params=query,
    )
    assert response.status == 200, response.json()
    assert response.json() == expected_data


@pytest.mark.parametrize(
    'query,expected_status,expected_data',
    (
        pytest.param(
            {'name': 'first'},
            200,
            {'bin_labels': ['label1', 'label2'], 'name': 'first'},
            id='Ok',
        ),
        pytest.param(
            {'name': 'not_found'},
            404,
            {
                'code': 'NOT_FOUND',
                'message': 'bin_label_set with name \'not_found\' not found',
            },
            id='Not found',
        ),
    ),
)
@pytest.mark.pgsql('discounts', files=['bin_label_sets.sql'])
@pytest.mark.now('2018-12-31T23:58:30Z')
async def test_view_bin_label_sets(
        taxi_discounts, query, expected_status, expected_data,
):
    response = await taxi_discounts.get(
        'v1/admin/bin_label_sets/view',
        headers=common.DEFAULT_DISCOUNTS_HEADER,
        params=query,
    )
    assert response.status == expected_status
    assert response.json() == expected_data


@pytest.mark.parametrize(
    'body,expected_status,expected_check_data,expected_data',
    (
        pytest.param(
            {'name': 'new', 'bin_labels': ['new_label2', 'new_label1']},
            200,
            {
                'change_doc_id': 'new',
                'data': {
                    'name': 'new',
                    'bin_labels': ['new_label1', 'new_label2'],
                },
                'diff': {
                    'new': {
                        'name': 'new',
                        'bin_labels': ['new_label1', 'new_label2'],
                    },
                },
            },
            {'name': 'new', 'bin_labels': ['new_label1', 'new_label2']},
            id='Create new bin_label_set',
        ),
        pytest.param(
            {'name': 'first', 'bin_labels': ['label2', 'new_label']},
            400,
            {
                'code': 'ALREADY_EXISTS',
                'message': 'bin label set with same name already exists',
            },
            {
                'code': 'ALREADY_EXISTS',
                'message': 'bin label set with same name already exists',
            },
            id='already exists',
        ),
    ),
)
@pytest.mark.pgsql('discounts', files=['bin_label_sets.sql'])
@pytest.mark.now('2018-12-31T23:58:30Z')
async def test_post_bin_label_sets(
        taxi_discounts,
        body,
        expected_status,
        expected_check_data,
        expected_data,
):
    response = await taxi_discounts.post(
        'v1/admin/bin_label_sets/check',
        headers=common.DEFAULT_DISCOUNTS_HEADER,
        json=body,
    )
    assert response.status == expected_status, response.json()
    assert response.json() == expected_check_data

    response = await taxi_discounts.post(
        'v1/admin/bin_label_sets',
        headers=common.DEFAULT_DISCOUNTS_HEADER,
        json=body,
    )
    assert response.status == expected_status, response.json()
    assert response.json() == expected_data
