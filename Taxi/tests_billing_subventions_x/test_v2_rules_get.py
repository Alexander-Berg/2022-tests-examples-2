import pytest


async def test_v2_rules_get_single_ride(
        taxi_billing_subventions_x,
        a_single_ride,
        create_rules,
        load_json,
        a_budget,
):
    rule = a_single_ride(
        id='2abf062a-b607-11ea-998e-07e60204cbcf',
        updated_at='2020-05-01T21:00:00+00:00',
        tag='some_tag',
        branding='sticker',
        points=60,
        geoarea='sviblovo',
        stop_tag='stop',
    )
    create_rules(rule, draft_id='fake_draft_id', budget_id=a_budget)
    response = await _make_request(taxi_billing_subventions_x, rule['id'])
    assert response == {
        'rule': load_json('single_ride.json'),
        'budget': {
            'id': a_budget,
            'daily': True,
            'weekly': True,
            'threshold': '5',
        },
    }


async def test_v2_rules_get_goal_rule(
        taxi_billing_subventions_x, load_json, a_goal, create_rules,
):
    rule = a_goal(
        id='5e03538d-740b-4e0b-b5f4-1425efa59319',
        tag='another_tag',
        branding='full_branding',
        unique_driver_id='2fa69ea2-8d53-4b24-ae78-a02d795f5d9d',
        updated_at='2020-05-01T21:00:00+00:00',
        stop_tag='stop',
    )
    create_rules(
        rule,
        draft_id='22222',
        budget_id='f0ca1925-9397-4d7e-8667-1536363829bd',
    )
    response = await _make_request(taxi_billing_subventions_x, rule['id'])
    assert response == {'rule': load_json('goal.json')}


async def test_v2_rules_get_on_top_rule(
        taxi_billing_subventions_x, load_json, a_single_ontop, create_rules,
):
    rule = a_single_ontop(
        id='2abf062a-b607-11ea-998e-07e60204cbdf',
        updated_at='2020-05-01T21:00:00+00:00',
        tag='some_tag',
        branding='sticker',
        points=60,
        geoarea='sviblovo',
        stop_tag='stop',
    )
    create_rules(
        rule,
        draft_id='fake_draft_id',
        budget_id='f0ca1925-9397-4d7e-8667-1536363829bd',
    )
    response = await _make_request(taxi_billing_subventions_x, rule['id'])
    assert response == {'rule': load_json('on_top.json')}


async def _make_request(taxi_billing_subventions_x, rule_id):
    response = await taxi_billing_subventions_x.get(
        '/v2/rules/get', params={'rule_id': rule_id},
    )
    assert response.status_code == 200, response.json()
    return response.json()


async def test_v2_rules_get_returns_404_when_rule_not_found(
        taxi_billing_subventions_x,
):
    response = await taxi_billing_subventions_x.get(
        '/v2/rules/get',
        params={'rule_id': 'bbbbbbbb-cccc-aaaa-dddd-eeeeeeeeeeee'},
    )
    assert response.status_code == 404


@pytest.fixture(name='a_budget')
def _make_budget(load_sql, pgsql):
    cursor = pgsql['billing_subventions'].cursor()
    budget_id = 'f0ca1925-9397-4d7e-8667-1536363829bd'
    cursor.execute(
        load_sql('budget_save.sql'),
        [budget_id, True, True, '5', 'RUPRICING-1'],
    )
    return budget_id
