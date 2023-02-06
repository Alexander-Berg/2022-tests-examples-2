import pytest

PARAMETRIZE_STOCKS_LIMITS_BRAND_ID = 1
PARAMETRIZE_STOCKS_LIMITS = pytest.mark.parametrize(
    'displayed_stocks_limits_applied, displayed_stocks_limits_exp_enabled',
    [
        pytest.param(False, False, id='experiment and config are disabled'),
        pytest.param(
            False, True, id='experiment is enabled, config is disabled',
        ),
        pytest.param(
            False,
            True,
            marks=[
                pytest.mark.config(
                    EATS_NOMENCLATURE_STOCK_LIMITS={
                        str(PARAMETRIZE_STOCKS_LIMITS_BRAND_ID): {
                            'should_limit_in_stock': False,
                        },
                    },
                ),
            ],
            id='experiment is enabled, disabled brand',
        ),
        pytest.param(
            True,
            True,
            marks=[
                pytest.mark.config(
                    EATS_NOMENCLATURE_STOCK_LIMITS={
                        str(PARAMETRIZE_STOCKS_LIMITS_BRAND_ID): {
                            'should_limit_in_stock': True,
                        },
                    },
                ),
            ],
            id='experiment is enabled, enabled brand',
        ),
        pytest.param(
            True,
            True,
            marks=[
                pytest.mark.config(
                    EATS_NOMENCLATURE_STOCK_LIMITS={
                        '__default__': {'should_limit_in_stock': True},
                    },
                ),
            ],
            id='experiment is enabled, enabled brands by default',
        ),
    ],
)


async def enable_displ_stock_limits_exp(
        taxi_eats_nomenclature, experiments3, public_id_to_stock_limit,
):
    experiments3.add_experiment(
        clauses=[
            {
                'predicate': {'init': {}, 'type': 'true'},
                'title': 'any-title',
                'value': {
                    'limits': {public_id: stock_limit}
                    for public_id, stock_limit in public_id_to_stock_limit.items()  # noqa: E501 pylint: disable=line-too-long
                },
            },
        ],
        match={
            'consumers': [{'name': 'eats_nomenclature/stock_limits'}],
            'enabled': True,
            'predicate': {'init': {}, 'type': 'true'},
        },
        name='eats_nomenclature_stock_limits',
    )
    await taxi_eats_nomenclature.invalidate_caches()
