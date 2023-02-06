import copy

import pytest

from tests_driver_fix import common


def _new_rule(rule_type):
    prototypes = {
        'driver_fix': common.DEFAULT_DRIVER_FIX_RULE,
        'geo_booking': common.DEFAULT_GEOBOOKING_RULE,
    }
    return copy.deepcopy(prototypes[rule_type])


@pytest.mark.parametrize(
    'params_by_rule_id',
    [
        {
            '_id/geobooking1': {
                'rule_type': 'geo_booking',
                'tariff_zone': 'moscow',
                'geoarea': 'moscow_center',
                'tag': 'geobooking_moscow_center',
            },
        },
        {
            '_id/geobooking1': {
                'rule_type': 'geo_booking',
                'tariff_zone': 'moscow',
                'geoarea': 'moscow_center',
                'tag': 'geobooking_moscow_center',
            },
            '_id/geobooking2': {
                'rule_type': 'geo_booking',
                'tariff_zone': 'perm',
                'geoarea': 'perm',
                'tag': 'geobooking_perm',
            },
        },
        {
            '_id/geobooking1': {
                'rule_type': 'geo_booking',
                'tariff_zone': 'moscow',
                'geoarea': 'moscow_center',
                'tag': 'geobooking_moscow_center',
            },
            '_id/driver_fix1': {
                'rule_type': 'driver_fix',
                'tariff_zone': 'perm',
                'geoarea': 'perm',
                'tag': 'driver_fix__perm',
            },
        },
    ],
)
async def test_rule_key_params(taxi_driver_fix, mockserver, params_by_rule_id):
    rule_ids = list(params_by_rule_id.keys())

    @mockserver.json_handler('/billing_subventions/v1/rules/select')
    def _bs(request):
        body = request.json
        requested_ids = body['rule_ids']
        assert len(requested_ids) == 1
        assert requested_ids[0] in rule_ids

        subventions = []
        for rule_id in requested_ids:
            params = params_by_rule_id[rule_id]
            rule = _new_rule(params['rule_type'])
            rule['tariff_zones'] = [params['tariff_zone']]
            rule['geoareas'] = [params['geoarea']]
            rule['tags'] = [params['tag']]
            subventions.append(rule)
        return {'subventions': subventions}

    response = await taxi_driver_fix.post(
        '/v1/view/rule_key_params',
        json={'rule_ids': rule_ids},
        headers=common.DEFAULT_DRIVER_FIX_HEADER,
    )
    assert response.status_code == 200

    doc = response.json()
    assert len(doc['rules']) == len(rule_ids)

    for rule in doc['rules']:
        rule_id = rule['rule_id']
        params = params_by_rule_id[rule_id]

        expected_key_params = {
            'tariff_zone': params['tariff_zone'],
            'subvention_geoarea': params['geoarea'],
            'tag': params['tag'],
        }

        assert rule['key_params'] == expected_key_params


@pytest.mark.config(
    DRIVER_FIX_VIEW_RULE_KEY_PARAMS_SETTINGS={'max_bulk_size': 100},
)
@pytest.mark.parametrize('rules_in_request', [0, 101])
async def test_bad_request(taxi_driver_fix, rules_in_request):
    request_body = {'rule_ids': ['_id/rule'] * rules_in_request}

    response = await taxi_driver_fix.post(
        '/v1/view/rule_key_params',
        json=request_body,
        headers=common.DEFAULT_DRIVER_FIX_HEADER,
    )
    assert response.status_code == 400
