import pytest

from . import common
from . import experiments

# Проверяем, что прокидываем в прокси поиска формулу ранжирования из
# эксперимента
@experiments.MODES_ROOT_LAYOUT_ENABLED
@experiments.create_search_flow_experiment('market', fallback_flow='internal')
@pytest.mark.parametrize(
    'formula, foodtech_cgi',
    [
        pytest.param('heuristic', 'formula=heuristic', id='some'),
        pytest.param(None, None, id='none'),
    ],
)
async def test_forward_formula(
        taxi_grocery_api,
        mockserver,
        overlord_catalog,
        load_json,
        grocery_depots,
        market_report_proxy,
        grocery_search,
        experiments3,
        formula,
        foodtech_cgi,
):
    experiments3.add_experiment3_from_marker(
        experiments.seach_market_use_relevance_formula(formula), load_json,
    )

    location = [0, 0]
    common.prepare_overlord_catalog_json(load_json, overlord_catalog, location)

    market_report_proxy.expect_query_params(
        params={'foodtech-cgi': foodtech_cgi},
    )

    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/search',
        json={'text': 'query', 'position': {'location': location}},
    )
    assert response.status_code == 200
    assert market_report_proxy.times_called == 1
