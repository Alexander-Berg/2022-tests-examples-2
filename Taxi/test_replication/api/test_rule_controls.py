import datetime
import operator

import pytest

from replication.generated.service.swagger.models import api as api_model

_FROZEN_RULE_SCOPES_LIST = [
    'test_api_basestamp',
    'test_initialize_columns',
    'test_sharded_rule',
    'test_pg',
]

REPLICATION_MONRUN_THRESHOLDS = {
    'replication': {
        '__default__': {
            'relative_delay': {'critical': 0},
            'sync_delay': {'warning': 600, 'critical': 900},
            'disable_rule_sync_delay': {'warning': 700, 'critical': 1000},
        },
    },
    'verification': {
        '__default__': {
            'current_fails_num': {'critical': 1, 'warning': 1},
            'sync_delay': {'critical': 3600},
        },
    },
}


@pytest.mark.config(
    REPLICATION_WEB_CTL={'admin': {'raw_layer_check': {'enabled': True}}},
    REPLICATION_MONRUN_THRESHOLDS=REPLICATION_MONRUN_THRESHOLDS,
)
@pytest.mark.now(datetime.datetime(2019, 3, 16, 3).isoformat())
async def test_rules_control(
        monkeypatch, replication_client, replication_app, load_json,
):
    expected_rule_control = load_json('expected_rule_control.json')
    original_state_items = (
        replication_app.rule_keeper.states_wrapper.state_items
    )

    def frozen_state_items(*args, **kwargs):
        for rule_scope in _FROZEN_RULE_SCOPES_LIST:
            yield from original_state_items(rule_scope=rule_scope)

    monkeypatch.setattr(
        replication_app.rule_keeper.states_wrapper,
        'state_items',
        frozen_state_items,
    )
    response = await replication_client.get('/control/rule/view_all/')
    assert response.status == 200
    response_data = await response.json()
    assert response_data == expected_rule_control


@pytest.mark.config(
    REPLICATION_WEB_CTL={
        'admin': {
            'raw_layer_check': {'enabled': True},
            'scope_kibana_link_settings': {
                'query_template': 'https://kibana:/{replication_rule_scope}',
                'scope_link_enabled': True,
            },
        },
    },
    REPLICATION_MONRUN_THRESHOLDS=REPLICATION_MONRUN_THRESHOLDS,
    REPLICATION_CRON_MAIN_SETUP={
        'use_chains': ['test/test_struct_sharded', 'test/test_sharded_pg'],
    },
)
@pytest.mark.now(datetime.datetime(2019, 3, 16, 3).isoformat())
async def test_rule_view_all_scopes(
        monkeypatch,
        replication_client,
        replication_app,
        load_json,
        load_yaml,
        root_dir,
):
    frozen_rule_scopes_list = [
        'test_sharded_rule',
        'test_pg',
        'test_raw_history',
    ]

    def _frozen_all_scopes_list():
        return frozen_rule_scopes_list

    monkeypatch.setattr(
        replication_app.rule_keeper.rules_storage,
        'get_all_scopes_names',
        _frozen_all_scopes_list,
    )
    expected_all_rule_scopes = {
        'diagnostics': [
            {
                'alert_status': 'ok',
                'description': '',
                'link': 'arcadia',
                'name': 'arcadia',
            },
            {
                'alert_status': 'ok',
                'description': '',
                'link': 'https://unittests/drafts',
                'name': 'drafts',
            },
            {
                'alert_status': 'ok',
                'description': '',
                'link': 'https://grafana/replication_web',
                'name': 'web: grafana',
            },
            {
                'alert_status': 'ok',
                'description': '',
                'link': 'https://kibana/replication_web',
                'name': 'web: kibana',
            },
        ],
        'extra_filters_names': set(),
        'rules': [],
    }
    expected_by_scopes = {}
    for rule_scope in sorted(frozen_rule_scopes_list):
        scope_info = load_json(f'expected_scope-{rule_scope}.json')
        expected_by_scopes[rule_scope] = scope_info
        expected_all_rule_scopes['rules'].extend(scope_info.get('rules', []))
        expected_all_rule_scopes['extra_filters_names'].update(
            scope_info.get('extra_filters_names', []),
        )
    expected_all_rule_scopes['rules'] = sorted(
        expected_all_rule_scopes['rules'], key=operator.itemgetter('name'),
    )
    expected_all_rule_scopes['extra_filters_names'] = sorted(
        expected_all_rule_scopes['extra_filters_names'],
    )
    response = await replication_client.post('/admin/v1/rules/view/')
    assert response.status == 200
    all_response_data = await response.json()

    for rule_scope in frozen_rule_scopes_list:
        expected = expected_by_scopes[rule_scope]
        response_with_body = await replication_client.post(
            '/admin/v1/rules/view/', json={'rule_scope': rule_scope},
        )
        assert response_with_body.status == 200
        response_data = await response_with_body.json()
        # validation
        api_model.AdminRulesViewResponse.deserialize(response_data)
        assert response_data == expected, rule_scope

    # validation
    api_model.AdminRulesViewResponse.deserialize(all_response_data)
    assert all_response_data == expected_all_rule_scopes
