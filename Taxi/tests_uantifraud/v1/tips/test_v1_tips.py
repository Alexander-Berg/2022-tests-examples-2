import copy

import pytest


def _make_experiment():
    return {
        'name': 'uafs_js_rules_enabled',
        'match': {
            'consumers': [{'name': 'uafs_js_rule'}],
            'predicate': {'type': 'true'},
            'enabled': True,
        },
        'clauses': [
            {
                'predicate': {
                    'init': {
                        'arg_name': 'rule_type',
                        'arg_type': 'string',
                        'value': 'tips',
                    },
                    'type': 'eq',
                },
                'value': {'enabled': True},
            },
        ],
    }


GOOD_ORG_ID = 98765
BAD_ORG_ID = 12345

TEST_ITEM_FOR_ALLOW = {
    'client_has_yandex_plus': False,
    'client_ip': '1.2.3.4',
    'client_login_id': 'good_login_id',
    'client_yandex_uid': 'good_yandex_uid',
    'organization_id': GOOD_ORG_ID,
    'staff_id': 777,
    'user_agent': 'curl/7.68.0',
}

TEST_ITEM_FOR_BLOCK = {
    'client_has_yandex_plus': False,
    'is_admin_reg': True,
    'client_ip': '1.2.3.4',
    'client_login_id': 'bad_login_id',
    'client_yandex_uid': 'bad_yandex_uid',
    'organization_id': BAD_ORG_ID,
    'staff_id': 777,
    'user_agent': 'curl/7.68.0',
    'recipient_id': '23fe4c38-2386-4fe4-9b0f-39fb5614ca5a',
    'recipient_created_at': '2022-02-22T22:22:22+03:00',
}


@pytest.mark.parametrize(
    'tip_item,result',
    [(TEST_ITEM_FOR_ALLOW, 'allow'), (TEST_ITEM_FOR_BLOCK, 'block')],
)
@pytest.mark.experiments3(**_make_experiment())
async def test_base(taxi_uantifraud, tip_item, result, testpoint):
    @testpoint('init_with_idempotent_result')
    def tp_init_with_idempotent_result(_):
        pass

    @testpoint('idempotent_result_store_successful')
    def tp_idempotent_store_successful(_):
        pass

    async def request_and_check():
        resp = await taxi_uantifraud.post('/v1/tips/check', json=tip_item)
        assert resp.status_code == 200
        assert resp.json()['status'] == result

    await request_and_check()

    assert tp_init_with_idempotent_result.times_called == 0
    assert tp_idempotent_store_successful.times_called == 1

    recalls_num = 5

    for _ in range(recalls_num):
        await request_and_check()

    assert tp_init_with_idempotent_result.times_called == recalls_num
    assert tp_idempotent_store_successful.times_called == 1


@pytest.mark.parametrize(
    'tip_item,result,org_id_subst',
    [
        (TEST_ITEM_FOR_ALLOW, 'allow', BAD_ORG_ID),
        (TEST_ITEM_FOR_BLOCK, 'block', GOOD_ORG_ID),
    ],
)
@pytest.mark.experiments3(**_make_experiment())
async def test_idempotent_cache(
        taxi_uantifraud, tip_item, result, org_id_subst, testpoint,
):
    @testpoint('init_with_idempotent_result')
    def tp_init_with_idempotent_result(_):
        pass

    @testpoint('idempotent_result_store_successful')
    def tp_idempotent_store_successful(_):
        pass

    async def request_and_check(tip_item):
        resp = await taxi_uantifraud.post('/v1/tips/check', json=tip_item)
        assert resp.status_code == 200
        assert resp.json()['status'] == result

    tip_item_copy = copy.deepcopy(tip_item)

    await request_and_check(tip_item_copy)

    assert tp_init_with_idempotent_result.times_called == 0
    assert tp_idempotent_store_successful.times_called == 1

    # change for switch other status
    tip_item_copy['organization_id'] = org_id_subst

    await request_and_check(tip_item_copy)

    assert tp_init_with_idempotent_result.times_called == 1
    assert tp_idempotent_store_successful.times_called == 1


@pytest.mark.experiments3(**_make_experiment())
async def test_args(taxi_uantifraud, testpoint):
    response = {'status': 'block', 'reason': 'test_rule1'}

    @testpoint('test_args')
    def test_args_tp(data):
        assert data == {
            'client_has_yandex_plus': False,
            'is_admin_reg': True,
            'client_ip': '1.2.3.4',
            'client_login_id': 'bad_login_id',
            'client_yandex_uid': 'bad_yandex_uid',
            'organization_id': 12345,
            'recipient_created_at': '2022-02-22T19:22:22.000Z',
            'recipient_id': '23fe4c38-2386-4fe4-9b0f-39fb5614ca5a',
            'staff_id': 777,
            'user_agent': 'curl/7.68.0',
            'auto_entity_map': {},
        }
        return response

    resp = await taxi_uantifraud.post(
        '/v1/tips/check', json=TEST_ITEM_FOR_BLOCK,
    )

    assert await test_args_tp.wait_call()

    assert resp.status_code == 200
    assert resp.json() == response
