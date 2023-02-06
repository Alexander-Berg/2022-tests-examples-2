from typing import Optional

import pytest

CONTROL_SHARE = 20
BUDGET_CALCULATION_SETTINGS = {
    'surge_rate_pushes_bound': 0.3,
    'window_for_smoothing': 209,
    'window_for_derivation': 15,
    'break_point_value': 1.07,
    'min_city_population': 100000,
    'min_data_size': 300,
    'min_avg_discount_for_push': 0.1,
    'peak_height_ratio': 100.0,
}

CONFIG = {
    'DISCOUNTS_OPERATION_CALCULATIONS_RECOMMEND_BUDGET': {
        'budget_calculation': BUDGET_CALCULATION_SETTINGS,
    },
    'DISCOUNTS_OPERATION_CALCULATIONS_ALGORITHMS_CONFIGS': {
        'kt': {'control_share': CONTROL_SHARE},
    },
}


class TestValidateFixedDiscounts:
    suggest_id = 1

    @pytest.fixture(scope='function')
    def send_request(self, web_app_client):
        async def send(
                url: str,
                discount_value: float,
                request_body: Optional[dict] = None,
        ):
            response = await web_app_client.post(
                url,
                json={
                    'suggest_id': self.suggest_id,
                    'all_fixed_discounts': [
                        {
                            'algorithm_id': 'kt',
                            'fixed_discounts': [
                                {
                                    'segment': 'control',
                                    'discount_value': discount_value,
                                },
                            ],
                        },
                    ],
                    **(request_body or {}),
                },
            )

            return response

        return send

    @pytest.fixture(scope='function')
    def discount_bounds(self, pgsql):
        cursor = pgsql['discounts_operation_calculations'].cursor()
        cursor.execute(
            'SELECT calc_segments_params '
            'FROM discounts_operation_calculations.suggests '
            f'WHERE id = {self.suggest_id}',
        )
        (params,) = next(cursor)
        cursor.close()
        return (
            params['common_params']['min_discount'],
            params['common_params']['max_discount'],
        )

    @pytest.mark.pgsql(
        'discounts_operation_calculations',
        files=[
            'fill_pg_suggests_v2.sql',
            'fill_pg_calc_segment_stats_tasks.sql',
            'fill_pg_segment_stats_all.sql',
        ],
    )
    @pytest.mark.parametrize(
        'url, params',
        [
            ('/v2/statistics', {}),
            ('/v2/suggests/recommended_budget/', {}),
            (
                '/v2/suggests/calc_discounts/',
                {'max_absolute_value': 12345, 'budget': 400503},
            ),
        ],
    )
    @pytest.mark.config(**CONFIG)
    async def test_fallback_discount_bounds(
            self, send_request, url, params, discount_bounds,
    ):
        min_disc, max_disc = discount_bounds
        discount_value = min_disc - 15

        resp = await send_request(url, discount_value, params)
        content = await resp.json()
        assert resp.status == 400
        assert content == {
            'code': 'BadRequest::WrongParams',
            'message': (
                f'Invalid value for discount_value: value '
                f'"{discount_value}" must be not less than '
                f'suggest\'s min_discount = {min_disc}'
            ),
        }

        discount_value = max_disc + 10
        resp = await send_request(url, discount_value, params)
        content = await resp.json()
        assert resp.status == 400
        assert content == {
            'code': 'BadRequest::WrongParams',
            'message': (
                f'Invalid value for discount_value: value '
                f'"{discount_value}" must be not greater than suggest\'s '
                f'max_discount = {max_disc}'
            ),
        }

    @pytest.mark.pgsql(
        'discounts_operation_calculations',
        files=[
            'fill_pg_suggests_v2.sql',
            'fill_pg_calc_segment_stats_tasks.sql',
            'fill_pg_segment_stats_all.sql',
        ],
    )
    @pytest.mark.parametrize(
        'url, params',
        [
            ('/v2/statistics', {}),
            ('/v2/suggests/recommended_budget/', {}),
            (
                '/v2/suggests/calc_discounts/',
                {'max_absolute_value': 12345, 'budget': 400503},
            ),
        ],
    )
    @pytest.mark.config(**CONFIG)
    async def test_discount_multiple_of(self, send_request, url, params):
        discount_value = 8
        resp = await send_request(url, discount_value, params)
        content = await resp.json()
        assert resp.status == 400
        assert content == {
            'code': 'BadRequest::WrongParams',
            'message': (
                f'Invalid value for discount_value: '
                f'value "{discount_value}" must be multiple of 3'
            ),
        }
