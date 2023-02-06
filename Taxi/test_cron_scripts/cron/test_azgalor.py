import os
import requests
import requests_mock
import json

from cron_scripts import azgalor
from infranaim import config

from infranaim.conftest import *
from bson import json_util


TEST_URL = 'http://test.com'
ZENDESK_ROUTE_GET_TICKET_FIELDS = '/ticket_fields'


def set_configs():
    config.ZENDESK["URL"] = TEST_URL
    config.ZENDESK["ROUTES"]['GET_TICKET_FIELDS'] = (
        ZENDESK_ROUTE_GET_TICKET_FIELDS
    )


def from_mongo_to_id_dict(mongo_cursor):
    return {
        doc['_id']: doc
        for doc in mongo_cursor
    }


@pytest.mark.parametrize(
    'ticket_fields_filename, '
    'expected_custom_field_options, '
    'expected_custom_fields',
    [
        (
            'ticket_fields.json',
            {
                '_not_active_option': {
                    'field_eng_name': 'filled_in_the_form',
                    'deactivated': True,
                    'deactivated_reason': 'This option is non-existent or is not active in zendesk'
                },
                'korksenn_randi': {
                    'field_eng_name': 'filled_in_the_form',
                    'deactivated': None
                }
            },
            {
                30063229: {
                    'deactivated': None
                },
                560063229: {
                    'deactivated': True,
                    'deactivated_reason': 'This field is non-existent or is not active in zendesk'
                },
                30063209: {
                    'deactivated': None
                }
            }
        )
    ]
)
def test_azgalor(ticket_fields_filename,
                 expected_custom_field_options,
                 expected_custom_fields,
                 requests_mock, load_json, get_mongo,
                 *args, **kwargs):
    mongo = get_mongo
    set_configs()
    requests_mock.get(
        azgalor.helper.get_zendesk_url('GET_TICKET_FIELDS'),
        json=load_json(ticket_fields_filename)
    )
    azgalor.update_fields(mongo)
    options = from_mongo_to_id_dict(mongo.custom_field_options.find())
    for option_id, exp_option_data in expected_custom_field_options.items():
        if option_id == '_not_active_option':
            assert option_id not in options, (
                'Inactive option {} not deleted'.format(option_id)
            )
        else:
            assert option_id in options, 'No expected option {}'.format(
                option_id
            )
            for option_field, exp_option_value in exp_option_data.items():
                option_value = options[option_id].get(option_field)
                assert option_value == exp_option_value, (
                    'Bad value in custom_field_options option_id={} '
                    'option_field={} value={} expected_value={}'.format(
                        option_id, option_field,
                        option_value, exp_option_value
                    )
                )
    fields = from_mongo_to_id_dict(mongo.custom_fields.find())
    for field_id, exp_field_data in expected_custom_fields.items():
        if field_id == 560063229:
            assert field_id not in fields, (
                'Inactive field {} not deleted'.format(
                    field_id
                )
            )
        else:
            assert field_id in fields, 'No expected custom field {}'.format(
                field_id
            )
            for field_field, exp_field_field_value in exp_field_data.items():
                field_field_value = fields[field_id].get(field_field)
                assert field_field_value == exp_field_field_value, (
                    'Bad value in custom_fields field_id={} '
                    'field_field={} value={} expected_value={}'.format(
                        field_id, field_field,
                        field_field_value, exp_field_field_value
                    )
                )
