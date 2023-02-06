import pytest


URL = 'internal/eulas/v1/is-freightage-required'
FREIGHTAGE_DRIVER_TAGS = ['show_freightage']


@pytest.mark.config(EULAS_FREIGHTAGE_DRIVER_TAGS=FREIGHTAGE_DRIVER_TAGS)
@pytest.mark.parametrize(
    'nearest_zone, tags, is_required',
    [
        pytest.param('test_zone', None, True),
        pytest.param('test_zone', [], True),
        pytest.param('test_zone', ['another_tag'], True),
        pytest.param('contract_not_required_zone', None, False),
        pytest.param('contract_not_required_zone', [], False),
        pytest.param('contract_not_required_zone', ['another_tag'], False),
        pytest.param(
            'contract_not_required_zone', FREIGHTAGE_DRIVER_TAGS, True,
        ),
    ],
)
async def test_is_freightage_required(
        taxi_eulas, nearest_zone, tags, is_required,
):
    body = {
        'tariff_class': 'ultimate',
        'nearest_zone': nearest_zone,
        'tags': tags,
    }
    response = await taxi_eulas.post(URL, json=body)

    assert response.status_code == 200
    assert response.json() == {'required': is_required}
