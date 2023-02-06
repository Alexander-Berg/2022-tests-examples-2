import json

import pytest


@pytest.mark.parametrize(
    'request_json, status_code, exprected_rules_file',
    [
        (
            {
                'name': 'name0',
                'parameters': [
                    {'name': 'x_dist', 'value': 0},
                    {'name': 'x_time', 'value': 0},
                ],
                'expression': (
                    'cb1_dist-b2b1_dist>x_dist && cb1_time-b2b1_time>x_time'
                ),
            },
            200,
            'post-response-0.json',
        ),
        (
            {
                'name': 'name1',
                'parameters': [
                    {'name': 'x_dist', 'value': 0},
                    {'name': 'x_time', 'value': 0},
                ],
                'expression': (
                    'cb1_dist-b2b1_dist>x_dist && cb1_time-b2b1_time>x_time'
                ),
            },
            200,
            'post-response-1.json',
        ),
        (
            {
                'name': 'promised_time_left',
                'parameters': [{'name': 'time_bound', 'value': 2000}],
                'expression': 'promised_time_left<time_bound',
            },
            200,
            'post-response-2.json',
        ),
        (
            {
                'name': 'combo_mathcing_policy',
                'parameters': [{'name': 'max_delta_eta_1', 'value': 180}],
                'expression': (
                    '!(driving_time_1 - base_driving_time_1 < max_delta_eta_1)'
                ),
            },
            200,
            'post-response-3.json',
        ),
        (
            {
                'name': 'name0',
                'parameters': [{'name': 'x_dist', 'value': 0}],
                'expression': (
                    'cb1_dist-b2b1_dist>x_dist && cb1_time-b2b1_time>x_time'
                ),
            },
            400,  # Missing parameter 'x_time'
            '',
        ),
        (
            {
                'name': 'name0',
                'parameters': [
                    {'name': 'x_dist', 'value': 0},
                    {'name': 'x_time', 'value': 0},
                ],
                'expression': (
                    '??? cb1_dist-b2b1_dist>x_dist '
                    '&& cb1_time-b2b1_time>x_time'
                ),
            },
            400,  # Invalid expression syntax
            '',
        ),
    ],
)
@pytest.mark.pgsql('combo_contractors', files=['order_match_rule.sql'])
async def test_admin_order_match_rules_post(
        taxi_combo_contractors,
        pgsql,
        load_json,
        request_json,
        status_code,
        exprected_rules_file,
):
    response = await taxi_combo_contractors.post(
        'v1/admin/order-match-rules', json=request_json,
    )
    assert response.status_code == status_code

    if status_code != 200:
        return

    cursor = pgsql['combo_contractors'].cursor()
    cursor.execute(
        'select '
        '   name,'
        '   expression,'
        '   compiled_expression '
        'from'
        '   combo_contractors.order_match_rule '
        'order by name',
    )
    colnames = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    rules = [dict(zip(colnames, row)) for row in rows]
    for rule in rules:
        rule['compiled_expression']['parameter_names'].sort()

    expected_rules = load_json(exprected_rules_file)
    assert rules == expected_rules, 'Gor response: ' + json.dumps(rules)


@pytest.mark.pgsql('combo_contractors', files=['order_match_rule.sql'])
async def test_admin_order_match_rules_get(taxi_combo_contractors, load_json):
    response = await taxi_combo_contractors.get('v1/admin/order-match-rules')
    assert response.status_code == 200
    response_json = response.json()
    for rule in response_json['order_match_rules']:
        rule['parameters'] = sorted(
            rule['parameters'], key=lambda x: x['name'],
        )
    assert response_json == load_json('get-response.json')


@pytest.mark.parametrize(
    'params, status_code, expected_rules',
    [
        ({'name': 'name0'}, 200, []),
        ({'name': 'name43'}, 404, [{'name': 'name0'}]),
    ],
)
@pytest.mark.pgsql('combo_contractors', files=['order_match_rule.sql'])
async def test_admin_order_match_rules_delete(
        taxi_combo_contractors, pgsql, params, status_code, expected_rules,
):
    response = await taxi_combo_contractors.delete(
        'v1/admin/order-match-rules', params=params,
    )
    assert response.status_code == status_code

    cursor = pgsql['combo_contractors'].cursor()
    cursor.execute('select name from combo_contractors.order_match_rule')
    colnames = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    rules = [dict(zip(colnames, row)) for row in rows]

    assert rules == expected_rules
