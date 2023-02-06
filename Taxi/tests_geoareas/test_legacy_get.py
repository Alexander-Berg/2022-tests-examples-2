import operator

import pytest

from tests_geoareas import common

PARAMS_GEOAREAS = pytest.param(
    'geoareas',
    '/1.0/get_geoareas',
    marks=[pytest.mark.filldb(geoareas='spb_msk2')],
)

PARAMS_SUBVENTION_GEOAREAS = pytest.param(
    'subvention_geoareas',
    '/1.0/get_subvention_geoareas',
    marks=[pytest.mark.filldb(subvention_geoareas='spb_msk2')],
)


@pytest.mark.parametrize(
    ['collection_name', 'endpoint'],
    [PARAMS_GEOAREAS, PARAMS_SUBVENTION_GEOAREAS],
)
async def test_legacy_get_basic(
        taxi_geoareas, load_json, collection_name, endpoint,
):
    areas_ids = '<removed_with_ts>,<removed>,<msk2>'
    res = await taxi_geoareas.get(endpoint, params={'id': areas_ids})

    expected = load_json('legacy_get_basic_response.json')
    expected.sort(key=operator.itemgetter('_id'))

    assert res.status_code == 200
    res_json = res.json()
    res_json.sort(key=operator.itemgetter('_id'))
    assert res_json == common.deep_approx(expected)


@pytest.mark.parametrize(
    ['collection_name', 'endpoint'],
    [PARAMS_GEOAREAS, PARAMS_SUBVENTION_GEOAREAS],
)
async def test_legacy_get_404(
        taxi_geoareas, load_json, collection_name, endpoint,
):
    areas_ids = 'ololo1,<removed_with_ts>,<removed>,<msk2>,ololo2'
    res = await taxi_geoareas.get(endpoint, params={'id': areas_ids})

    assert res.status_code == 404
    assert res.json() == {
        'code': 'not_found',
        'details': {'missing_ids': ['ololo2', 'ololo1']},
        'message': 'could not find docs, see details',
    }
