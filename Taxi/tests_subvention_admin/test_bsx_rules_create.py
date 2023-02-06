import copy

import pytest


@pytest.mark.parametrize(
    'zone,subgmv,expected_approvers',
    [
        (
            # zone
            'br_moscow',
            # subgmv
            '0',
            # expected_approvers
            {'disable_extra_approve_group': True},
        ),
        (
            # zone
            'br_moscow',
            # subgmv
            '2',
            # expected_approvers
            {
                'disable_extra_approve_group': False,
                'extra_approve_group_key': 'big_lord',
            },
        ),
        (
            # zone
            'krasnogorsk',
            # subgmv
            '2',
            # expected_approvers
            {
                'disable_extra_approve_group': False,
                'extra_approve_group_key': 'big_lord',
            },
        ),
        (
            # zone
            'krasnogorsk',
            # subgmv
            '1',
            # expected_approvers
            {'disable_extra_approve_group': True},
        ),
    ],
)
@pytest.mark.geo_nodes(
    [
        {
            'name': 'br_root',
            'name_en': 'Basic Hierarchy',
            'name_ru': 'Базовая иерархия',
            'node_type': 'root',
        },
        {
            'name': 'br_russia',
            'name_en': 'Russia',
            'name_ru': 'Россия',
            'node_type': 'agglomeration',
            'parent_name': 'br_root',
        },
        {
            'name': 'br_moscow',
            'name_en': 'Moscow',
            'name_ru': 'Москва',
            'node_type': 'agglomeration',
            'parent_name': 'br_russia',
            'tariff_zones': ['moscow', 'khimki', 'krasnogorsk'],
        },
    ],
)
@pytest.mark.config(SUBVENTION_ADMIN_ADD_APPROVERS_FIELD_TO_BSX_DRAFTS=True)
@pytest.mark.config(
    SUBVENTION_ADMIN_DRAFT_APPROVERS={
        '__default__': {},
        'br_moscow': {
            '__default__': [
                {'subgmv_threshold': 2, 'extra_approve_group_key': 'big_lord'},
            ],
        },
        'mosow': {
            '__default__': [
                {'subgmv_threshold': 1, 'extra_approve_group_key': 'big_lord'},
            ],
        },
    },
)
async def test_bsx_rules_create_add_approvers(
        taxi_subvention_admin, mockserver, zone, subgmv, expected_approvers,
):
    headers = {'X-YaTaxi-Draft-Author': 'superuser'}
    request = {
        'rule_spec': {
            'zones': [zone],
            'rule': {
                'rule_type': 'single_ride',
                'rates': [
                    {
                        'bonus_amount': '11',
                        'week_day': 'mon',
                        'start': '00:00',
                    },
                ],
                'start': '2021-11-30T00:00:00+0000',
                'end': '2021-12-01T00:00:00+0000',
                'branding_type': 'without_sticker',
                'activity_points': 30,
            },
            'budget': {
                'rolling': True,
                'weekly': '9999',
                'daily': '9999',
                'subgmv': subgmv,
            },
            'tariff_classes': ['express'],
        },
        'old_rule_ids': [],
    }

    bsx_response = {}

    @mockserver.json_handler('/billing-subventions-x/v2/rules/create')
    def _mock_bsx_rules_create(request):
        nonlocal bsx_response
        bsx_response = {
            'change_doc_id': 'moscow:e2f7db13-4bdf-47af-9ca5-4f50af2b022d',
            'data': {
                'rule_spec': request.json['rule_spec'],
                'old_rule_ids': request.json['old_rule_ids'],
                'created_rules': [
                    {
                        'id': 'e9ac60d0-3072-40e8-92e2-7dd266966edf',
                        'start': '2021-11-30T00:00:00+00:00',
                        'end': '2021-12-01T00:00:00+00:00',
                        'zone': zone,
                        'tariff_class': 'express',
                        'branding_type': 'without_sticker',
                        'activity_points': 30,
                        'rates': [
                            {
                                'week_day': 'mon',
                                'start': '00:00',
                                'bonus_amount': '11',
                            },
                        ],
                        'rule_type': 'single_ride',
                    },
                ],
                'doc_id': 'e2f7db13-4bdf-47af-9ca5-4f50af2b022d',
            },
        }
        return bsx_response

    response = await taxi_subvention_admin.post(
        '/bsx/v2/rules/create', json=request, headers=headers,
    )
    assert response.status_code == 200

    expected_response = copy.deepcopy(bsx_response)
    expected_response['data']['_approvers'] = expected_approvers
    assert response.json() == expected_response


async def test_bsx_rules_create_400(taxi_subvention_admin, mockserver):
    @mockserver.json_handler('/billing-subventions-x/v2/rules/create')
    def _mock_bsx_rules_create(request):
        return mockserver.make_response('{"some_body": "here"}', 400)

    response = await taxi_subvention_admin.post(
        '/bsx/v2/rules/create', json={}, headers={},
    )
    assert response.status_code == 400
    assert response.json() == {'some_body': 'here'}
