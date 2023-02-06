import json

import pytest


class DriverWorkRulesContext:
    def __init__(self):
        self.list_times_called = 0
        self.comp_list_times_called = 0
        self.status_code = 200
        self.work_rules_response = None  # default response
        self.from_master = None

    def inc_list_times_called(self):
        self.list_times_called += 1

    def inc_comp_list_times_called(self):
        self.comp_list_times_called += 1

    def set_work_rules_response(self, response):
        self.work_rules_response = response

    def set_from_master(self, value):
        self.from_master = value


@pytest.fixture
def driver_work_rules(mockserver, load_json):

    context = DriverWorkRulesContext()

    @mockserver.json_handler('/driver_work_rules/v1/work-rules')
    def mock_work_rules(request):
        context.inc_list_times_called()

        park_id = request.args['park_id']
        work_rule_id = request.args['id']
        from_master = request.args.get('from_master')
        assert from_master == 'true' or from_master == 'false', from_master

        context.set_from_master(from_master == 'true')

        park_work_rules = (
            context.work_rules_response['work_rules']
            if context.work_rules_response
            else load_json('work_rules_list.json')[park_id]
        )
        work_rule = [x for x in park_work_rules if x['id'] == work_rule_id]

        assert len(work_rule) <= 1, f'duplicate work rule id `{work_rule_id}`'
        if not work_rule:
            return mockserver.make_response(
                json.dumps({'code': 'not_found', 'message': 'Not Found'}),
                status=404 if context.from_master else 400,
            )

        return work_rule[0]

    @mockserver.json_handler('/driver_work_rules/v1/work-rules/list')
    def mock_work_rules_list(request):
        request_data = json.loads(request.get_data())

        if context.work_rules_response:
            rule_id = request_data['query']['park']['work_rule']['ids'][0]
            for rule in context.work_rules_response['work_rules']:
                if rule['id'] == rule_id:
                    return {'work_rules': [rule]}
            return {'work_rules': []}

        park_id_to_work_rules = load_json('work_rules_list.json')

        park_id = request_data['query']['park']['id']
        work_rules = park_id_to_work_rules[park_id]
        filter_ids = request_data['query']['park']['work_rule']['ids']

        response = [
            work_rule
            for work_rule in work_rules
            if work_rule['id'] in filter_ids
        ]

        context.inc_list_times_called()
        return {'work_rules': response}

    @mockserver.json_handler(
        '/driver_work_rules/v1/dispatcher/work-rules/compatible/list',
    )
    def mock_dispatcher_work_rules_compatible_list(request):
        park_id_to_work_rules = load_json('work_rules_list.json')

        request_data = json.loads(request.get_data())
        park_id = request_data['query']['park']['id']
        work_rules = park_id_to_work_rules[park_id]
        compatible_with_id = request_data['query']['park']['work_rule'][
            'compatible_with_id'
        ]

        work_rule_for_compatibility = [
            work_rule
            for work_rule in work_rules
            if work_rule['id'] == compatible_with_id
        ].pop()

        response = [
            work_rule
            for work_rule in work_rules
            if work_rule['type'] == work_rule_for_compatibility['type']
        ]

        context.inc_comp_list_times_called()
        return {'work_rules': response}

    @mockserver.json_handler(
        '/driver_work_rules/v1/work-rules/compatible/list',
    )
    def mock_work_rules_compatible_list_new(request):
        park_id_to_work_rules = load_json('work_rules_list.json')

        park_id = request.args['park_id']
        compatible_with_id = request.args['compatible_with_id']
        client_type = request.args['client_type']

        work_rules = park_id_to_work_rules[park_id]

        work_rule_for_compatibility = None
        if compatible_with_id:
            work_rule_for_compatibility = [
                work_rule
                for work_rule in work_rules
                if work_rule['id'] == compatible_with_id
            ].pop()

        if client_type == 'external':
            if not work_rule_for_compatibility:
                context.inc_comp_list_times_called()
                return {
                    'work_rules': [
                        work_rule
                        for work_rule in work_rules
                        if work_rule['type'] == 'park'
                    ],
                }
            else:
                context.inc_comp_list_times_called()
                return {
                    'work_rules': [
                        work_rule
                        for work_rule in work_rules
                        if work_rule['type']
                        == work_rule_for_compatibility['type']
                    ],
                }

        context.inc_comp_list_times_called()
        return {'work_rules': work_rules}

    return context
