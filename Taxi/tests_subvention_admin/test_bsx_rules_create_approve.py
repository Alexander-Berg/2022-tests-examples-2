async def test_bsx_rules_create_approve_proxy(
        taxi_subvention_admin, mockserver,
):
    headers = {
        'X-YaTaxi-Draft-Author': 'user0',
        'X-YaTaxi-Draft-Tickets': 'TAXITICKET-001',
        'X-YaTaxi-Draft-Approvals': 'user1,user2',
        'X-YaTaxi-Draft-Id': 'draft_id',
    }
    body = {
        'rule_spec': {
            'rule': {
                'start': '2021-11-30T00:00:00+00:00',
                'end': '2021-12-01T00:00:00+00:00',
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
            'tariff_classes': ['express'],
            'zones': ['moscow'],
            'budget': {
                'weekly': '9999',
                'daily': '9999',
                'rolling': True,
                'threshold': 100,
            },
        },
        'old_rule_ids': [],
        'created_rules': [
            {
                'id': 'e9ac60d0-3072-40e8-92e2-7dd266966edf',
                'start': '2021-11-30T00:00:00+00:00',
                'end': '2021-12-01T00:00:00+00:00',
                'zone': 'moscow',
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
    }

    @mockserver.json_handler('/billing-subventions-x/v2/rules/create/approve')
    def _mock_bsx_rules_create_approve(request):
        for key in headers:
            assert request.headers[key] == headers[key]
        assert request.json == body
        return {}

    response = await taxi_subvention_admin.post(
        '/bsx/v2/rules/create/approve', json=body, headers=headers,
    )
    assert response.status_code == 200

    assert _mock_bsx_rules_create_approve.times_called == 1
