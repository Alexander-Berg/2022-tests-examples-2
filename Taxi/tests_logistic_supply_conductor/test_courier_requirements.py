import pytest

CORRECT_VALUES = [
    {
        'expression': {
            'expressions': [{'operator': 'nor', 'tags': ['foo3', 'foo4']}],
            'operator': 'and',
            'tags': ['foo1', 'foo2'],
        },
        'name': 'foo',
        'reason_title_for_courier': 'foo_title',
        'reason_subtitle_for_courier': 'foo_subtitle',
        'revision': 1,
    },
    {
        'expression': {
            'expressions': [{'operator': 'or', 'tags': ['bar1', 'bar2']}],
            'operator': 'and',
            'professions': ['fisher'],
        },
        'name': 'bar',
        'reason_title_for_courier': 'bar_title',
        'reason_subtitle_for_courier': 'bar_subtitle',
        'revision': 1,
    },
]


@pytest.mark.pgsql(
    'logistic_supply_conductor', files=['pg_courier_requirements.sql'],
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
async def test_requirements_list(
        taxi_logistic_supply_conductor, offset, limit, expected_data,
):
    response = await taxi_logistic_supply_conductor.post(
        'admin/v1/workshift-rule/courier-requirement/list',
        params={'offset': offset, 'limit': limit},
    )

    assert response.status_code == 200

    assert response.json()['total_items_count'] == 2
    assert response.json()['requirements'] == expected_data


@pytest.mark.pgsql(
    'logistic_supply_conductor', files=['pg_courier_requirements.sql'],
)
@pytest.mark.config(
    LOGISTIC_SUPPLY_CONDUCTOR_ENABLED_PROFESSIONS=[
        'bar1',
        'bar2',
        'bar3',
        'bar4',
        'fisher',
    ],
)
@pytest.mark.parametrize(
    'updated_value, expected_data, response_code',
    [
        pytest.param(
            {
                'expression': {
                    'operator': 'nor',
                    'tags': ['bar1', 'bar2'],
                    'exams': {'super_cool': 4},
                },
                'name': 'bar',
                'reason_title_for_courier': 'foo_title',
                'reason_subtitle_for_courier': 'foo_subtitle',
                'revision': 1,
            },
            CORRECT_VALUES,
            400,
            id='update is disabled',
        ),
        pytest.param(
            {
                'expression': {
                    'operator': 'nor',
                    'tags': ['bar1', 'bar2'],
                    'exams': {'super_cool': 4},
                },
                'name': 'bar',
                'reason_title_for_courier': 'foo_title',
                'reason_subtitle_for_courier': 'foo_subtitle',
                'revision': 1,
            },
            [
                CORRECT_VALUES[0],
                {
                    'expression': {
                        'operator': 'nor',
                        'tags': ['bar1', 'bar2'],
                        'exams': {'super_cool': 4},
                    },
                    'name': 'bar',
                    'reason_title_for_courier': 'foo_title',
                    'reason_subtitle_for_courier': 'foo_subtitle',
                    'revision': 2,
                },
            ],
            200,
            marks=pytest.mark.config(
                LOGISTIC_SUPPLY_CONDUCTOR_ADMIN_SETTINGS={
                    'edits': {'enabled': False, 'threshold': 1},
                    'geoareas_types_of_interest': [],
                    'allow_courier_requirement_update': True,
                },
            ),
            id='update is enabled, correct revision',
        ),
        pytest.param(
            {
                'expression': {
                    'operator': 'nor',
                    'tags': ['baz1', 'baz2'],
                    'exams': {'super_cool': 4},
                },
                'name': 'baz',
                'reason_title_for_courier': 'baz_title',
                'reason_subtitle_for_courier': 'baz_subtitle',
            },
            [
                CORRECT_VALUES[0],
                CORRECT_VALUES[1],
                {
                    'expression': {
                        'operator': 'nor',
                        'tags': ['baz1', 'baz2'],
                        'exams': {'super_cool': 4},
                    },
                    'name': 'baz',
                    'reason_title_for_courier': 'baz_title',
                    'reason_subtitle_for_courier': 'baz_subtitle',
                    'revision': 1,
                },
            ],
            200,
            id='correct insert',
        ),
        pytest.param(
            {
                'expression': {
                    'operator': 'or',
                    'professions': ['bar1', 'bar2'],
                    'exams': {'super_cool': 4},
                    'expressions': [
                        {
                            'expression': {
                                'operator': 'and',
                                'professions': ['bar3', 'bar4'],
                            },
                        },
                    ],
                },
                'name': 'baz',
                'reason_title_for_courier': 'baz_title',
                'reason_subtitle_for_courier': 'baz_subtitle',
            },
            CORRECT_VALUES,
            400,
            id='invalid expression, performer can have only one profession',
        ),
        pytest.param(
            {
                'expression': {
                    'operator': 'or',
                    'professions': ['bar5'],
                    'exams': {'super_cool': 4},
                },
                'name': 'baz',
                'reason_title_for_courier': 'baz_title',
                'reason_subtitle_for_courier': 'baz_subtitle',
            },
            CORRECT_VALUES,
            400,
            id='invalid expression, non exist profession',
        ),
        pytest.param(
            {
                'expression': {
                    'operator': 'nor',
                    'tags': ['bar1', 'bar2'],
                    'exams': {'super_cool': 4},
                },
                'name': 'bar',
                'reason_title_for_courier': 'foo_title',
                'reason_subtitle_for_courier': 'foo_subtitle',
            },
            CORRECT_VALUES,
            400,
            id='already exists',
        ),
        pytest.param(
            {
                'expression': {'operator': 'nor', 'tags': ['bar1', 'bar2']},
                'name': 'bar',
                'reason_title_for_courier': 'foo_title',
                'reason_subtitle_for_courier': 'foo_title',
                'revision': 42,
            },
            CORRECT_VALUES,
            409,
            marks=pytest.mark.config(
                LOGISTIC_SUPPLY_CONDUCTOR_ADMIN_SETTINGS={
                    'edits': {'enabled': False, 'threshold': 1},
                    'geoareas_types_of_interest': [],
                    'allow_courier_requirement_update': True,
                },
            ),
            id='update is enabled, incorrect revision',
        ),
    ],
)
async def test_requirements_upsert(
        taxi_logistic_supply_conductor,
        updated_value,
        expected_data,
        response_code,
):
    dry_response = await taxi_logistic_supply_conductor.post(
        'admin/v1/workshift-rule/courier-requirement/upsert',
        json=updated_value,
        params={'dry_run': True},
    )

    assert dry_response.status_code == response_code

    dry_list_response = await taxi_logistic_supply_conductor.post(
        'admin/v1/workshift-rule/courier-requirement/list',
    )

    assert dry_list_response.status_code == 200
    assert dry_list_response.json()['requirements'] == CORRECT_VALUES

    response = await taxi_logistic_supply_conductor.post(
        'admin/v1/workshift-rule/courier-requirement/upsert',
        json=updated_value,
    )

    assert response.status_code == response_code

    list_response = await taxi_logistic_supply_conductor.post(
        'admin/v1/workshift-rule/courier-requirement/list',
    )

    assert list_response.status_code == 200
    assert list_response.json()['requirements'] == expected_data
