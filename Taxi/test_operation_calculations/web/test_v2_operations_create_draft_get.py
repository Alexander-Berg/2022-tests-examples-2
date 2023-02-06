# pylint: disable=C0103, W0603
import json

from aiohttp import web
import pytest

from taxi import discovery

count = 0

DEFAULT_RESULT = {'draft_id': 11, 'is_multi': True}
OLD_STATE = {
    'code': 'BadRequest::OldState',
    'message': 'State_hash is invalid, request new state_hash',
}
WRONG_RULES = {
    'code': 'BadRequest::WrongCloseRules',
    'details': {'out_of_state_rules': ['bad_rule_id']},
    'message': 'You can not close rules out of state',
}


@pytest.mark.config(
    OPERATION_CALCULATIONS_NMFG_MAX_SUBGMV={'__default__': 0.1, 'spb': 0.2},
)
@pytest.mark.pgsql(
    'operation_calculations',
    files=[
        'pg_operations_params.sql',
        'pg_operations_status.sql',
        'pg_operations_result.sql',
    ],
)
@pytest.mark.now('2019-12-31T20:59:00+00:00')
@pytest.mark.parametrize(
    'expected_status, hash_strategy, rules_strategy,'
    'expected_count, expected_result',
    (
        pytest.param(
            200,
            lambda x: x,
            lambda x: list(map(lambda r: r['subvention_rule_id'], x)),
            4,
            DEFAULT_RESULT,
        ),
        pytest.param(200, lambda x: x, lambda x: [], 3, DEFAULT_RESULT),
        pytest.param(400, lambda x: 'BAD HASH', lambda x: [], 0, OLD_STATE),
        pytest.param(
            400, lambda x: x, lambda x: ['bad_rule_id'], 0, WRONG_RULES,
        ),
    ),
)
async def test_v2_operations_create_draft_get(
        web_app_client,
        patch_aiohttp_session,
        mockserver,
        mock_taxi_tariffs,
        response_mock,
        open_file,
        expected_status,
        hash_strategy,
        rules_strategy,
        expected_count,
        expected_result,
):
    @mock_taxi_tariffs('/v1/tariff_settings/bulk_retrieve')
    def _tariff_settings_handler(request):
        return web.json_response(
            {
                'zones': [
                    {
                        'tariff_settings': {'timezone': 'Europe/Moscow'},
                        'zone': 'moscow',
                    },
                    {
                        'tariff_settings': {'timezone': 'Europe/Moscow'},
                        'zone': 'lytkarino',
                    },
                ],
            },
        )

    with open_file(
            'test_data_billing_nmfg_rules.json', mode='rb', encoding=None,
    ) as fp:
        test_data = json.load(fp)

    @patch_aiohttp_session(
        discovery.find_service('billing_subventions').url + '/v1/rules/select',
        'POST',
    )
    def _patch_request(method, url, **kwargs):
        rules = test_data['subventions']
        return response_mock(json={'subventions': rules})

    global count
    count = 0

    @mockserver.json_handler('/taxi-approvals/drafts/create/')
    def _handler_drafts(request):
        global count
        count += 1
        return {
            'id': count,
            'version': 1,
            'status': 'need_approval',
            'ticket': 'RUPRICING-1',
        }

    @mockserver.json_handler('/taxi-approvals/multidrafts/create/')
    def _handler_multidrafts(request):
        global count
        count += 1
        assert count == expected_count
        return {'id': 11}

    response_close_candidates = await web_app_client.get(
        '/v1/operations/close_candidates',
        params={'task_id': '61711eb7b7e4790047d4fe51'},
    )
    result_close_candidates = await response_close_candidates.json()
    state_hash = hash_strategy(result_close_candidates['state_hash'])
    close_rules = rules_strategy(result_close_candidates['rules'])
    params = {'task_id': '61711eb7b7e4790047d4fe51', 'state_hash': state_hash}
    if close_rules:
        params['close_rule_ids'] = ','.join(close_rules)
    response = await web_app_client.get(
        '/v2/operations/create_draft/',
        params=params,
        headers={'X-Yandex-Login': 'test_robot'},
    )
    results = await response.json()
    assert count == expected_count
    assert response.status == expected_status
    assert results == expected_result
