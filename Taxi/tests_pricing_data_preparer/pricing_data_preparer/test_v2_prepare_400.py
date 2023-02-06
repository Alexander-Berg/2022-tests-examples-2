# pylint: disable=redefined-outer-name, import-only-modules
# flake8: noqa F401
import pytest


from .plugins.mock_surge import surger, mock_surger


@pytest.mark.config(
    PRICING_DATA_PREPARER_ROUTER_ENABLED={'__default__': False},
)
@pytest.mark.parametrize(
    'req, error_code',
    [
        (
            {
                'categories': ['econom'],
                'order_type': 'APPLICATION',
                'classes_requirements': {'econom': {'nosmoking': 0}},
                'waypoints': [[37.607429, 55.751352]],
                'zone': 'moscow',
                'tolls': 'DENY',
                'modifications_scope': 'taxi',
            },
            'BAD_REQUIREMENTS',
        ),
        (
            {
                'categories': ['econom'],
                'order_type': 'APPLICATION',
                'classes_requirements': {'econom': {'invalid_double': 0.0}},
                'waypoints': [[37.607429, 55.751352]],
                'zone': 'moscow',
                'tolls': 'DENY',
                'modifications_scope': 'taxi',
            },
            'BAD_REQUIREMENTS',
        ),
        (
            {
                'categories': ['econom'],
                'order_type': 'APPLICATION',
                'classes_requirements': {'econom': {'invalid_array': [1, 2]}},
                'waypoints': [[37.607429, 55.751352]],
                'zone': 'moscow',
                'tolls': 'DENY',
                'modifications_scope': 'taxi',
            },
            'BAD_REQUIREMENTS',
        ),
        (
            {
                'categories': ['econom'],
                'order_type': 'APPLICATION',
                'classes_requirements': {},
                'waypoints': [[30.273033, 59.799774]],
                'zone': 'ivalid',
                'tolls': 'DENY',
                'modifications_scope': 'taxi',
            },
            'UNABLE_TO_MATCH_TARIFF',
        ),
        (
            {
                'categories': ['invalid'],
                'order_type': 'APPLICATION',
                'classes_requirements': {},
                'waypoints': [[37.607429, 55.751352]],
                'zone': 'moscow',
                'tolls': 'DENY',
                'modifications_scope': 'taxi',
            },
            'NO_CATEGORIES_MATCHED',
        ),
        (
            {
                'categories': ['econom'],
                'order_type': 'APPLICATION',
                'classes_requirements': {
                    'econom': {
                        'childchair': 3,
                        'nosmoking': True,
                        'childchair_for_child_tariff': [3],
                        'luggage': 'warning only',
                    },
                },
                'waypoints': [[37.607429, 55.751352]],
                'zone': 'moscow',
                'tolls': 'DENY',
                'modifications_scope': 'taxi',
            },
            None,
        ),
    ],
)
async def test_v2_prepare_400(
        taxi_pricing_data_preparer, surger, mock_surger, req, error_code,
):
    surger.set_user_id(None)

    response = await taxi_pricing_data_preparer.post('v2/prepare', json=req)
    assert response.status_code == 400 if error_code else 200

    if error_code:
        resp = response.json()
        assert 'code' in resp and resp['code'] == error_code
