import pytest


async def test_bad_request_w_empty_query_parameter(taxi_subvention_admin):
    response = await taxi_subvention_admin.get(
        '/internal/subvention-admin/v1/settings',
    )
    assert response.status_code == 400


@pytest.mark.parametrize(
    'query',
    [
        pytest.param(
            # query
            {'name': 'bad_setting_name'},
        ),
    ],
)
async def test_bad_request_w_wrong_query_parameter(
        taxi_subvention_admin, query,
):
    response = await taxi_subvention_admin.get(
        '/internal/subvention-admin/v1/settings', params=query,
    )
    assert response.status_code == 400


@pytest.mark.parametrize(
    'query, expected_setting',
    [
        pytest.param(
            # query
            {'name': 'smart_subventions_admin'},
            # expected_setting
            {'geoarea_disabled': True},
            marks=[
                pytest.mark.config(
                    BILLING_SUBVENTIONS_X_TARIFF_EDITOR_SMART_SUBVENTIONS_CONFIG={  # noqa: E501
                        'geoarea_disabled': True,
                    },
                ),
            ],
        ),
        pytest.param(
            # query
            {'name': 'smart_subventions_admin'},
            # expected_setting
            {
                'geoarea_disabled': False,
                'intervals': {
                    'night': 0,
                    'morning': 7,
                    'daytime': 16,
                    'evening': 19,
                },
            },
            marks=[
                pytest.mark.config(
                    BILLING_SUBVENTIONS_X_TARIFF_EDITOR_SMART_SUBVENTIONS_CONFIG={  # noqa: E501
                        'geoarea_disabled': False,
                        'intervals': {
                            'night': 0,
                            'morning': 7,
                            'daytime': 16,
                            'evening': 19,
                        },
                    },
                ),
            ],
        ),
        pytest.param(
            # query
            {'name': 'subventions_max_duration_admin'},
            # expected_setting
            123456789,
            marks=[pytest.mark.config(SUBVENTIONS_MAX_DURATION=123456789)],
        ),
    ],
)
async def test_smart_subvention_receiving_w_disabled_geoarea(
        taxi_subvention_admin, query, expected_setting,
):
    response = await taxi_subvention_admin.get(
        '/internal/subvention-admin/v1/settings', params=query,
    )
    assert response.status_code == 200
    assert expected_setting == response.json()
