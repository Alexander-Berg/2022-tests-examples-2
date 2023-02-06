import pytest


@pytest.mark.pgsql('pricing_data_preparer', files=['rules.sql'])
async def test_v2_settings_workability_get_empty(taxi_pricing_admin):
    response = await taxi_pricing_admin.get('v2/settings/workability')
    assert response.status_code == 200
    resp = response.json()
    assert 'workability' in resp
    assert resp['workability'] == {'driver': [], 'user': []}


@pytest.mark.pgsql(
    'pricing_data_preparer', files=['rules.sql', 'workabilities.sql'],
)
@pytest.mark.parametrize('scope', [None, 'taxi', 'cargo'])
async def test_v2_settings_workability_get(taxi_pricing_admin, scope):
    response = await taxi_pricing_admin.get(
        'v2/settings/workability', params={'scope': scope} if scope else {},
    )
    assert response.status_code == 200
    resp = response.json()
    assert 'workability' in resp
    workability = resp['workability']
    expected_driver = ['three'] if scope == 'cargo' else ['one', 'two']
    expected_user = ['five', 'four'] if scope == 'cargo' else ['one']
    assert (
        list(item['name'] for item in workability['driver']) == expected_driver
    )
    assert list(item['name'] for item in workability['user']) == expected_user


@pytest.mark.parametrize(
    'rule_name, response_code', [('one', 200), ('invalid', 400)],
)
@pytest.mark.pgsql('pricing_data_preparer', files=['rules.sql'])
async def test_v2_service_approvals_workability_bad_rules(
        taxi_pricing_admin, rule_name, response_code,
):
    rule = {
        'name': rule_name,
        'using_settings': {
            'used_for_antisurge': True,
            'used_for_paid_supply': True,
            'used_for_plus_promo': True,
            'used_for_strikeout': True,
            'used_for_total': True,
        },
    }
    response = await taxi_pricing_admin.post(
        'v2/service/approvals/workability/check',
        json={'driver': [rule], 'user': [rule]},
    )
    assert response.status_code == response_code


@pytest.mark.parametrize(
    'workability',
    [
        {'driver': [], 'user': []},
        {
            'driver': [
                {
                    'name': 'one',
                    'using_settings': {
                        'used_for_antisurge': True,
                        'used_for_combo_order': False,
                        'used_for_perfect_chain': False,
                        'used_for_full_auction': False,
                        'used_for_combo_inner': False,
                        'used_for_combo_outer': False,
                        'used_for_combo': False,
                        'used_for_paid_supply': True,
                        'used_for_plus_promo': False,
                        'used_for_total': True,
                    },
                },
                {
                    'name': 'two',
                    'using_settings': {
                        'used_for_antisurge': True,
                        'used_for_combo_order': False,
                        'used_for_perfect_chain': False,
                        'used_for_full_auction': False,
                        'used_for_combo_inner': False,
                        'used_for_combo_outer': False,
                        'used_for_combo': False,
                        'used_for_paid_supply': True,
                        'used_for_plus_promo': False,
                        'used_for_total': True,
                    },
                },
            ],
            'user': [
                {
                    'name': 'two',
                    'using_settings': {
                        'used_for_antisurge': True,
                        'used_for_combo_order': True,
                        'used_for_perfect_chain': True,
                        'used_for_full_auction': True,
                        'used_for_combo_inner': True,
                        'used_for_combo_outer': True,
                        'used_for_combo': True,
                        'used_for_paid_supply': True,
                        'used_for_plus_promo': True,
                        'used_for_strikeout': True,
                        'used_for_total': True,
                    },
                },
                {
                    'name': 'three',
                    'using_settings': {
                        'used_for_antisurge': True,
                        'used_for_perfect_chain': True,
                        'used_for_full_auction': True,
                        'used_for_combo_order': True,
                        'used_for_combo_inner': True,
                        'used_for_combo_outer': True,
                        'used_for_combo': True,
                        'used_for_paid_supply': True,
                        'used_for_plus_promo': True,
                        'used_for_strikeout': True,
                        'used_for_total': True,
                    },
                },
            ],
        },
    ],
)
@pytest.mark.pgsql('pricing_data_preparer', files=['rules.sql'])
@pytest.mark.parametrize('scope', [None, 'taxi', 'cargo'])
async def test_v2_service_approvals_workability_check(
        taxi_pricing_admin, workability, scope,
):
    response = await taxi_pricing_admin.post(
        'v2/service/approvals/workability/check',
        params={'scope': scope} if scope else {},
        json=workability,
    )
    assert response.status_code == 200


