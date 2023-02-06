import pytest

SLA_PARAMS = {'a': 1.0, 'b': 1.0, 'c': 1.0, 'd': 1.0, 'max_coef': 1.0}

REGULAR1 = {
    'da_distance_ratio': 1.0,
    'da_time_ratio': 2.0,
    'formula_type': 'regular_mode',
    'home_cancel_prob': 3.0,
    'home_distance_ratio': 4.0,
    'home_time_ratio': 5.0,
    'min_home_distance_ratio': 6.0,
    'min_home_time_ratio': 7.0,
    'min_order_distance': 8,
    'min_order_time': 9,
    'sla_params': SLA_PARAMS,
}

REGULAR_OFFER1 = {
    'da_distance_ratio': 1.0,
    'da_time_ratio': 2.0,
    'formula_type': 'regular_offer_mode',
    'home_cancel_prob': 3.0,
    'home_distance_ratio': 4.0,
    'home_time_ratio': 5.0,
    'min_b_surge': 10.0,
    'min_home_distance_ratio': 6.0,
    'min_home_time_ratio': 7.0,
    'min_order_distance': 8,
    'min_order_time': 9,
    'min_surge_gradient': 11.0,
}

REGULAR_OFFER2 = {
    'da_distance_ratio': 11.0,
    'da_time_ratio': 12.0,
    'formula_type': 'regular_offer_mode',
    'home_cancel_prob': 13.0,
    'home_distance_ratio': 14.0,
    'home_time_ratio': 15.0,
    'min_b_surge': 110.0,
    'min_home_distance_ratio': 16.0,
    'min_home_time_ratio': 17.0,
    'min_order_distance': 18,
    'min_order_time': 19,
    'min_surge_gradient': 111.0,
    'sla_params': SLA_PARAMS,
}

REGULAR_OFFER3 = {
    'da_distance_ratio': 21.0,
    'da_time_ratio': 22.0,
    'formula_type': 'regular_offer_mode',
    'home_cancel_prob': 23.0,
    'home_distance_ratio': 24.0,
    'home_time_ratio': 25.0,
    'min_b_surge': 210.0,
    'min_home_distance_ratio': 26.0,
    'min_home_time_ratio': 27.0,
    'min_order_distance': 28,
    'min_order_time': 29,
    'min_surge_gradient': 211.0,
}

DESTINATION_DISTRICT1 = {
    'dh_time_cmp_coeff': 4.0,
    'formula_type': 'destination_district_mode',
    'max_bh_air_dist': 1.0,
    'max_bh_time': 2.0,
}

DESTINATION_DISTRICT2 = {
    'dh_time_cmp_coeff': 14.0,
    'formula_type': 'destination_district_mode',
    'max_bh_air_dist': 11.0,
    'max_bh_time': 12.0,
}


DESTINATION_DISTRICT3 = {
    'dh_time_cmp_coeff': 24.0,
    'formula_type': 'destination_district_mode',
    'max_bh_air_dist': 21.0,
    'max_bh_time': 22.0,
}


@pytest.mark.pgsql('reposition_matcher', files=['modes_zones.sql'])
async def test_get_empty(taxi_reposition_matcher):
    response = await taxi_reposition_matcher.get(
        'v1/admin/deviation_formulas/list?zone=moscow',
    )
    assert response.status_code == 200
    assert response.json() == {}


@pytest.mark.pgsql(
    'reposition_matcher', files=['modes_zones.sql', 'formulas.sql'],
)
async def test_get(taxi_reposition_matcher):
    response = await taxi_reposition_matcher.get(
        'v1/admin/deviation_formulas/list?zone=moscow',
    )
    assert response.status_code == 200
    assert response.json() == {
        'District': {
            'bonus': DESTINATION_DISTRICT1,
            'riding': {'formula_type': 'area_mode'},
            'submodes': {
                '30': {'bonus': DESTINATION_DISTRICT3, 'riding': REGULAR1},
                '90': {'riding': DESTINATION_DISTRICT2},
            },
        },
        'home': {'riding': REGULAR1},
        'poi': {
            'riding': REGULAR_OFFER1,
            'submodes': {
                'fast': {
                    'bonus': REGULAR1,
                    'riding': REGULAR_OFFER2,
                    'fallback': {'bonus': REGULAR1, 'riding': REGULAR_OFFER3},
                },
                'slow': {'bonus': REGULAR_OFFER3, 'riding': REGULAR_OFFER2},
            },
        },
        'surge': {
            'riding': {
                'formula_type': 'surge_mode',
                'min_b_lrsp_time': 1.0,
                'min_b_surge': 2.0,
                'min_order_distance': 3,
                'min_order_time': 4,
            },
        },
    }


@pytest.mark.pgsql('reposition_matcher', files=['modes_zones.sql'])
async def test_get_invalid_zone(taxi_reposition_matcher):
    response = await taxi_reposition_matcher.get(
        'v1/admin/deviation_formulas/list?zone=kek',
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': 'Zone \'kek\' not found',
    }
