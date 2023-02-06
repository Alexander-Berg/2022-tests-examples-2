import pytest

import tests_driver_scoring.tvm_tickets as tvm_tickets


EXPECTED_SCORING = [
    {'search': {}, 'candidates': [{'id': 'dbid0_uuid0', 'score': 600.0}]},
]


@pytest.mark.experiments3(filename='postprocessors.json')
@pytest.mark.experiments3(filename='js_bonuses.json')
async def test_request_fields_fetching(taxi_driver_scoring, load_json):
    test_field_params = [
        ('meta_info', {'routestats_id': '0xdead', 'user_id': '0xbeef'}),
        ('min_taximeter_version', '0xdead'),
        ('only_free', False),
        ('limit', 10),
        ('max_distance', 1000.0),
        ('payment_method', 'card'),
        ('payment_tech', {}),
        ('prices', [10.0]),
        ('freeze_time', 60),
        ('excluded_license_ids', []),
        ('metadata', {}),
        ('use_dynamic_limits', False),
        ('skip_blacklisted', False),
        ('no_newbies', False),
        ('lookup', {'version': 1, 'wave': 1, 'generation': 1}),
        ('sv', 1.0),
        ('svs', [1.0]),
    ]
    for test_case, (field_name, field_value) in enumerate(test_field_params):
        script = (
            f'if (order_context.search_from_request.{field_name}'
            + '!= undefined) {{ return 50; }}'
        )
        add_response = await taxi_driver_scoring.post(
            'v2/admin/scripts/add',
            headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
            json={
                'script_name': 'checker',
                'type': 'calculate',
                'content': script,
            },
        )
        assert add_response.status_code == 200

        activation_request = {
            'id': test_case + 1,
            'revision': test_case,
            'script_name': 'checker',
            'type': 'calculate',
        }
        if test_case > 0:
            activation_request['last_active_id'] = test_case

        activate_response = await taxi_driver_scoring.post(
            'v2/admin/scripts/activate',
            headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
            json=activation_request,
        )
        assert activate_response.status_code == 202

        await taxi_driver_scoring.invalidate_caches()

        request_body = load_json('request_body.json')
        request_body['requests'][0]['search'][field_name] = field_value

        response = await taxi_driver_scoring.post(
            'v2/score-candidates-bulk',
            headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
            json=request_body,
        )
        assert response.status_code == 200
        assert response.json() == {'responses': EXPECTED_SCORING}