@pytest.mark.pgsql('pricing_data_preparer', files=['rules.sql'])
@pytest.mark.parametrize('scope', [None, 'taxi', 'cargo'])
async def test_v2_service_approvals_workability_apply(
        taxi_pricing_admin, load_json, scope,
):
    async def do_put_get_test(driver_rules, user_rules):
        response = await taxi_pricing_admin.post(
            'v2/service/approvals/workability/apply',
            params={'scope': scope} if scope else {},
            json={'driver': driver_rules, 'user': user_rules},
        )
        assert response.status_code == 200

        response = await taxi_pricing_admin.get(
            'v2/settings/workability',
            params={'scope': scope} if scope else {},
        )
        assert response.status_code == 200

        resp = response.json()
        assert 'workability' in resp
        workability = resp['workability']
        assert 'driver' in workability and 'user' in workability

        for subject, rules in workability.items():
            if subject == 'driver':
                assert rules == driver_rules
            elif subject == 'user':
                assert rules == user_rules

    def add_using_parameters(
            rule,
            used_for_total,
            used_for_strikeout,
            used_for_antisurge,
            used_for_paid_supply,
            used_for_plus_promo,
            used_for_combo_order,
            used_for_combo_inner,
            used_for_combo_outer,
            used_for_combo,
            used_for_perfect_chain,
            used_for_full_auction,
            user=True,
    ):
        if user:
            json = {
                'name': rule,
                'using_settings': {
                    'used_for_total': used_for_total,
                    'used_for_strikeout': used_for_strikeout,
                    'used_for_antisurge': used_for_antisurge,
                    'used_for_paid_supply': used_for_paid_supply,
                    'used_for_plus_promo': used_for_plus_promo,
                    'used_for_combo_order': used_for_combo_order,
                    'used_for_perfect_chain': used_for_perfect_chain,
                    'used_for_combo_inner': used_for_combo_inner,
                    'used_for_combo_outer': used_for_combo_outer,
                    'used_for_combo': used_for_combo,
                    'used_for_full_auction': used_for_full_auction,
                },
            }
        else:
            json = {
                'name': rule,
                'using_settings': {
                    'used_for_total': used_for_total,
                    'used_for_antisurge': used_for_antisurge,
                    'used_for_paid_supply': used_for_paid_supply,
                    'used_for_plus_promo': used_for_plus_promo,
                    'used_for_combo_order': used_for_combo_order,
                    'used_for_perfect_chain': used_for_perfect_chain,
                    'used_for_combo_inner': used_for_combo_inner,
                    'used_for_combo_outer': used_for_combo_outer,
                    'used_for_combo': used_for_combo,
                    'used_for_full_auction': used_for_full_auction,
                },
            }
        return json

    # declare
    rule_one = load_json('rule_one.json')
    rule_two = load_json('rule_two.json')

    driver_rules = [
        add_using_parameters(
            rule_one['name'],
            used_for_total=True,
            used_for_strikeout=False,
            used_for_antisurge=True,
            used_for_paid_supply=False,
            used_for_plus_promo=False,
            used_for_combo_order=False,
            used_for_perfect_chain=True,
            used_for_combo_inner=False,
            used_for_combo_outer=False,
            used_for_combo=False,
            used_for_full_auction=True,
            user=False,
        ),
    ]
    user_rules = [
        add_using_parameters(
            rule_two['name'],
            used_for_total=True,
            used_for_strikeout=True,
            used_for_antisurge=False,
            used_for_paid_supply=False,
            used_for_plus_promo=True,
            used_for_combo_order=True,
            used_for_perfect_chain=True,
            used_for_combo_inner=True,
            used_for_combo_outer=True,
            used_for_combo=True,
            used_for_full_auction=True,
        ),
    ]

    # write
    await do_put_get_test(driver_rules, user_rules)

    # rewrite
    driver_rules.append(
        add_using_parameters(
            rule_two['name'],
            used_for_total=False,
            used_for_strikeout=False,
            used_for_antisurge=False,
            used_for_paid_supply=True,
            used_for_plus_promo=True,
            used_for_combo_order=True,
            used_for_perfect_chain=True,
            used_for_combo_inner=True,
            used_for_combo_outer=True,
            used_for_combo=True,
            used_for_full_auction=True,
            user=False,
        ),
    )
    user_rules.insert(
        0,
        add_using_parameters(
            rule_one['name'],
            used_for_total=False,
            used_for_strikeout=False,
            used_for_antisurge=True,
            used_for_paid_supply=True,
            used_for_plus_promo=True,
            used_for_combo_order=True,
            used_for_combo_inner=True,
            used_for_perfect_chain=True,
            used_for_combo_outer=True,
            used_for_combo=True,
            used_for_full_auction=True,
        ),
    )
    await do_put_get_test(driver_rules, user_rules)

    # delete
    driver_rules.clear()
    user_rules.clear()
    await do_put_get_test(driver_rules, user_rules)


@pytest.mark.config(PRICING_DATA_PREPARER_REQUIRED_METADATA=['qqq'])
@pytest.mark.pgsql('pricing_data_preparer', files=['rules.sql'])
@pytest.mark.parametrize(
    'rule_name, response_code', [('one', 400), ('two', 200), ('three', 400)],
)
async def test_v2_service_approvals_workability_apply_no_meta(
        taxi_pricing_admin, rule_name, response_code,
):
    rule = {
        'name': rule_name,
        'using_settings': {
            'used_for_antisurge': True,
            'used_for_paid_supply': True,
            'used_for_plus_promo': True,
            'used_for_combo_order': True,
            'used_for_perfect_chain': True,
            'used_for_combo_inner': True,
            'used_for_combo_outer': True,
            'used_for_combo': True,
            'used_for_strikeout': True,
            'used_for_full_auction': True,
            'used_for_total': True,
        },
    }
    response = await taxi_pricing_admin.post(
        'v2/service/approvals/workability/apply',
        json={'driver': [rule], 'user': [rule]},
    )
    assert response.status_code == response_code
