import json

import freezegun
import pytest
import requests

from infranaim.models.configs import external_config

BASE_COUNT = 5
EMPTY_EXP3_RESPONSE = {
    "items": [],
    "version": 11760
}
ROUTE_PRECHECK = '/zendesk/precheck_phone'
ROUTE_EXPERIMENTS = '/zendesk/experiments'


@freezegun.freeze_time("2020-01-15T12:00:00Z")
@pytest.mark.parametrize('route', [ROUTE_PRECHECK, ROUTE_EXPERIMENTS])
@pytest.mark.parametrize(
    'request_name, experiments_sequence, personal_response, history_count',
    [
        ('valid', 'one_experiment', 'valid', BASE_COUNT),
        ('missing_source', 'one_experiment', 'valid', BASE_COUNT - 1),
        ('no_items', 'one_experiment', 'valid', BASE_COUNT - 1),
        (
                'valid',
                'two_dependent_shuffled_experiments',
                'valid',
                BASE_COUNT + 1,
        ),
        (
                'history_check_hit',
                'two_dependent_shuffled_experiments',
                'valid',
                BASE_COUNT,
        ),
        (
                'history_check_no_hit',
                'two_dependent_shuffled_experiments',
                'valid',
                BASE_COUNT + 1,
        ),
        ('valid', 'one_non_existent_experiment', 'valid', BASE_COUNT - 1),
        ('valid', 'two_experiments_first_non_existent', 'valid', BASE_COUNT),
        ('valid', 'two_non_existent_experiments', 'valid', BASE_COUNT - 1),
        (
                'history_check_member_is_member_exists',
                'one_experiment_check_members',
                'valid',
                BASE_COUNT - 1,
        ),
        (
                'history_check_member_is_member_nonexistent',
                'one_experiment_check_members',
                'valid',
                BASE_COUNT,
        ),
        (
                'history_check_member_not_member_exists',
                'one_experiment_check_members',
                'valid',
                BASE_COUNT - 1,
        ),
        (
                'history_check_member_not_member_nonexistent',
                'one_experiment_check_members',
                'valid',
                BASE_COUNT - 1,
        ),
    ]
)
def test_experiments(
        flask_client_factory, get_mongo, load_json, personal,
        patch, find_documents_in_update_queue, request_name,
        _assertions, route, experiments_sequence, personal_response,
        history_count,
):
    @patch('infranaim.helper._find_valid_token')
    def _getenv(*args, **kwargs):
        return 'TOKEN'

    @patch('infranaim.helper._is_equal_b64')
    def _token(*args, **kwargs):
        return True

    @patch('infranaim.clients.experiments.ExperimentV2._prepare_headers')
    def _headers():
        return {'headers': 1}

    @patch('infranaim.clients.personal.PreparedRequestMain._generate_headers')
    def _tvm(*args, **kwargs):
        return {'headers': 1}

    @patch('infranaim.clients.personal.PreparedRequestSync._request')
    def _personal(*args, **kwargs):
        result = personal(personal_response, *args, **kwargs)
        return result

    @patch('infranaim.clients.telegram.Telegram.send_message')
    def _telegram(*args, **kwargs):
        return None

    @patch('infranaim.clients.experiments.ExperimentV2._find_config')
    def _config():
        return load_json('experiments_config.json')

    @patch('infranaim.utils.make_request.request')
    def _response(**kwargs):
        _data = kwargs['payload']
        consumer = _data['consumer']
        response = load_json('responses.json')[experiments_sequence].get(
            consumer, {}).get(request_name)
        if response:
            if (
                experiments_sequence == 'two_dependent_shuffled_experiments'
                and consumer == 'infranaim/cannibalization'
            ):
                park_base = ''
                status = ''
                request_fields = _data['args']
                for request_field in request_fields:
                    if request_field['name'] == 'park_base':
                        park_base = request_field['value']
                    elif request_field['name'] == 'status':
                        status = request_field['value']
                if status == 'не_лид':
                    response = EMPTY_EXP3_RESPONSE
                elif park_base:
                    response['items'].append(
                        load_json('exp_cannibalization.json')
                    )
        else:
            response = EMPTY_EXP3_RESPONSE
        result = requests.Response()
        result._content = bytes(json.dumps(response), encoding='utf8')
        result.status_code = 200
        return result

    external_config.HIRING_SCOUTS_EXPERIMENTS_CONFIG = load_json(
        'experiments_config.json')
    external_config.HIRING_SCOUTS_EXPERIMENTS_SEQUENCE = load_json(
        'experiments_sequence.json')[experiments_sequence]

    mongo = get_mongo
    configs = {'USE_EXPERIMENTS3': True}
    flask_client = flask_client_factory(mongo, configs=configs)

    data = load_json('requests.json')[request_name]
    data['s_code'] = 'TOKEN'
    expected = load_json('expected.json')[experiments_sequence][request_name]
    res = flask_client.post(route, json=data)
    _assertions(res, mongo, expected, data, history_count)


@pytest.fixture
def _assertions(load_json):
    def _wrapper(
            res,
            mongo,
            expected,
            data,
            history_count,
    ):
        assert res.status_code == 200
        docs = list(mongo.zendesk_tickets_to_update.find())
        assert docs
        assert len(docs) == 1
        tickets = docs[0]['upd_data']
        assert len(tickets) == 1

        ticket = tickets[0]['data']

        assert ticket['id'] == data['ticket_id']

        ticket_custom_fields = {
            item['id']: item
            for item in ticket['custom_fields']
        }
        for field in expected['contains']['custom_fields']:
            ticket_field = ticket_custom_fields.get(field['id'])
            assert ticket_field, f'Not able to find field {field["id"]}'
            assert field['value'] == ticket_field['value']

        for field in expected['does_not_contain']['custom_fields']:
            ticket_field = ticket_custom_fields.get(field['id'])
            assert not ticket_field or ticket_field['value'] != field['value']

        for tag in expected['contains']['tags']:
            assert tag in ticket['additional_tags']

        for tag in expected['does_not_contain']['tags']:
            assert tag not in ticket.get('additional_tags', [])

        assert mongo.experiments.count_documents({}) == history_count

    return _wrapper
