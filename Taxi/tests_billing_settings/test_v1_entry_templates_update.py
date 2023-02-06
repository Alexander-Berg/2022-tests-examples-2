import pytest


@pytest.mark.parametrize(
    'update_json, status, expected, expected_count',
    [('update_entry.json', 200, {}, 2)],
)
@pytest.mark.servicetest
@pytest.mark.pgsql(
    'billing_settings', files=['create_template_one_version.sql'],
)
async def test_update_success(
        taxi_billing_settings,
        load_json,
        pgsql,
        update_json,
        status,
        expected,
        expected_count,
):
    entry_template_update = load_json(update_json)
    response = await taxi_billing_settings.post(
        'v1/entry_templates/update', json=entry_template_update,
    )
    assert response.status_code == status
    assert response.json() == expected

    rows = _select_versions_from_db(pgsql)
    assert len(rows) == expected_count

    VERSION_IDX = 5

    assert rows[0][VERSION_IDX] == rows[1][VERSION_IDX] - 1

    END_DATE_IDX = 7
    START_DATE_IDX = 6

    assert rows[0][END_DATE_IDX] == rows[1][START_DATE_IDX]


def _select_versions_from_db(pgsql):
    cursor = pgsql['billing_settings'].cursor()
    cursor.execute(
        f"""
        SELECT * FROM billing_settings.billing_settings
        ORDER BY id
        """,
    )
    return cursor.fetchall()


@pytest.mark.parametrize(
    'update_json, status, expected',
    [
        (
            'update_entry_in_past.json',
            400,
            {
                'code': 'INCORRECT_PARAMETERS',
                'message': 'New version start_date is less than old version start_date',
            },
        ),
        (
            'update_entry.json',
            409,
            {
                'code': 'DUPLICATE_NAME_ERROR',
                'message': 'Version 1 has already been updated',
            },
        ),
        (
            'update_non_existent_entry.json',
            404,
            {
                'code': 'NOT_FOUND_ERROR',
                'message': 'Entry template \'test_entry_templates_update_non_exists\' with version 1 not found',
            },
        ),
    ],
)
@pytest.mark.servicetest
@pytest.mark.pgsql(
    'billing_settings', files=['create_template_two_versions.sql'],
)
async def test_update_fail(
        taxi_billing_settings, load_json, update_json, status, expected,
):
    entry_template_update = load_json(update_json)
    response = await taxi_billing_settings.post(
        'v1/entry_templates/update', json=entry_template_update,
    )
    assert response.status_code == status
    assert response.json() == expected


@pytest.mark.parametrize('update_json, status', [('bad_request.json', 400)])
@pytest.mark.servicetest
@pytest.mark.pgsql(
    'billing_settings', files=['create_template_one_version.sql'],
)
async def test_update_bad_request(
        taxi_billing_settings, load_json, update_json, status,
):
    entry_template_update = load_json(update_json)
    response = await taxi_billing_settings.post(
        'v1/entry_templates/update', json=entry_template_update,
    )
    assert response.status_code == status
