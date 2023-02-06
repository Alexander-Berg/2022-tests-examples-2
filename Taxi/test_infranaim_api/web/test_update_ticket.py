import collections

import freezegun
import pytest

from infranaim.models.configs import external_config
from infranaim import helper


Expected = collections.namedtuple('Expected', ['status_code', 'fields'])

OP_EQ = '$eq'
OP_NE = '$ne'
OPERATORS = (OP_EQ, OP_NE)


class OperatorError(Exception):
    pass


def check_value(value, exp_formula):
    for operator, exp_value in exp_formula.items():
        if operator not in OPERATORS:
            raise OperatorError(f'{operator} expected one of {OPERATORS}')
        if OP_EQ == operator and value != exp_value:
            return False
        if OP_NE == operator and value == exp_value:
            return False
    return True


@freezegun.freeze_time('2020-01-01T12:00:00.999')
@pytest.mark.parametrize(
    'name',
    [
        'valid_no_medium_no_source',
        'valid_medium_and_source',
        'valid_medium_and_source_only_external_id',
        'forbidden',
        'forbidden_only_external_id',
        'non_existent',
        'bool_field',
        'repeat',
        'fake_update',
        'fake_external_id_old',
        'fake_external_id_not_old',
    ]
)
def test_update(
        infranaim_client_factory, patch, personal, get_mongo, load_json,
        name
):
    external_config.INFRANAIM_PERSONAL.update({'store_mongo': 1})

    @patch('infranaim.clients.personal.PreparedRequestMain._generate_headers')
    def _tvm(*args, **kwargs):
        return {'headers': 1}

    @patch('infranaim.clients.personal.PreparedRequestSync._request')
    def _personal(*args, **kwargs):
        result = personal('valid', *args, **kwargs)
        return result

    @patch('infranaim.clients.telegram.Telegram.send_message')
    def _telegram(*args, **kwargs):
        return None

    mongo = get_mongo
    client = infranaim_client_factory(mongo)
    request = load_json('requests.json')[name]
    for request_body in request['requests']:
        res = client.post(
            request['route'],
            headers=request['headers'],
            json=request_body['json'],
        )
        exp = Expected(**request_body['expected'])
        assert res.status_code == exp.status_code

        update_docs = list(mongo.zendesk_tickets_to_update.find())
        create_docs = list(mongo.zendesk_tickets_to_create.find())
        assert not create_docs

        if name in {'fake_update', 'fake_external_id_old'}:
            assert not update_docs
            return

        if exp.status_code == 200:
            assert len(update_docs) == 1
            upd_data = update_docs[0]['upd_data']
            if name != 'repeat':
                assert len(upd_data) == 1
                ticket = upd_data[0]['data']
            else:
                ticket = upd_data[-1]['data']
            custom_fields = helper.get_ticket_value_for_fields(
                mongo, ticket, list(exp.fields.keys())
            )
            for field, exp_query in exp.fields.items():
                assert check_value(custom_fields.get(field), exp_query), (
                    f'bad value ({custom_fields.get(field)}) for field {field}, '
                    f'expected {exp_query},  custom_fields {custom_fields}'
                )
        else:
            if name != 'repeat':
                assert not update_docs
            else:
                assert len(update_docs[0]['upd_data']) == 3
