import pytest


def _reset_prepare_link(response):
    for category in response['categories'].values():
        assert 'links' in category and 'prepare' in category['links']
        if category['links']['prepare']:
            category['links']['prepare'] = '__default__'
    return response


@pytest.mark.now('2019-10-22T11:32:00+0300')
@pytest.mark.config()
@pytest.mark.parametrize(
    'testname, ' 'plugin_decoupling_enabled, ' 'corp_decoupling ',
    [
        (
            'simple',
            True,  # plugin_decoupling_enabled
            False,  # corp_decoupling
        ),
        (
            'with_multiple_categories',
            True,  # plugin_decoupling_enabled
            False,  # corp_decoupling
        ),
        (
            'with_user_info',
            True,  # plugin_decoupling_enabled
            False,  # corp_decoupling
        ),
        (
            'exp_decoupling_disabled',
            False,  # plugin_decoupling_enabled
            False,  # corp_decoupling
        ),
        (
            'with_corp_decoupling',
            True,  # plugin_decoupling_enabled
            True,  # corp_decoupling
        ),
    ],
)
async def test_v1_get_pricing_data(
        taxi_pricing_fallback,
        load_json,
        experiments3,
        testname,
        plugin_decoupling_enabled,
        corp_decoupling,
):
    if plugin_decoupling_enabled:
        experiments3.add_experiments_json(
            load_json('exp3_plugin_decoupling.json'),
        )

    request = load_json(testname + '/request.json')

    response = await taxi_pricing_fallback.post(
        'v1/get_pricing_data', json=request,
    )
    assert response.status_code == 200

    response = _reset_prepare_link(response.json())
    expected_response = load_json(testname + '/response.json')
    assert response == expected_response
