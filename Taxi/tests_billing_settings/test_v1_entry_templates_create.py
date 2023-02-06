import pytest


@pytest.mark.parametrize(
    'query_json, status, expected, expected_count',
    [('request.json', 200, {}, 1), ('full_request.json', 200, {}, 1)],
)
@pytest.mark.servicetest
@pytest.mark.pgsql('billing_settings')
async def test_create_check(
        taxi_billing_settings,
        load_json,
        pgsql,
        query_json,
        status,
        expected,
        expected_count,
):
    entry_template_query = load_json(query_json)
    response = await taxi_billing_settings.post(
        'v1/entry_templates/create', json=entry_template_query,
    )
    assert response.status_code == status
    assert response.json() == expected
    _assert_entry_templates_count(pgsql, expected_count)


def _assert_entry_templates_count(pgsql, expected_count):
    cursor = pgsql['billing_settings'].cursor()
    cursor.execute(
        f"""
        SELECT COUNT(*) FROM billing_settings.billing_settings
        """,
    )
    entry_templates_count = cursor.fetchone()[0]
    assert entry_templates_count == expected_count


@pytest.mark.parametrize(
    'query_json, status, expected',
    [
        (
            'request.json',
            409,
            {
                'code': 'DUPLICATE_NAME_ERROR',
                'message': 'Template named \'test_entry_template_creation\' already exists',
            },
        ),
    ],
)
@pytest.mark.servicetest
@pytest.mark.pgsql('billing_settings', files=['create_entry_template.sql'])
async def test_create_duplicate_template(
        taxi_billing_settings, load_json, query_json, status, expected,
):
    entry_template_query = load_json(query_json)
    response = await taxi_billing_settings.post(
        'v1/entry_templates/create', json=entry_template_query,
    )
    assert response.status_code == status
    assert response.json() == expected


@pytest.mark.parametrize('query_json, status', [('bad_request.json', 400)])
@pytest.mark.servicetest
@pytest.mark.pgsql('billing_settings')
async def test_create_bad_request(
        taxi_billing_settings, load_json, query_json, status,
):
    entry_template_query = load_json(query_json)
    response = await taxi_billing_settings.post(
        'v1/entry_templates/create', json=entry_template_query,
    )
    assert response.status_code == status
