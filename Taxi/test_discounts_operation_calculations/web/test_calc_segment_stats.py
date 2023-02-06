import typing as tp

import pytest


@pytest.mark.config(
    DISCOUNTS_OPERATION_CALCULATIONS_ALGORITHMS_CONFIGS={
        'algorithm1': {
            'description': 'test description',
            'metric_name': 'test_metric_name',
        },
        'kt2_smart_script': {
            'description': 'kt2_smart_script desc',
            'metric_name': 'kt2_smart_script metric_name',
        },
    },
)
async def test_check_ignore_companies(web_app_client):
    response = await web_app_client.post(
        '/v2/statistics/calc_segment_stats',
        headers={'X-Yandex-Login': 'test_user'},
        json={
            'common_params': {
                'discounts_city': 'test_city',
                'companies': [],
                'tariffs': ['econom', 'business'],
                'min_discount': 6,
                'max_discount': 30,
            },
            'custom_params': [
                {
                    'algorithm_id': 'kt2_smart_script',
                    'max_surge': 1.2,
                    'with_push': False,
                },
                {'algorithm_id': 'kt2', 'max_surge': 1.2, 'with_push': False},
            ],
        },
    )
    assert response.status == 400
    content = await response.json()

    assert content == {
        'code': 'BadRequest::WrongParams',
        'message': 'Cannot ignore companies for algo kt2!',
    }


@pytest.mark.config(
    DISCOUNTS_OPERATION_CALCULATIONS_ALGORITHMS_CONFIGS={
        'algorithm1': {
            'description': 'test description',
            'metric_name': 'test_metric_name',
            'ignore_companies': True,
        },
        'kt2_smart_script': {
            'description': 'kt2_smart_script desc',
            'metric_name': 'kt2_smart_script metric_name',
        },
    },
)
async def test_check_ignore_companies_allow(web_app_client):
    response = await web_app_client.post(
        '/v2/statistics/calc_segment_stats',
        headers={'X-Yandex-Login': 'test_user'},
        json={
            'common_params': {
                'discounts_city': 'test_city',
                'companies': [],
                'tariffs': ['econom', 'business'],
                'min_discount': 6,
                'max_discount': 30,
            },
            'custom_params': [
                {
                    'algorithm_id': 'kt2_smart_script',
                    'max_surge': 1.2,
                    'with_push': False,
                },
                {
                    'algorithm_id': 'algorithm1',
                    'max_surge': 1.2,
                    'with_push': False,
                },
            ],
        },
    )
    assert response.status == 200
    content = await response.json()

    assert content == {'suggest_id': 1}


async def test_small_fallback_disc(web_app_client):
    response = await web_app_client.post(
        '/v2/statistics/calc_segment_stats',
        headers={'X-Yandex-Login': 'test_user'},
        json={
            'common_params': {
                'discounts_city': 'test_city',
                'companies': ['ololo'],
                'tariffs': ['econom', 'business'],
                'min_discount': 6,
                'max_discount': 30,
            },
            'custom_params': [
                {
                    'algorithm_id': 'kt2_smart_script',
                    'max_surge': 1.2,
                    'with_push': False,
                },
                {
                    'algorithm_id': 'kt2',
                    'max_surge': 1.2,
                    'with_push': True,
                    'fallback_discount': 2,
                },
            ],
        },
    )
    assert response.status == 400
    content = await response.json()

    assert content == {
        'code': 'REQUEST_VALIDATION_ERROR',
        'details': {
            'reason': (
                'Invalid value for fallback_discount: 2 must be a value '
                'greater than or equal to 3'
            ),
        },
        'message': 'Some parameters are invalid',
    }


class TestValidation:
    URL = '/v2/statistics/calc_segment_stats'

    @pytest.fixture(scope='function')
    def send_request(self, web_app_client):
        async def send(
                min_discount: float = 0,
                max_discount: float = 30,
                fallback_discount: tp.Optional[float] = None,
                surge=1.2,
                with_push=None,
        ):
            params: tp.Dict[str, tp.Any] = {
                'common_params': {
                    'discounts_city': 'test_city',
                    'companies': [],
                    'tariffs': ['econom', 'business'],
                    'min_discount': min_discount,
                    'max_discount': max_discount,
                },
                'custom_params': [
                    {'algorithm_id': 'kt2_smart_script', 'max_surge': surge},
                ],
            }

            if fallback_discount is not None:
                params['custom_params'][0][
                    'fallback_discount'
                ] = fallback_discount

            if with_push is not None:
                params['custom_params'][0]['with_push'] = with_push

            response = await web_app_client.post(
                self.URL, headers={'X-Yandex-Login': 'test_user'}, json=params,
            )

            return response

        return send

    async def test_discount_bounds_order(self, send_request):
        resp = await send_request(56, 12, 24)
        content = await resp.json()
        assert resp.status == 400
        assert content == {
            'code': 'BadRequest::WrongParams',
            'message': 'min_discount should be less than max_discount',
        }

    async def test_fallback_discount_bounds(self, send_request):
        discount_value = 3
        min_disc = 12
        max_disc = 64

        resp = await send_request(
            min_disc, max_disc, fallback_discount=discount_value,
        )
        content = await resp.json()
        assert resp.status == 400
        assert content == {
            'code': 'BadRequest::WrongParams',
            'message': (
                f'fallback_discount value "{discount_value}" must be not less '
                f'than suggest\'s min_discount = {min_disc}'
            ),
        }

        discount_value = 66
        resp = await send_request(
            min_disc, max_disc, fallback_discount=discount_value,
        )
        content = await resp.json()
        assert resp.status == 400
        assert content == {
            'code': 'BadRequest::WrongParams',
            'message': (
                f'fallback_discount value "{discount_value}" must be not '
                f'greater than suggest\'s '
                f'max_discount = {max_disc}'
            ),
        }

    async def test_discount_multiple_of(self, send_request):
        resp = await send_request(fallback_discount=8)
        content = await resp.json()
        assert resp.status == 400
        assert content == {
            'code': 'BadRequest::WrongParams',
            'message': f'fallback_discount value must be multiple of 3',
        }

    async def test_push_and_fallback_discount(self, send_request):
        resp = await send_request(fallback_discount=9)
        assert resp.status == 200

        resp = await send_request(fallback_discount=9, with_push=True)
        assert resp.status == 200

        resp = await send_request(with_push=True)
        content = await resp.json()
        assert resp.status == 400
        assert content == {
            'code': 'BadRequest::WrongParams',
            'message': (
                'fallback_discount must be specified for sending pushes'
            ),
        }
