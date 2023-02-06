import pytest


@pytest.mark.parametrize(
    'discount_series_id,has_limit,expected_status,expected_content',
    (
        (
            'discount2',
            True,
            200,
            {
                'discount': {
                    'calculation_params': {
                        'calculation_method': 'calculation_formula',
                        'discount_calculator': {
                            'calculation_formula_v1_a1': 0.0,
                            'calculation_formula_v1_a2': 0.0,
                            'calculation_formula_v1_c1': 1.0,
                            'calculation_formula_v1_c2': 1.0,
                            'calculation_formula_v1_p1': 50.0,
                            'calculation_formula_v1_p2': 50.0,
                            'calculation_formula_v1_threshold': 300.0,
                        },
                        'max_value': 0.5,
                        'min_value': 0.0,
                        'newbie_max_coeff': 1.5,
                        'newbie_num_coeff': 0.15,
                        'round_digits': 2,
                    },
                    'description': 'discount2',
                    'discount_class': 'valid_class',
                    'limit': {
                        'label': 'Limit 2',
                        'ref': 'discount2_limit_id',
                        'windows': [
                            {
                                'label': 'label of limit 1',
                                'size': 10,
                                'threshold': 100,
                                'type': 'tumbling',
                                'value': '1',
                            },
                        ],
                    },
                    'limit_id': 'discount2_limit_id',
                    'discount_method': 'subvention-fix',
                    'discount_series_id': 'discount2',
                    'enabled': True,
                    'reference_entity_id': 2,
                    'select_params': {
                        'classes': ['econom'],
                        'datetime_params': {
                            'date_from': '2019-01-01T00:00:00',
                            'timezone_type': 'utc',
                        },
                        'discount_target': 'tag_service',
                        'geoarea_a': 'Himki',
                        'geoarea_b': 'Aprelevka',
                        'payment_types': ['applepay', 'card', 'cash'],
                        'user_tags': ['tag3', 'tag4'],
                        'intermediate_points_prohibited': True,
                    },
                    'zones_list': [1],
                },
            },
        ),
        (
            'discount2',
            False,
            200,
            {
                'discount': {
                    'calculation_params': {
                        'calculation_method': 'calculation_formula',
                        'discount_calculator': {
                            'calculation_formula_v1_a1': 0.0,
                            'calculation_formula_v1_a2': 0.0,
                            'calculation_formula_v1_c1': 1.0,
                            'calculation_formula_v1_c2': 1.0,
                            'calculation_formula_v1_p1': 50.0,
                            'calculation_formula_v1_p2': 50.0,
                            'calculation_formula_v1_threshold': 300.0,
                        },
                        'max_value': 0.5,
                        'min_value': 0.0,
                        'newbie_max_coeff': 1.5,
                        'newbie_num_coeff': 0.15,
                        'round_digits': 2,
                    },
                    'description': 'discount2',
                    'discount_class': 'valid_class',
                    'limit_id': 'discount2_limit_id',
                    'discount_method': 'subvention-fix',
                    'discount_series_id': 'discount2',
                    'enabled': True,
                    'reference_entity_id': 2,
                    'select_params': {
                        'classes': ['econom'],
                        'datetime_params': {
                            'date_from': '2019-01-01T00:00:00',
                            'timezone_type': 'utc',
                        },
                        'discount_target': 'tag_service',
                        'geoarea_a': 'Himki',
                        'geoarea_b': 'Aprelevka',
                        'payment_types': ['applepay', 'card', 'cash'],
                        'user_tags': ['tag3', 'tag4'],
                        'intermediate_points_prohibited': True,
                    },
                    'zones_list': [1],
                },
            },
        ),
    ),
)
@pytest.mark.config(
    DISCOUNTS_ADMIN_EXTERNAL_CLIENTS_ENABLED={
        'billing-limits': True,
        'discounts': True,
    },
)
async def test_v1_view_discount(
        taxi_discounts_admin,
        discount_series_id,
        expected_status,
        expected_content,
        mockserver,
        tvm_ticket,
        has_limit,
):
    @mockserver.json_handler('/discounts/v1/admin/discounts/view')
    def _discounts_mock(request):
        return {
            'discount': {
                'calculation_params': {
                    'calculation_method': 'calculation_formula',
                    'discount_calculator': {
                        'calculation_formula_v1_a1': 0.0,
                        'calculation_formula_v1_a2': 0.0,
                        'calculation_formula_v1_c1': 1.0,
                        'calculation_formula_v1_c2': 1.0,
                        'calculation_formula_v1_p1': 50.0,
                        'calculation_formula_v1_p2': 50.0,
                        'calculation_formula_v1_threshold': 300.0,
                    },
                    'max_value': 0.5,
                    'min_value': 0.0,
                    'newbie_max_coeff': 1.5,
                    'newbie_num_coeff': 0.15,
                    'round_digits': 2,
                },
                'description': 'discount2',
                'discount_class': 'valid_class',
                'limit_id': 'discount2_limit_id',
                'discount_method': 'subvention-fix',
                'discount_series_id': 'discount2',
                'enabled': True,
                'reference_entity_id': 2,
                'select_params': {
                    'classes': ['econom'],
                    'datetime_params': {
                        'date_from': '2019-01-01T00:00:00',
                        'timezone_type': 'utc',
                    },
                    'intermediate_points_prohibited': True,
                    'discount_target': 'tag_service',
                    'geoarea_a': 'Himki',
                    'geoarea_b': 'Aprelevka',
                    'payment_types': ['applepay', 'card', 'cash'],
                    'user_tags': ['tag3', 'tag4'],
                },
                'zones_list': [1],
            },
        }

    @mockserver.json_handler('/billing-limits/v1/get')
    def _limits_mock(request):
        if has_limit:
            return {
                'currency': 'rub',
                'label': 'Limit 2',
                'ref': 'discount2_limit_id',
                'account_id': 'discount2_limit_id',
                'tags': [],
                'approvers': ['staff_login'],
                'tickets': ['TAXIBACKEND-11'],
                'windows': [
                    {
                        'type': 'tumbling',
                        'value': '1',
                        'size': 10,
                        'label': 'label of limit 1',
                    },
                ],
            }
        raise mockserver.TimeoutError()

    response = await taxi_discounts_admin.get(
        '/v1/admin/discounts/view',
        headers={'X-Ya-Service-Ticket': tvm_ticket},
        params={'discount_series_id': discount_series_id},
    )

    content = response.json()
    assert response.status_code == 200, content
    content['discount']['select_params']['payment_types'].sort()
    content['discount']['select_params']['user_tags'].sort()
    assert content == expected_content
