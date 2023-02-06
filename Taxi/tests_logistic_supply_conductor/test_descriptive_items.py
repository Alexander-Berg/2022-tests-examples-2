import pytest

CORRECT_VALUES = [
    {
        'name': 'name1',
        'title': 'foo',
        'text': 'bar',
        'content_code_hint': 'free_minutes',
        'revision': 1,
    },
    {'name': 'name2', 'title': 'bar', 'text': 'baz', 'revision': 1},
]


@pytest.mark.pgsql(
    'logistic_supply_conductor', files=['pg_descriptive_items.sql'],
)
@pytest.mark.parametrize(
    'offset, limit, expected_data',
    [
        (0, 10, CORRECT_VALUES),
        (0, 1, CORRECT_VALUES[:1]),
        (1, 1, CORRECT_VALUES[1:]),
        (10, 10, []),
    ],
)
async def test_descriptive_items_list(
        taxi_logistic_supply_conductor, offset, limit, expected_data,
):
    response = await taxi_logistic_supply_conductor.post(
        'admin/v1/workshift-rule/descriptive-item/list',
        params={'offset': offset, 'limit': limit},
    )

    assert response.status_code == 200

    assert response.json()['total_items_count'] == 2
    assert response.json()['descriptive_items'] == expected_data


@pytest.mark.pgsql(
    'logistic_supply_conductor', files=['pg_descriptive_items.sql'],
)
@pytest.mark.parametrize(
    'updated_value, expected_data, response_code',
    [
        pytest.param(
            {'name': 'name2', 'title': 'baz', 'text': 'foo', 'revision': 1},
            CORRECT_VALUES,
            400,
            id='update is disabled',
        ),
        pytest.param(
            {'name': 'name2', 'title': 'baz', 'text': 'foo', 'revision': 1},
            [
                CORRECT_VALUES[0],
                {
                    'name': 'name2',
                    'title': 'baz',
                    'text': 'foo',
                    'revision': 2,
                },
            ],
            200,
            marks=pytest.mark.config(
                LOGISTIC_SUPPLY_CONDUCTOR_ADMIN_SETTINGS={
                    'edits': {'enabled': False, 'threshold': 1},
                    'geoareas_types_of_interest': [],
                    'allow_descriptive_item_update': True,
                },
            ),
            id='update is enabled, correct revision',
        ),
        pytest.param(
            {'name': 'name3', 'title': 'baz', 'text': 'foo'},
            [
                CORRECT_VALUES[0],
                CORRECT_VALUES[1],
                {
                    'name': 'name3',
                    'title': 'baz',
                    'text': 'foo',
                    'revision': 1,
                },
            ],
            200,
            id='correct insert',
        ),
        pytest.param(
            {'name': 'name1', 'title': 'baz', 'text': 'bar'},
            CORRECT_VALUES,
            400,
            id='already exists',
        ),
        pytest.param(
            {'name': 'name1', 'title': 'baz', 'text': 'bar', 'revision': 42},
            CORRECT_VALUES,
            409,
            marks=pytest.mark.config(
                LOGISTIC_SUPPLY_CONDUCTOR_ADMIN_SETTINGS={
                    'edits': {'enabled': False, 'threshold': 1},
                    'geoareas_types_of_interest': [],
                    'allow_descriptive_item_update': True,
                },
            ),
            id='update is enabled, incorrect revision',
        ),
    ],
)
async def test_descriptive_items_upsert(
        taxi_logistic_supply_conductor,
        updated_value,
        expected_data,
        response_code,
):
    dry_response = await taxi_logistic_supply_conductor.post(
        'admin/v1/workshift-rule/descriptive-item/upsert',
        json=updated_value,
        params={'dry_run': True},
    )
    assert dry_response.status_code == response_code

    dry_list_response = await taxi_logistic_supply_conductor.post(
        'admin/v1/workshift-rule/descriptive-item/list',
    )

    assert dry_list_response.status_code == 200
    assert dry_list_response.json()['descriptive_items'] == CORRECT_VALUES

    response = await taxi_logistic_supply_conductor.post(
        'admin/v1/workshift-rule/descriptive-item/upsert', json=updated_value,
    )

    assert response.status_code == response_code

    list_response = await taxi_logistic_supply_conductor.post(
        'admin/v1/workshift-rule/descriptive-item/list',
    )

    assert list_response.status_code == 200
    assert list_response.json()['descriptive_items'] == expected_data
