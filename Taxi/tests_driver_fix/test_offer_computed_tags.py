import pytest

from tests_driver_fix import common


@pytest.mark.config(
    DRIVER_FIX_OFFER_SCREENS_BY_ROLE_V2={
        '__default__': common.DEFAULT_OFFER_CONFIG_V2,
    },
    DRIVER_FIX_OFFER_COMPUTE_ADDITIONAL_TAGS=True,
)
@pytest.mark.parametrize(
    'tags, subvention_rule_id',
    ((['tag1', 'tag3'], 'subvention_rule_id'), (['tag1'], None)),
)
@pytest.mark.experiments3(filename='computed_tags_exp3.json')
@pytest.mark.now('2019-01-01T12:00:00+0300')
@pytest.mark.servicetest
async def test_offer_computed_tags(
        taxi_driver_fix,
        taxi_config,
        mockserver,
        mock_offer_requirements,
        driver_tags_mocks,
        tags,
        subvention_rule_id,
):
    common.default_init_mock_offer_requirements(mock_offer_requirements)
    driver_tags_mocks.set_tags_info('dbid', 'uuid', tags)

    @mockserver.json_handler('/billing_subventions/v1/rules/select')
    def _bs(request):
        subventions = []
        if 'computed_tag' in request.json['profile_tags']:
            subventions.append(common.DEFAULT_DRIVER_FIX_RULE)
        return {'subventions': subventions}

    response = await taxi_driver_fix.post(
        '/v1/view/offer',
        json={'driver_profile_id': 'uuid', 'park_id': 'dbid'},
        headers=common.DEFAULT_DRIVER_FIX_HEADER,
    )

    assert response.status_code == 200
    response_json = response.json()
    if not subvention_rule_id:
        assert not response_json['offers']
    else:
        offers = response_json['offers']
        assert len(offers) == 1
        assert offers[0]['settings']['rule_id'] == subvention_rule_id
