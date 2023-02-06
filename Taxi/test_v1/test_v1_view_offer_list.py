import copy

import pytest

from tests_driver_fix import common


_CONFIG_BY_ROLE1 = {
    'offer_card': {
        'title': 'role_offer_card.title',
        'description': 'role_offer_card.description',
    },
    'offer_screen': [],
    'memo_screen': [],
}

_CONFIG_BY_ROLE2 = {
    'offer_card': {
        'title': 'role2_offer_card.title',
        'description': 'role2_offer_card.description',
    },
    'offer_screen': [],
    'memo_screen': [],
}

use_role_config = pytest.mark.config(  # pylint: disable=C0103
    DRIVER_FIX_OFFER_SCREENS_BY_ROLE_V2={
        '__default__': common.DEFAULT_OFFER_CONFIG_V2,
        'role': _CONFIG_BY_ROLE1,
        'role2': _CONFIG_BY_ROLE2,
    },
)


def _build_driver_fix_rule(rule_id, tariff_zone, tags):
    rule = copy.deepcopy(common.DEFAULT_DRIVER_FIX_RULE)
    rule['subvention_rule_id'] = rule_id
    rule['tariff_zones'] = [tariff_zone]
    rule['tags'] = tags
    return rule


def _build_body(tariff_zones, roles=None, current_mode_settings=None):
    body = {
        'driver_profile_id': 'uuid',
        'park_id': 'dbid',
        'tariff_zones': tariff_zones,
    }
    if roles is not None:
        body['roles'] = [{'name': role_name} for role_name in roles]
    if current_mode_settings is not None:
        body['current_mode_settings'] = current_mode_settings
    return body


def _sort_offers(offers):
    return sorted(offers, key=lambda offer: offer['settings']['rule_id'])


@pytest.fixture(name='mock_billing_subventions')
def _mock_billing_subventions(mockserver):
    class Context:
        def __init__(self):
            self.rules_by_zone = {}
            self.rules_select = None

    ctx = Context()

    @mockserver.json_handler('/billing_subventions/v1/rules/select')
    def _rules_select(request):
        doc = request.json
        rules = ctx.rules_by_zone.get(doc['tariff_zone'], [])
        return {'subventions': [rules]}

    ctx.rules_select = _rules_select

    return ctx


@pytest.mark.parametrize(
    'tariff_zones,use_roles_as_tags,roles,expected_offers',
    [
        (
            # tariff_zones
            ['moscow'],
            # use_roles_as_tags
            False,
            # roles
            None,
            # expected_offers
            [
                {
                    'title': 'За время',
                    'tariff_zone': 'moscow',
                    'settings': {
                        'rule_id': 'id_rule_moscow',
                        'shift_close_time': '00:00+03:00',
                    },
                },
            ],
        ),
        (
            # tariff_zones
            ['moscow', 'zelenograd'],
            # use_roles_as_tags
            False,
            # roles
            None,
            # expected_offers
            [
                {
                    'title': 'За время',
                    'tariff_zone': 'moscow',
                    'settings': {
                        'rule_id': 'id_rule_moscow',
                        'shift_close_time': '00:00+03:00',
                    },
                },
                {
                    'title': 'За время',
                    'tariff_zone': 'zelenograd',
                    'settings': {
                        'rule_id': 'id_rule_zelenograd',
                        'shift_close_time': '00:00+03:00',
                    },
                },
            ],
        ),
        (
            # tariff_zones
            ['moscow', 'zelenograd'],
            # use_roles_as_tags
            True,
            # roles
            ['role', 'role2'],
            # expected_offers
            [
                {
                    'title': 'За время role',
                    'tariff_zone': 'moscow',
                    'settings': {
                        'rule_id': 'id_rule_moscow',
                        'shift_close_time': '00:00+03:00',
                    },
                },
                {
                    'title': 'За время role2',
                    'tariff_zone': 'zelenograd',
                    'settings': {
                        'rule_id': 'id_rule_zelenograd',
                        'shift_close_time': '00:00+03:00',
                    },
                },
            ],
        ),
    ],
)
@use_role_config
async def test_offer_list(
        taxi_driver_fix,
        mock_offer_requirements,
        mock_billing_subventions,
        taxi_config,
        tariff_zones,
        use_roles_as_tags,
        roles,
        expected_offers,
):
    common.default_init_mock_offer_requirements(mock_offer_requirements)

    if use_roles_as_tags:
        taxi_config.set_values(
            dict(
                DRIVER_FIX_OFFER_USE_ROLES_AS_TAGS=True,
                DRIVER_FIX_MATCH_ROLES_FOR_OFFERS={
                    'driver_fix': True,
                    'geo_booking': False,
                },
            ),
        )

    mock_billing_subventions.rules_by_zone = {
        'moscow': _build_driver_fix_rule(
            'id_rule_moscow', 'moscow', tags=['role'],
        ),
        'zelenograd': _build_driver_fix_rule(
            'id_rule_zelenograd', 'zelenograd', tags=['role2'],
        ),
    }

    response = await taxi_driver_fix.post(
        '/v1/view/offer_by_zone',
        json=_build_body(tariff_zones, roles=roles),
        headers=common.DEFAULT_DRIVER_FIX_HEADER,
    )

    assert response.status_code == 200
    doc = response.json()

    assert _sort_offers(doc['offers']) == _sort_offers(expected_offers)
